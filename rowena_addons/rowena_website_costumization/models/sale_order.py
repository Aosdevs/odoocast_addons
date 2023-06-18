from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_total_without_hidden_delivery = fields.Float(
        string="(=) Subtotal",
    )

    hidden_delivery_amount = fields.Float(
        string="(+) Frete (Oculto)",
        digits="Product Price"
    )

    amount_untaxed = fields.Monetary(
        string='(=) Subtotal',
        store=True, readonly=True,
        compute='_amount_all',
        tracking=5
    )

    l10n_br_delivery_amount = fields.Monetary(
        string="(+) Frete",
        compute="_compute_l10n_br_delivery_amount",
    )