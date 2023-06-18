from odoo import http
from odoo.http import request


class DefaultCode(http.Controller):
    @http.route(
        "/rowena_product_info", type="json", auth="public", website=True
    )
    def get_default_code(self, **kw):
        prod = (
            request.env["product.product"].sudo().browse(kw.get("product_id"))
        )
        return {
            "ok": len(prod) > 0,
            "default_code": prod.default_code,
            "website_default_quantity": prod.website_default_quantity,
        }
