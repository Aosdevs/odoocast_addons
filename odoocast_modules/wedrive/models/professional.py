from odoo import models, fields

class Professional(models.Model):
    #_inherit = 'res.partner'
    _name = 'wedrive.professional'
    _description = 'Profissional'

    # Adicione campos adicionais específicos para o prontuário de veículos
    #service_ids = fields.One2many('wedrive.service', 'professional_id', string='Serviços')
    especialidade = fields.Char(string='especialidade')
    # Outros campos relevantes para o profissional
