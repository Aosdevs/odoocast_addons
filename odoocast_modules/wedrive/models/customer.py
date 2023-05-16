from odoo import models, fields

class Customer(models.Model):
    _name = 'wedrive.customer'
   # _inherit = 
    _description = 'Cliente'

    # Adicione campos adicionais específicos para o prontuário de veículos
    Customer_id = fields.Char(string='Cliente')
    vehicle_ids = fields.One2many('wedrive.vehicle', 'customer_id', string='Veíulos')
    # Outros campos relevantes para o cliente

