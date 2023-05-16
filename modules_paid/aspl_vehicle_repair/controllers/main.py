from odoo import http
from odoo.http import request


class CustomerRegistration(http.Controller):

    @http.route('/customer/register', auth='public', website=True)
    def customer_register(self, **post):
        return http.request.render('aspl_vehicle_repair.customer_registration_template')

    @http.route('/customer/create', auth='public', type='http', website=True, method=['POST'])
    def customer_create(self, **post):
        partner = request.env['res.partner'].sudo().create({
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('Telefone')
            # Adicione outros campos necessários aqui
        })
        return http.request.redirect('/customer/register')
