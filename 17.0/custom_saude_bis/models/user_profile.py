from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_dependent = fields.Boolean(string="Dependente", default=False)
    dependents = fields.One2many('res.partner', 'partner_id', string="Dependentes", domain=[('is_dependent', '=', True)])
    partner_id = fields.Many2one('res.partner', string="Titular", domain=[('is_dependent', '=', False)])
    plan_type = fields.Selection([
        ('plus', 'Plus'),
        ('smart', 'Smart'),
        ('premium', 'Premium')],
        string="Tipo de Plano")
    document_number = fields.Char(string="Número do Documento")
    validity_date = fields.Date(string="Válido até")
    tipo_documento = fields.Selection([
        ('cpf', 'CPF'),
        ('rg', 'RG')],
        string="Tipo de Documento")

        
