from odoo import models, api


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    @api.depends(
        "commission_id",
        "object_id.price_subtotal",
        "object_id.product_id",
        "object_id.product_uom_qty",
    )
    def _compute_amount(self):
        for line in self:
            order_line = line.object_id
            subtotal = (
                order_line.base_price_unit
                or order_line.price_unit_without_delivery
                or order_line.price_unit
            ) * order_line.product_uom_qty
            line.amount = line._get_commission_amount(
                line.commission_id,
                subtotal,
                order_line.product_id,
                order_line.product_uom_qty,
            )
