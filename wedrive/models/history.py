from odoo import models, fields

class History(models.Model):
    _name = 'wedrive.history'
    _description = 'Histórico do Veículo'

    vehicle_id = fields.Many2one('wedrive.vehicle', string='Veículo', required=True)
    professional_id = fields.Many2one('wedrive.professional', string='Profissional', required=True)
    service_id = fields.Many2one('wedrive.service', string='Serviço', required=True)
    description = fields.Text(string='Detalhamento')
    date = fields.Date(string='Data', required=True)
    # Outros campos relevantes para o histórico do veículo

