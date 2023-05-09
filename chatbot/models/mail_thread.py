# Copyright (C) 2020 - Hendrix Costa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields
from odoo.addons.queue_job.job import Job
from odoo import exceptions, tools


import requests
import json
import re

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def get_greeting(self):
        # obtém a hora atual para bom dia, boa tarde ou boa noite
        import datetime
        hora_atual = datetime.datetime.now().hour - 3

        if hora_atual < 12:
            return 'Bom dia'
        elif 12 <= hora_atual < 18:
            return 'Boa tarde'
        else:
            return 'Boa noite'

    def make_bot_message(self, message, author):
        """
        Create a bot message
        """

        # Hard Capitalize
        message = message.replace(message[0], message[0].capitalize(), 1) \
            if message[0].isalpha() \
            else message.replace(message[1], message[1].capitalize(), 1)

        # Substituição de tokens
        tokens = re.findall('\"[\w ]*\"', message)

        for token in tokens:

            code = token.replace("\"", "")

            substitution = self.env['mail.shortcode'].sudo().search([
                ("source", "ilike", code)], limit=1).substitution

            if substitution:
                if "|" in substitution:
                    code = substitution.replace("|", "")
                    substitution = str(eval(code))
                message = message.replace(token, substitution)

        kwargs = {
            'partner_ids': [],
            'channel_ids': [],
            'body': message,
            'attachment_ids': [],
            'canned_response_ids': [],
            'subtype': 'mail.mt_comment',
            'author_id': author.id,
        }

        self.sudo().message_post(message_type='comment', **kwargs)

    #@Job
    def send_bot_message(self, question, author):
        """
        """
        url = self.env['ir.config_parameter'].sudo().\
                  get_param('chatbot_service_url') or "http://localhost:7788/"

        intents = self.env['intent'].search([])

        intents_data = \
            [{"label": x.label, "context": x.context} for x in intents]

        json_data = json.dumps(
            {"question": question, "intents": intents_data})

        result = requests.post(url, json=json_data)

        resposta = result.json().get('answer')

        if isinstance(resposta, str):
            self.make_bot_message(resposta, author)

        if isinstance(resposta, list):
            for res in resposta:
                self.make_bot_message(res, author)

        return True

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):

        message = super(MailThread, self).message_post(**kwargs)

        modulo_habilitado = \
            self.env['ir.config_parameter'].sudo().\
                get_param('has_chatbot_ai') or False
        if not modulo_habilitado:
            return message

        chatbot_user_id = self.env['ir.config_parameter'].sudo().\
            get_param('chatbot_user_id') or False
        if not chatbot_user_id:
            return message

        chatbot_patner_id = \
            self.env['res.users'].browse(int(chatbot_user_id)).partner_id or False
        if not chatbot_patner_id:
            return message

        if self._name not in ['crm.lead', 'account.move', 'solplace.projeto'] and chatbot_patner_id in self.channel_partner_ids and \
                kwargs.get("author_id") != chatbot_patner_id.id:
            self.with_delay().send_bot_message(
                tools.html2plaintext(message.body), chatbot_patner_id)

        return message
