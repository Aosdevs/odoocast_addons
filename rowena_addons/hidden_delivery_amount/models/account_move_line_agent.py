from odoo import models, api


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    @api.depends(
        "object_id.price_subtotal",
        "object_id.product_id.commission_free",
        "commission_id",
    )
    def _compute_amount(self):
        for line in self:
            inv_line = line.object_id
            subtotal = (
                inv_line.price_unit_without_delivery
                or inv_line.price_unit
            ) * inv_line.quantity
            line.amount = line._get_commission_amount(
                line.commission_id,
                subtotal,
                inv_line.product_id,
                inv_line.quantity,
            )
            # Refunds commissions are negative
            if (
                line.invoice_id.move_type
                and "refund" in line.invoice_id.move_type
            ):
                line.amount = -line.amount
