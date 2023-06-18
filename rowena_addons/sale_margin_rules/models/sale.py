from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("price_unit")
    def price_unit_onchange(self):
        salesman_margin = self.salesman_id.salesperson_profit_margin_id.margin
        product_min_margin = self.product_id.min_margin
        current_margin = self.margin

        # The salesperson margin has priority
        conditions = (
            salesman_margin < current_margin
            and product_min_margin > 0
            and current_margin < product_min_margin
        )

        if conditions:
            raise UserError(
                _(
                    "The product margin needs to be at least %s"
                    % salesman_margin
                )
            )
