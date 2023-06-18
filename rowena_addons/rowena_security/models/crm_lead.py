from odoo import models, api
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.constrains("partner_id")
    def _crm_lead_partner_id(self):
        for item in self:
            if item.partner_id.user_id != item.user_id:
                raise ValidationError(
                    "Este parceiro não está relacionado ao vendedor desta oportunidade!"
                )
