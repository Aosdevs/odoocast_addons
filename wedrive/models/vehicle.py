from odoo import models, fields

class Vehicle(models.Model):
    _name = 'wedrive.vehicle'
    _description = 'Veículo'

    name = fields.Char(string='Nome do Veículo')
    plate = fields.Char(string='Placa do Veículo')
    customer_id = fields.Many2one('wedrive.customer', string='Customer')
    type = fields.Selection([
        ('car', 'Carro'),
        ('motorcycle', 'Motocicleta'),
        ('truck', 'Caminhão'),
        ('other', 'Outro'),
    ], string='Tipo')
    year_model= fields.Char(string='Ano/Modelo')
    version = fields.Char(string='Versão')
    km = fields.Char(string='Kilometragem')
    chassi = fields.Char(string='Chassi')
    color = fields.Char(string='Cor')
    # Adicione aqui outros campos relevantes para o cadastro de veículos

    
