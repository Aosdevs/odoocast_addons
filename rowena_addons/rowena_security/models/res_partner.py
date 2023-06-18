from odoo import fields, models, api
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_code = fields.Char('Código do parceiro', size=6)

    _sql_constraints = [
        ('res_partner_partner_code_uniq', 'unique (partner_code)',
         'Este código já está em uso por outro parceiro!')
    ]

    @api.model
    def create(self, vals):
        if vals.get(
            "company_type"
        ) == "company" and not self.env.user.has_group(
            "rowena_security.group_create_company_contact"
        ):
            raise UserError(
                "Você não tem permissão para criar contatos do tipo 'Empresa'"
            )
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        if vals.get(
            "company_type"
        ) == "company" and not self.env.user.has_group(
            "rowena_security.group_create_company_contact"
        ):
            raise UserError(
                "Você não tem permissão para criar contatos do tipo 'Empresa'"
            )
        return super(ResPartner, self).write(vals)
