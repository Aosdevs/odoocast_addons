from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    salesperson_profit_margin_id = fields.Many2one(
        "salesperson.profit.margin", string="Salesperson Profit Margin"
    )
