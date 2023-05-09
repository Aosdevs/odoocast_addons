# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    has_chatbot_ai = fields.Boolean(
        string="AI Chatbot",
    )

    chatbot_service_url = fields.Char(
        string="Serviço do Chatbot",
    )

    chatbot_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Chatbot User",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        params = self.env['ir.config_parameter'].sudo()

        has_chatbot_ai = params.get_param('has_chatbot_ai', default=False)
        chatbot_service_url = params.get_param('chatbot_service_url', default="")
        chatbot_user_id = params.get_param('chatbot_user_id', default=False)

        res.update(
            has_chatbot_ai=has_chatbot_ai,
            chatbot_user_id=int(chatbot_user_id),
            chatbot_service_url=chatbot_service_url,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("has_chatbot_ai", self.has_chatbot_ai)
        self.env['ir.config_parameter'].sudo().set_param("chatbot_service_url", self.chatbot_service_url)
        self.env['ir.config_parameter'].sudo().set_param("chatbot_user_id", self.chatbot_user_id.id)
