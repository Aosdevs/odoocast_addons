import re
import json
import requests

from odoo import models, fields
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    asaas_customer_id = fields.Char(string="Assas Customer ID")
    asaas_wallet_id = fields.Char(string="Asaas Wallet ID")

    def _get_asaas_partner_vals(self):
        mobile = (self.mobile or "").strip().replace("+55", "")
        return {
            "name": self.name,
            "email": self.email,
            "phone": re.sub("[^0-9]", "", self.phone or ""),
            "mobilePhone": re.sub("[^0-9]", "", mobile),
            "cpfCnpj": re.sub("[^0-9]", "", self.l10n_br_cnpj_cpf or ""),
            "postalCode": self.zip,
            "addressNumber": self.l10n_br_number,
            "complement": self.street2,
        }

    def asaas_request(self, method, endpoint, values={}):
        self.ensure_one()
        acquirer_id = self.env["payment.acquirer"].search(
            [("provider", "=", "asaas")], limit=1
        )
        response = acquirer_id.asaas_request(method, endpoint, values)
        _logger.info(str(response.status_code))
        if response.status_code != 200:
            try:
                res = response.json()
                raise UserError(
                    "\r\n".join(
                        error.get("description", "")
                        for error in res.get("errors", [])
                    )
                )
            except json.decoder.JSONDecodeError:
                raise UserError("Erro tentar cadastrar o cliente.")
        return response.json()

    def request_asaas_wallet(self):
        cnpj = re.sub("[^0-9]", "", self.l10n_br_cnpj_cpf or "")
        if cnpj:
            data = self.asaas_request(
                "GET", "/api/v3/accounts?cpfCnpj={}".format(cnpj)
            )
            if data.get("totalCount", 0) > 0:
                return data.get("data")[0].get("walletId")

    def create_asaas_wallet(self):
        wallet = self.request_asaas_wallet()
        if wallet:
            self.asaas_wallet_id = wallet
        else:
            if not (self.name and self.l10n_br_cnpj_cpf and self.email):
                message = (
                    "Os campos Nome, CNPJ/CPF e e-mail são obrigatórios!"
                )
                if self._context.get("raise_error"):
                    raise UserError(message)
                else:
                    order_id = self._context.get("order_id")
                    if order_id:
                        order = self.env["sale.order"].sudo().browse(order_id)
                        order.message_post(
                            body="Erro ao tentar criar Wallet na Asaas para o comissionado: {}<br />".format(
                                self.name
                            )
                            + message
                        )
                return ''
            vals = self._get_asaas_partner_vals()
            data = self.asaas_request("POST", "/api/v3/accounts", vals)
            self.asaas_wallet_id = data.get("walletId")
        return self.asaas_wallet_id

    def get_wallet_id(self):
        return self.asaas_wallet_id or self.create_asaas_wallet()

    def request_asaas_customer_id(self):
        cnpj = re.sub("[^0-9]", "", self.l10n_br_cnpj_cpf or "")
        data = self.asaas_request(
            "GET", "/api/v3/customers?cpfCnpj={}".format(cnpj)
        )
        if data.get("totalCount", 0) > 0:
            return data.get("data")[0].get("id")

    def create_asaas_customer(self):
        customer_id = self.request_asaas_customer_id()
        if customer_id:
            self.asaas_customer_id = customer_id
        else:
            if not (self.name and self.l10n_br_cnpj_cpf):
                raise UserError("Os campos Nome e CNPJ/CPF são obrigatórios!")
            vals = self._get_asaas_partner_vals()
            data = self.asaas_request("POST", "/api/v3/customers", vals)
            self.asaas_customer_id = data.get("id")
        return self.asaas_customer_id

    def get_asaas_customer_id(self):
        return self.asaas_customer_id or self.create_asaas_customer()
