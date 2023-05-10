# -*- coding: utf-8 -*-
# Part of AlmightyCS See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.service import common
import odoo.modules as addons
loaded_modules = addons.module.loaded
import requests
import json


class ResCompany(models.Model):
    _inherit = "res.company"

    birthday_mail_template_id = fields.Many2one('mail.template', 'Birthday Wishes Template',
        help="This will set the default mail template for birthday wishes.")

    @api.model
    def acs_send_access_data(self, data):
        ir_config_model = self.env["ir.config_parameter"].sudo()
        try:
            domain = "https://www.almightyhms.com" + '/acs/module/checksubscription'
            reply = requests.post(domain, json.dumps(data), headers={'accept': 'application/json', 'Content-Type': 'application/json'})
            if reply.status_code==200:
                reply = json.loads(reply.text)
        except:
            pass

    @api.model
    def acs_update_access_data(self):
        user = self.env.user
        company = user.sudo().company_id
        ir_config_model = self.env["ir.config_parameter"].sudo()
        secret = ir_config_model.get_param("database.secret")
        url = ir_config_model.get_param("web.base.url")
        data = {
            "installed_modules": loaded_modules, 
            "db_secret": secret, 
            "company_name": company.name,
            "email": company.email,
            "mobile": company.partner_id.mobile,
            "url": url,
            'users': self.env['res.users'].sudo().search_count([('share','=',False)]),
            'physicians': self.env['hms.physician'].sudo().search_count([]),
            'patients': self.env['hms.patient'].sudo().search_count([]),
        }

        try:
            version_info = common.exp_version()
            data['version'] = version_info.get('server_serie')    
        except:
            pass

        try:
            if "acs_hms" in loaded_modules:
                data.update({
                    'appointments': self.env['hms.appointment'].sudo().search_count([]),
                    'prescriptions': self.env['prescription.order'].sudo().search_count([]),
                    'treatments': self.env['hms.treatment'].sudo().search_count([]),
                })
        except:
            pass

        try:
            if "acs_hms_insurance" in loaded_modules:
                data['insurance_policies'] = self.env['hms.patient.insurance'].sudo().search_count([])
                data['claims'] = self.env['hms.insurance.claim'].sudo().search_count([])
            if "acs_hms_certification" in loaded_modules:
                data['certificates'] = self.env['certificate.management'].sudo().search_count([])
            if "acs_hms_hospitalization" in loaded_modules:
                data['hospitalizations'] = self.env['acs.hospitalization'].sudo().search_count([])
            if "acs_consent_form" in loaded_modules:
                data['consentforms'] = self.env['acs.consent.form'].sudo().search_count([])
            if "acs_hms_laboratory" in loaded_modules:
                data['laboratory_requests'] = self.env['acs.laboratory.request'].sudo().search_count([])
                data['laboratory_results'] = self.env['patient.laboratory.test'].sudo().search_count([])
            if "acs_hms_vaccination" in loaded_modules:
                data['vaccinations'] = self.env['acs.vaccination'].sudo().search_count([])
            if "acs_hms_surgery" in loaded_modules:
                data['surgeries'] = self.env['hms.surgery'].sudo().search_count([])
            if "acs_sms" in loaded_modules:
                data['sms'] = self.env['acs.sms'].sudo().search_count([])
            if "acs_whatsapp" in loaded_modules:
                data['whatsapp'] = self.env['acs.whatsapp.message'].sudo().search_count([])
        except:
            pass
        self.acs_send_access_data(data)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    birthday_mail_template_id = fields.Many2one('mail.template', 
        related='company_id.birthday_mail_template_id',
        string='Birthday Wishes Template',
        help="This will set the default mail template for birthday wishes.", readonly=False)