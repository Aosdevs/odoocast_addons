from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    office_role = fields.Char(string="Cargo")
    department = fields.Char(string="Departamento")
