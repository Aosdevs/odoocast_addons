import requests

from odoo import http, fields
from odoo.http import request
from odoo.addons.payment_asaas.helpers import ASAAS_URL, ASAAS_SANDBOX_URL
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError

from odoo.addons.website_sale.controllers.main import WebsiteSale

odoo_request = request


class AsaasController(WebsiteSale):
    def _get_pix_info(self, tx):
        headers = {
            "Content-Type": "application/json",
            "access_token": tx.acquirer_id.asaas_access_token,
        }
        url_asaas = (
            ASAAS_URL
            if tx.acquirer_id.state == "enabled"
            else ASAAS_SANDBOX_URL
        )
        url = url_asaas + "/api/v3/payments/{}/pixQrCode".format(
            tx.acquirer_reference
        )
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "pix": True,
                "expirationDate": fields.Date.today().strftime("%d/%m/%Y") + " 23h59",
                "encodedImage": data.get("encodedImage"),
                "payload": data.get("payload"),
                "payload_display": data.get("payload")[0:15] + "...",
            }
        return {}

    def _get_boleto_info(self, tx):
        headers = {
            "Content-Type": "application/json",
            "access_token": tx.acquirer_id.asaas_access_token,
        }
        url_asaas = (
            ASAAS_URL
            if tx.acquirer_id.state == "enabled"
            else ASAAS_SANDBOX_URL
        )
        url = url_asaas + "/api/v3/payments/{}/identificationField".format(
            tx.acquirer_reference
        )
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "boleto_url": tx.asaas_boleto_url,
                "identificationField": data.get("identificationField"),
            }
        return {}

    @http.route(
        "/shop/payment/asaas",
        type="http",
        auth="public",
        methods=["GET", "POST"],
        website=True,
    )
    def asaas_transaction_info(self, **args):
        order = odoo_request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if any(item.state == "pending" for item in order.transaction_ids):
            return odoo_request.redirect("/shop/confirmation")

        tx = order.transaction_ids.filtered(lambda x: x.state == "draft")

        tx = tx and tx[0]

        if not tx or tx.acquirer_id.provider != "asaas":
            return odoo_request.redirect("/shop/payment")

        vals = {
            "website_sale_order": order,
        }

        if tx.acquirer_id.asaas_type == "UNDEFINED":
            vals.update(self._get_pix_info(tx))
        elif tx.acquirer_id.asaas_type == "BOLETO":
            vals.update(self._get_boleto_info(tx))

        return odoo_request.render(
            "payment_asaas.asaas_payment_info_page", vals
        )

    @http.route(
        "/shop/confirmation/asaas",
        type="http",
        auth="public",
        methods=["GET", "POST"],
        website=True,
    )
    def shop_confirmation_asaas(self):
        order = odoo_request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        tx = order.transaction_ids.filtered(lambda x: x.state == "draft")

        tx = tx and tx[0]

        if not tx or tx.acquirer_id.provider != "asaas":
            return odoo_request.redirect("/shop/payment")

        tx._set_transaction_pending()
        return odoo_request.redirect("/shop/confirmation")

    @http.route(
        "/payment/asaas/new", type="json", auth="public", website=True
    )
    def create_new_payment(self, **post):
        if request.env.user._is_public() and not post.get("partner_id"):
            raise ValidationError(
                "É preciso um parceiro para criar uma cobrança"
            )
        acquirer = (
            request.env["payment.acquirer"]
            .sudo()
            .browse(int(post.get("acquirer_id")))
        )
        if acquirer.provider != "asaas":
            raise ValidationError(
                "O provedor do modo de pagamento deve ser ASAAS"
            )
        token = acquirer.s2s_process(post)
        return {"result": True, "3d_secure": False, "id": token.id}

    @http.route(
        "/asaas/payment/update",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def asaas_payment_update(self, **args):
        token = request.httprequest.headers.get("asaas-access-token")
        odoo_token = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("asaas.webhook.token")
        )

        if odoo_token and odoo_token != token:
            return {"ok'": False, "error": "Invalid Token"}

        event = request.jsonrequest.get("event")
        if event in (
            "PAYMENT_RECEIVED",
            "PAYMENT_REFUNDED",
            "PAYMENT_CONFIRMED",
        ):
            try:
                vals = request.jsonrequest.get("payment")
                tx_res = (
                    request.env["payment.transaction"]
                    .sudo()
                    .search([("acquirer_reference", "=", vals.get("id"))])
                )
                tx_res.form_feedback(vals, "asaas")
                return {"ok": True}
            except Exception as e:
                return {"ok'": False, "error": str(e)}

    @http.route(
        ["/shop/asaas_installment"],
        type="json",
        auth="public",
        website=True,
        sitemap=False,
        methods=["POST"],
    )
    def asaas_installment(self, **post):
        max_parcels = int((
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("payment_asaas.asaas_installment_max", default=6)
        ))
        try:
            message = ""
            installment = int(post.get("installment_number"))
            if installment <= max_parcels:
                order = request.website.sale_get_order()
                order.sudo().write({"asaas_installment": installment})
            else:
                message = "O parcelamento máximo é em {} vezes!".format(
                        max_parcels
                    )
        except ValueError:
            message = "Erro ao aplicar parcelamento, favor tentar novamente"

        if message:
            return {
                "ok": False,
                "message": message
            }

        return {"ok": True, "current_parcels": installment}

    @http.route(
        ["/shop/asaas_installment_info"],
        type="json",
        auth="public",
        website=True,
        sitemap=False,
        methods=["GET", "POST"],
    )
    def asaas_installment_info(self, **vals):
        parcels = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("payment_asaas.asaas_installment_max", default=6)
        )
        order = request.website.sale_get_order()
        return {
            "max_parcels": parcels,
            "amount": order.amount_total,
            "current_parcels": order.asaas_installment,
        }
