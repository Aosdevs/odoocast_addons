import logging
import json
import requests
import re
from datetime import timedelta
from ..erede import Transaction, Environment, Store, eRede, RedeError
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons.payment_asaas.helpers import REDE_URL, REDE_SANDBOX_URL


_logger = logging.getLogger(__name__)


class RedePayment(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(
        selection_add=[("rede", "Rede")], ondelete={"rede": "set default"}
    )
    rede_access_token = fields.Char(string="Access Token")
    rede_type = fields.Selection(
        [
            ("CREDIT_CARD", "Cartão de Crédito")
        ]
    )

    def asaas_request(self, method, endpoint, vals={}):
        store = Store("PV", "TOKEN", Environment.sandbox())

        transaction = Transaction(12345, "Reference")
        transaction.credit_card("5448280000000007", "123", "12", "2020", "Fulano de Tal")
        transaction.set_additional(3456, 12)

        try:
            transaction = eRede(store).create(transaction)

            if transaction.returnCode == "00":
                return transaction
        except RedeError as e:
            print("Opz[{}]: {}".format(e.code, e))

    def rede_s2s_form_process(self, data):
        partner_id = self.env["res.partner"].browse(
            int(data.get("partner_id"))
        )

        commercial_partner_id = partner_id.commercial_partner_id

        expiry_date = data.get("asaas-card-expiry").split("/")
        vals = {
            "customer": commercial_partner_id.name,
            "creditCardHolderName": data.get("asaas-card-holder"),
            "creditCardNumber": data.get("asaas-card-number").replace(
                " ", ""
            ),
            "creditCardExpiryMonth": len(expiry_date) > 1
                                     and expiry_date[0]
                                     or "",
            "creditCardExpiryYear": len(expiry_date) > 1
                                    and expiry_date[1]
                                    or "",
            "creditCardCcv": data.get("asaas-card-cvc"),
        }

        response = self.asaas_request("POST", "card", vals)

        if response.status_code == 200:
            res = response.json()

            pm_id = self.env["payment.token"].search(
                [("acquirer_ref", "=", res.get("creditCardToken"))],
                limit=1,
            )

            if not pm_id:
                pm_values = {
                    "acquirer_id": int(data.get("acquirer_id")),
                    "partner_id": int(data.get("partner_id")),
                    "acquirer_ref": res.get("creditCardToken"),
                    "name": res.get("creditCardBrand")
                            + " "
                            + res.get("creditCardNumber"),
                    "verified": True,
                }
                pm_id = self.env["payment.token"].sudo().create(pm_values)

            return pm_id
        else:
            try:
                res = response.json()
                raise UserError(
                    "\r\n".join(
                        error.get("description", "")
                        for error in res.get("errors", [])
                    )
                )
            except json.decoder.JSONDecodeError:
                raise UserError("Erro tentar adicionar forma de pagamento.")

    def asaas_form_generate_values(self, values):
        partner_id = values.get("billing_partner")
        commercial_partner_id = partner_id.commercial_partner_id
        base_url = (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )
        payment_transaction_id = self.env["payment.transaction"].search(
            [("reference", "=", values["reference"])]
        )
        order = payment_transaction_id.sale_order_ids
        if self.asaas_type == "BOLETO" and order.asaas_installment > 1:
            if values.get("amount") < 1000:
                raise UserError(
                    "O parcelamento no boleto é permitido apenas para compras maiores que R$ 1000,00"
                )
            order.action_confirm()
            order.message_post(
                body="O cliente está solicitando um parcelamento via boleto em {} vezes para esta compra!".format(
                    order.asaas_installment
                )
            )
            return {"checkout_url": order.access_url}
        vals = {
            "customer": commercial_partner_id.get_asaas_customer_id(),
            "billingType": self.asaas_type,
            "dueDate": (fields.Date.today() + timedelta(days=3)).strftime(
                "%Y-%m-%d"
            ),
            "value": values.get("amount"),
            "description": "Pagamento {}".format(values.get("reference")),
            "externalReference": values.get("reference"),
            "postalService": False,
        }

        vals.update(
            payment_transaction_id.sale_order_ids.get_asaas_split_values(self)
        )

        response = self.asaas_request("POST", "/api/v3/payments", vals)
        if response.status_code != 200:
            raise UserError("Erro durante a solicitação!")
        data = response.json()

        vals = {
            "acquirer_reference": data.get("id"),
        }
        if self.asaas_type == "BOLETO":
            vals.update({"asaas_boleto_url": data.get("bankSlipUrl")})
        payment_transaction_id.write(vals)

        return {"checkout_url": base_url + "/shop/payment/asaas"}


class TransactionAsaas(models.Model):
    _inherit = "payment.transaction"

    asaas_boleto_url = fields.Char(string="ASAAS Boleto URL")
    asaas_can_be_refunded = fields.Boolean(
        compute="_compute_asaas_can_be_refunded"
    )

    def _compute_asaas_can_be_refunded(self):
        for item in self:
            item.asaas_can_be_refunded = (
                    item.state == "done"
                    and item.acquirer_id.provider == "asaas"
                    and item.acquirer_id.asaas_type == "CREDIT_CARD"
            )

    def _set_transaction_refunded(self):
        allowed_states = ("done", "error")
        target_state = "cancel"
        (
            tx_to_process,
            tx_already_processed,
            tx_wrong_state,
        ) = self._filter_transaction_state(allowed_states, target_state)
        for tx in tx_already_processed:
            _logger.info(
                "Trying to write the same state twice on tx (ref: %s, state: %s"
                % (tx.reference, tx.state)
            )
        for tx in tx_wrong_state:
            _logger.warning(
                "Processed tx with abnormal state (ref: %s, target state: %s, previous state %s, expected previous states: %s)"
                % (tx.reference, target_state, tx.state, allowed_states)
            )
        # Cancel the existing payments.
        tx_to_process.mapped("payment_id").cancel()
        tx_to_process.write(
            {
                "state": target_state,
                "date": fields.Datetime.now(),
                "state_message": "Esta compra foi estornada no cartão de crédito do cliente!",
            }
        )
        tx_to_process._log_payment_transaction_received()

    def asaas_s2s_do_transaction(self):
        vals = {
            "customer": self.partner_id.get_asaas_customer_id(),
            "billingType": "CREDIT_CARD",
            "dueDate": fields.Date.today().strftime("%Y-%m-%d"),
            "value": self.amount,
            "description": "Pagamento {}".format(self.reference),
            "externalReference": re.sub("[^0-9]", "", self.reference),
            "creditCardToken": self.payment_token_id.acquirer_ref,
        }

        if 1 < self.sale_order_ids.asaas_installment < 7:
            vals.update(
                {
                    "totalValue": vals.pop("value"),
                    "installmentCount": self.sale_order_ids.asaas_installment,
                }
            )

        vals.update(self.sale_order_ids.get_asaas_split_values(self))

        response = self.acquirer_id.asaas_request(
            "POST", "/api/v3/payments", vals
        )

        if response.status_code == 200:
            self.write({"acquirer_reference": response.json().get("id")})
            self.form_feedback(response.json(), "asaas")
        else:
            try:
                res = response.json()
                self._set_transaction_error(
                    "\r\n".join(
                        error.get("description", "")
                        for error in res.get("errors", [])
                    )
                )
            except json.decoder.JSONDecodeError:
                self._set_transaction_error("Erro ao processar transação!")

    @api.model
    def _asaas_form_get_tx_from_data(self, data):
        acquirer_reference = data.get("id")
        tx = self.search([("acquirer_reference", "=", acquirer_reference)])
        return tx[0]

    def _asaas_form_validate(self, data):
        status = data.get("status")

        if status in ("RECEIVED", "CONFIRMED"):
            self._set_transaction_done()
            return True
        elif status in ("PENDING", "AWAITING_RISK_ANALYSIS"):
            self._set_transaction_pending()
            return True
        elif status == "REFUNDED":
            self._set_transaction_refunded()
        else:
            self._set_transaction_cancel()
            return False

    def check_asaas_payment_state(self):
        for item in self:
            if item.acquirer_id.provider != "asaas":
                continue
            response = item.acquirer_id.asaas_request(
                "GET",
                "/api/v3/payments/{}".format(item.acquirer_reference),
            )
            if response.status_code == 200:
                item.form_feedback(response.json(), "asaas")
            else:
                raise UserError(
                    "Erro ao consultar pagamento {}:\r\n".format(item.name)
                    + "\r\n".join(
                        error.get("description", "")
                        for error in response.json().get("errors", [])
                    ),
                )

    def refund_asaas_payment(self):
        if not self.asaas_can_be_refunded:
            raise UserError("Não é possível estornar esta compra!")

        response = self.acquirer_id.asaas_request(
            "POST",
            "/api/v3/payments/{}/refund".format(self.acquirer_reference),
        )

        if response.status_code == 200:
            self.form_feedback(response.json(), "asaas")
        else:
            # Can't use '_set_transaction_error' cause it
            # doesn't allow done transactions
            self.write(
                {
                    "state": "error",
                    "date": fields.Datetime.now(),
                    "state_message": "\r\n".join(
                        error.get("description", "")
                        for error in response.json().get("errors", [])
                    ),
                }
            )
            self._log_payment_transaction_received()
