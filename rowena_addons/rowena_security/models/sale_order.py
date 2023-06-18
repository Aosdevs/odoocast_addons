from odoo import models
from odoo.tools import float_is_zero
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        if not self.env.user.has_group(
            "rowena_security.group_confirm_quotations"
        ):
            raise UserError(
                "Você não possui permissão pra confirmar cotações!"
            )
        for prod in self.mapped("order_line.product_id"):
            if float_is_zero(
                prod.standard_price,
                precision_rounding=self.currency_id.rounding,
            ):
                self.env["bus.bus"].sendone(
                    (
                        self._cr.dbname,
                        "res.partner",
                        self.env.user.partner_id.id,
                    ),
                    {
                        "type": "simple_notification",
                        "title": "Custo de Produto",
                        "message": "O produto '{}' possui custo R$ 0,00".format(
                            prod.name
                        ),
                        'sticky': True,
                    },
                )
        return super(SaleOrder, self).action_confirm()
