from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    asaas_installment_max = fields.Integer(
        string="Número Máximo de Parcelas Asaas",
        default=6,
        config_parameter="payment_asaas.asaas_installment_max",
    )
