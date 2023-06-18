from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    min_margin = fields.Float(
        string="Minimum Margin", help="Minimum profit margin allowed"
    )
