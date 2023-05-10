# Copyright (C) 2020 - Hendrix Costa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api, fields


class Intent(models.Model):
    _name = "intent"
    _description = "Intent for model classification"
    _order = "indice"

    _sql_constraints = [
        ('label_uniq', 'unique (label)', 'Label number already exists!'),
    ]

    name = fields.Char(
        string="Nome",
    )

    label = fields.Char(
        string="Label para treinamento",
        size=2,
    )

    indice = fields.Integer(
        string="Indice da intent",
        compute="compute_indice",
        store=True,
    )

    description = fields.Char(
        string="Descrição da Intenção",
        help="Descrição da intenção para ajudar o usuário na "
             "identificação de cada intent",
    )

    intent_phrase_ids = fields.One2many(
        comodel_name="intent.phrase",
        string="Phrases",
        inverse_name="intent_id",
        help="Frases para treinar o modelo a reconhecer a intenção e buscar "
             "a resposta no contexto fornecido"
    )

    context = fields.Text(
        string="Contexto de resposta",
        help="Texto que contenha as resposta das perguntas de treinamento",
    )

    @api.model
    def create(self, values):
        values['label'] = str(len(self.search([]))) if self.search([]) else 0
        intent_id = super(Intent, self).create(values)
        return intent_id

    @api.depends("label")
    def compute_indice(self):
        for record in self:
            if record.label:
                record.indice = int(record.label) + 1
            else:
                record.indice = 0
