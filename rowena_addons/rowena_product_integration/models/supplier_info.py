from odoo import api, fields, models


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    is_api_create = fields.Boolean('Criado pela Api')
