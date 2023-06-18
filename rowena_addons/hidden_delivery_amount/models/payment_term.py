from odoo import models, fields


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    price_increase = fields.Float(
        string="Incremento no Preço (%)",
        help="Percentual a ser adicionado no preço unitário dos produtos",
    )
