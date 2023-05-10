from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    branch_id = fields.Many2one('company.branch', string='Branch', default=lambda self: self.env.user.branch_id)
