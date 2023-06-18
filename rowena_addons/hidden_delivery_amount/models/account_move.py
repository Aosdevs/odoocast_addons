from odoo import models, fields, api
from odoo.tools import float_round


class AccountMove(models.Model):
    _inherit = "account.move"

    hidden_delivery_amount = fields.Float(
        string="Frete Oculto", digits="Product Price"
    )

    amount_total_without_hidden_delivery = fields.Float(
        string="Total sem frete oculto",
        compute="_compute_total_without_hidden_delivery",
    )

    def _compute_total_without_hidden_delivery(self):
        for item in self:
            item.amount_total_without_hidden_delivery = sum(
                line.price_subtotal
                - (line.hidden_delivery_amount * line.quantity)
                for line in item.invoice_line_ids
            )

    @api.onchange(
        "hidden_delivery_amount",
        "invoice_line_ids",
    )
    def hidden_delivery_amount_partition(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Price"
        )
        for item in self:
            initial_amount = balance = item.hidden_delivery_amount
            invoice_line_ids = item.invoice_line_ids.filtered(
                lambda x: not x.l10n_br_is_delivery
            )
            for delivery_line in item.invoice_line_ids.filtered(
                lambda x: x.l10n_br_is_delivery
            ):
                delivery_line.with_context(
                    skip_onchange=True, check_move_validity=False
                ).update(
                    {"price_unit": delivery_line.price_unit_without_delivery}
                )
            current_total = sum(
                (line.price_unit_without_delivery or line.price_unit)
                * line.quantity
                for line in invoice_line_ids
            )
            if not current_total:
                continue
            for line in invoice_line_ids:
                price = line.price_unit_without_delivery or line.price_unit
                if line == invoice_line_ids[-1]:
                    line_amount = balance
                else:
                    line_amount = float_round(
                        initial_amount
                        * price
                        * line.quantity
                        / current_total,
                        precision_digits=precision,
                    )
                hidden_delivery_amount = line_amount / (line.quantity or 1)
                line.with_context(skip_onchange=True).update(
                    {
                        "hidden_delivery_amount": hidden_delivery_amount,
                        "price_unit_without_delivery": price,
                        "price_unit": price + hidden_delivery_amount,
                    }
                )
                balance -= line_amount
            item.with_context(
                check_move_validity=False
            )._move_autocomplete_invoice_lines_values()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    base_price_unit = fields.Float(string="Base Price Unit", store=True)

    price_unit_without_delivery = fields.Float(
        string="Initial Price Unit", digits="Product Price"
    )

    hidden_delivery_amount = fields.Float(
        string="Frete Oculto", digits="Product Price"
    )

    subtotal_without_delivery = fields.Float(
        string="Subtotal Without Delivery",
        digits="Product Price",
        compute="_compute_subtotal_without_delivery",
    )

    @api.onchange("price_subtotal")
    def _compute_subtotal_without_delivery(self):
        for item in self:
            item.subtotal_without_delivery = (
                item.price_unit_without_delivery * item.quantity
            )

    @api.onchange("price_unit", "product_id", "quantity")
    def _set_price_unit_without_delivery(self):
        if self.env.context.get("skip_onchange"):
            return
        for item in self:
            item.price_unit_without_delivery = item.price_unit
