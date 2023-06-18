from odoo import api, fields, models
from datetime import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    data_do_pagamento = fields.Datetime(string='Data do Pagamento')


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    data_do_pagamento = fields.Datetime(string='Data do Pagamento')

    def action_create_payments(self):
        payments = self._create_payments()
        self.data_do_pagamento = fields.Datetime.now()
        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action
