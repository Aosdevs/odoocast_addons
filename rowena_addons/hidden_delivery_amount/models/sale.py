from odoo import models, fields, api
from odoo.tools import float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
                - (line.hidden_delivery_amount * line.product_uom_qty)
                for line in item.order_line
            )

    @api.onchange(
        "payment_term_id",
        "hidden_delivery_amount",
        "order_line",
        "order_line.base_price_unit",
    )
    def hidden_delivery_amount_partition(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Price"
        )
        for order in self:
            initial_amount = balance = order.hidden_delivery_amount * (
                1 + (order.payment_term_id.price_increase / 100)
            )
            order_line_ids = order.order_line.filtered(
                lambda x: not x.is_delivery
            )
            for delivery_line in order.order_line.filtered(
                lambda x: x.is_delivery
            ):
                delivery_line.with_context(skip_onchange=True).update(
                    {"price_unit": delivery_line.price_unit_without_delivery}
                )
            current_total = sum(
                (
                    line.base_price_unit
                    or line.price_unit_without_delivery
                    or line.price_unit
                )
                * line.product_uom_qty
                * (1 + (order.payment_term_id.price_increase / 100))
                for line in order_line_ids
            )

            if not current_total:
                continue
            for line in order_line_ids:
                base_price = price = (
                    line.base_price_unit
                    or line.price_unit_without_delivery
                    or line.price_unit
                )
                if order.payment_term_id.price_increase:
                    price = price * (
                        1 + (order.payment_term_id.price_increase / 100)
                    )
                if line == order_line_ids[-1]:
                    line_amount = balance
                else:
                    line_amount = float_round(
                        initial_amount
                        * base_price
                        * line.product_uom_qty
                        / current_total,
                        precision_digits=precision,
                    )
                hidden_delivery_amount = line_amount / (
                    line.product_uom_qty or 1
                )
                line.with_context(skip_onchange=True).update(
                    {
                        "hidden_delivery_amount": hidden_delivery_amount,
                        "base_price_unit": base_price,
                        "price_unit_without_delivery": price,
                        "price_unit": price + hidden_delivery_amount,
                    }
                )
                balance -= line_amount

    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        vals["hidden_delivery_amount"] = self.hidden_delivery_amount
        return vals

    def update_prices(self):
        res = super(SaleOrder, self).update_prices()
        for line in self._get_update_prices_lines():
            line.update({
                "base_price_unit": line.price_unit,
                "price_unit_without_delivery": line.price_unit
            })
        self.hidden_delivery_amount_partition()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    base_price_unit = fields.Float(
        string="Base Price Unit",
        digits="Product Price",
    )

    price_unit_without_delivery = fields.Float(
        string="Initial Price Unit",
        digits="Product Price",
    )

    hidden_delivery_amount = fields.Float(
        string="Frete Oculto", digits="Product Price"
    )

    subtotal_without_delivery = fields.Float(
        string="Subtotal Without Delivery",
        digits="Product Price",
        compute="_compute_subtotal_without_delivery",
    )

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(
            **optional_values
        )
        res.update(
            {
                "base_price_unit": self.base_price_unit,
                "price_unit_without_delivery": self.price_unit_without_delivery,
                "hidden_delivery_amount": self.hidden_delivery_amount,
            }
        )
        return res

    def _compute_subtotal_without_delivery(self):
        for item in self:
            item.subtotal_without_delivery = (
                item.price_unit_without_delivery * item.product_uom_qty
            )

    @api.onchange("price_unit_without_delivery")
    def _set_base_price_unit(self):
        if self.env.context.get("skip_onchange"):
            return
        for item in self:
            item.base_price_unit = item.price_unit_without_delivery

    @api.onchange("price_unit", "product_uom_qty", "product_id")
    def _set_price_unit_without_delivery(self):
        if self.env.context.get("skip_onchange"):
            return
        for item in self:
            item.price_unit_without_delivery = item.price_unit

    @api.model_create_multi
    def create(self, vals):
        for values in vals:
            if values.get("price_unit") and not values.get(
                "price_unit_without_delivery"
            ):
                values.update(
                    {
                        "price_unit_without_delivery": values.get(
                            "price_unit"
                        ),
                        "base_price_unit": values.get("price_unit"),
                    }
                )
        return super(SaleOrderLine, self).create(vals)
