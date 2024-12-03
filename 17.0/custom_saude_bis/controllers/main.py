from odoo import http
from odoo.http import request
import logging

# Configuração do logger para ajudar na depuração
_logger = logging.getLogger(__name__)

class DependentsController(http.Controller):

    @http.route('/criar/dependente', type='http', auth="public", website=True, csrf=False)
    def create_dependent(self, **kwargs):
        _logger.info("Recebendo dados para criar dependente: %s", kwargs)

        partner_id = kwargs.get('partner_id')
        if not partner_id:
            _logger.warning("Titular não encontrado para partner_id: %s", partner_id)
            return request.render("website.dependents", {
                'error': 'Titular não identificado. Tente novamente!'
            })

        try:
            partner = request.env['res.partner'].sudo().browse(int(partner_id))
            if not partner.exists():
                _logger.warning("Titular com partner_id %s não encontrado no banco.", partner_id)
                return request.render("website.dependents", {
                    'error': 'Titular não encontrado!'
                })
        except ValueError as e:
            _logger.error("Erro ao converter partner_id para int: %s", e)
            return request.render("website.dependents", {
                'error': 'ID do titular inválido.'
            })

        if len(partner.dependents) >= 3:
            return request.render("website.dependents", {
                'error': 'Titular já possui 3 dependentes!'
            })

        dict_dependente = {
            'name': kwargs.get('nome'),
            'email': kwargs.get('email'),
            'phone': kwargs.get('telefone'),
            'document_number': kwargs.get('documento'),
            'plan_type': kwargs.get('tipo_plano', partner.plan_type),
            'tipo_documento': kwargs.get('tipo'),
            'partner_id': partner.id,
            'is_dependent': True,
        }

        dependente = request.env['res.partner'].sudo().create(dict_dependente)
        if dependente:
            return request.render("website.dependents", {
                'success': 'Dependente criado com sucesso!'
            })
        else:
            return request.render("website.dependents", {
                'error': 'Erro ao criar dependente. Tente novamente.'
            })
