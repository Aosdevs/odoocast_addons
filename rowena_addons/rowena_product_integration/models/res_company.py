from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    asia_pass = fields.Char(string="Asia API Key")
    xbz_user = fields.Char(string="XBZ Usuário")
    xbz_token = fields.Char(string="XBZ Token")
