# Copyright (C) 2020 - Hendrix Costa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields
import requests
import json

class IntentPhrase(models.Model):
    _name = "intent.phrase"
    _description = "Phrase for trainning models"

    text = fields.Char(
        string="Nome",
    )

    preview_answer = fields.Char(
        string="Previsão de resposta",
    )

    intent_id = fields.Many2one(
        string="Intenções",
        comodel_name="intent",
    )

    def button_preview_answer(self):
        """
        Botão para disparar a previsão de resposta na interfave
        """

        data = {
            "context": self.intent_id.context,
            "question": self.text,
        }

        url = self.env['ir.config_parameter'].sudo().\
                  get_param('chatbot_service_url') or "http://localhost:7788"

        resposta = requests.post(
            "{}/api/qea/".format(url), json=json.dumps(data))

        self.preview_answer = resposta.text
