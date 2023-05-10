# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).#

from odoo import api, fields, models, tools
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = "website"

    def compute_phone(self):
        for item in self.sudo():
            if item.sudo().last_id:
                last = self.env['website_floating_wsp'].sudo().search([('id','>',item.last_id),('status','=','done')], order="id")
                if last:
                    item.sudo().phone = last[0].phone
                    item.sudo().last_id = last[0].id
                    item.sudo().popup_message = last[0].popup_message
                else:
                    last = self.env['website_floating_wsp'].sudo().search([('status','=','done')], order="id")
                    if last:
                        item.sudo().phone = last[0].phone
                        item.sudo().last_id = last[0].id
                        item.sudo().popup_message = last[0].popup_message
                    else:
                        last = self.env['website_floating_wsp'].search([('id', '>', 0)], order="id")
                        item.phone = last[0].phone
                        item.last_id = last[0].id
                        item.sudo().popup_message = last[0].popup_message
            else:
                last = self.env['website_floating_wsp'].search([('id', '>', 0)], order="id")
                item.phone = last[0].phone
                item.last_id = last[0].id
                item.sudo().popup_message = last[0].popup_message

    floating_wsp_id = fields.Many2one('website_floating_wsp', string="Floating Button Whatsapp Theme")

    #phone = fields.Char('Phone', required=True, related='floating_wsp_id.phone')
    last_id = fields.Integer('Ultimo ID Phone')
    phone = fields.Char('Phone', required=True, compute="compute_phone")
    message = fields.Char('Message', default=' ', related='floating_wsp_id.message')
    position = fields.Selection([('left', 'Left'), ('right', 'Right')], default='left', String='Selection', related='floating_wsp_id.position')
    popup_message = fields.Char('Popup Message', default=' ', related='floating_wsp_id.popup_message')
    show_popup = fields.Boolean('Show Popup', defaut=True, related='floating_wsp_id.show_popup')
    auto_open_timeout = fields.Integer('Auto Open Time Out', default=0,  related='floating_wsp_id.auto_open_timeout')
    header_title = fields.Char('Header Title', default='WhatsApp Chat', related='floating_wsp_id.header_title')
    size = fields.Char('Size', default='72px', related='floating_wsp_id.size')
