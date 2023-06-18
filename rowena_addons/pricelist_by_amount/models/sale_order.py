from odoo import models, api
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains("discount")
    def _check_max_discount(self):
        for line in self:
            max_discount = line.order_id.pricelist_id.max_discount
            if max_discount > 0 and line.discount > max_discount:
                raise ValidationError(
                    "O desconto aplicado é maior que o limite de {}% definido na lista de preços".format(
                        max_discount
                    )
                )
