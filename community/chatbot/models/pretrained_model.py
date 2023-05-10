# Copyright (C) 2020 - Hendrix Costa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api
from odoo.addons.queue_job.job import Job
import requests
import json


class PreTrainedModel(models.Model):
    _name = "pretrained.model"
    _description = "Pre Trained Model"

    name = fields.Char(
        string="Nome",
    )

    tipo = fields.Selection(
        string="Model",
        selection=[
            ("bert", "bert-base-cased"),
            ("roberta", "roberta-base"),
        ],
        default="bert",
    )

    state = fields.Selection(
        string="Status",
        selection=[
            ("draft", "Rascunho"),
            ("treinado", "Ativo"),
            ("em_treinamento", "Treinando Modelo"),
            ("erro", "Erro no treinamento"),
            ("offline", "Serviço indisponível"),
        ],
        default="draft",
    )

    intent_ids = fields.Many2many(
        string="Intenções",
        comodel_name="intent",
    )

    #@Job
    def post_train(self, dataset):

        url = self.env['ir.config_parameter'].sudo().\
                  get_param('chatbot_service_url') or "http://localhost:7788"

        resposta = requests.post("{}/api/train".format(url), json=json.dumps(dataset))

        return True

    def button_train(self):

        intents = []

        for intent in self.intent_ids.filtered("intent_phrase_ids"):

            phrases = []

            for intent_phrase in intent.intent_phrase_ids:

                if not intent_phrase.text:
                    continue

                # original
                phrases.append(intent_phrase.text)

                # capitalize
                phrases.append(intent_phrase.text.capitalize())

                # all capitalize
                phrases.append(" ".join([x.capitalize() for x in intent_phrase.text.split()]))

                # upper
                phrases.append(intent_phrase.text.upper())

                # lower
                phrases.append(intent_phrase.text.lower())

                # remove '?'
                text_sem_interrogacao = intent_phrase.text.replace("?", " ")
                phrases.append(text_sem_interrogacao)

                # ADD '?'
                phrases.append("{} ?".format(text_sem_interrogacao))
                phrases.append("{}?".format(text_sem_interrogacao))

                # Sem palavras pequenas
                text_with_stopword = ' '.join(
                    [x for x in intent_phrase.text.split(' ') if len(x) > 2])
                phrases.append(text_with_stopword)

            intent = {
                "code": int(intent.label),
                "context": intent.context,
                "phrases": phrases
            }

            intents.append(intent)

        self.with_delay().post_train(dataset=intents)

        self.state = 'em_treinamento'
        return True