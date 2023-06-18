from odoo import models, api, fields


class SalespersonProfitMargin(models.Model):
    _name = "salesperson.profit.margin"

    name = fields.Char(string="Group Name")
    margin = fields.Float(
        string="Margin", help="Margin to salesperson work with"
    )
    salesperson_ids = fields.One2many(
        "res.users",
        "salesperson_profit_margin_id",
        string="Salespersons",
        help="Salespersons included in this group.",
    )
