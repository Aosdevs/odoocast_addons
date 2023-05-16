from odoo import models, fields

class Service(models.Model):
    #_inherit = 'product.template'
    _name = 'wedrive.service'
    _description = 'Serviço'

    # Adicione campos adicionais específicos para o prontuário de veículos
    # Por exemplo, você pode adicionar um campo para a duração estimada do serviço:
    duration = fields.Float(string='Duração do serviço')

    # Outros campos relevantes para o serviço
