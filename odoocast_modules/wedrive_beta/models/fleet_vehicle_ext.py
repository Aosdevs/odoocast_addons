import requests
from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    license_plate = fields.Char(string='License Plate')
    marca = fields.Char(string='Marca')
    modelo = fields.Char(string='Modelo')
    ano = fields.Char(string='Ano')
    cor = fields.Char(string='Cor')
    chassi = fields.Char(string='Chassi')
    municipio = fields.Char(string='Município')
    uf = fields.Char(string='UF')
    segmento = fields.Char(string='Segmento')
    anoModelo = fields.Char(string='Ano do Modelo')
    subsegmento = fields.Char(string='Subsegmento')
    combustivel = fields.Char(string='Combustível')
    cilindradas = fields.Char(string='Cilindradas')

    @api.model
    def action_get_plate_info(self, plate):
        url = "https://api.placafipe.xyz/getplaca"
        token = "1CD78B0C54849E565D2E42FFC2AE899ADD8A401200FA43683D0C42ED76BBAD5F"

        payload = {
            "placa": plate,
            "token": token,
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Verifica se houve erro na requisição
            data = response.json()
            if data.get("codigo") == 1:
                return {
                    'marca': data['informacoes_veiculo']['marca'],
                    'modelo': data['informacoes_veiculo']['modelo'],
                    'ano': data['informacoes_veiculo']['ano'],
                    'cor': data['informacoes_veiculo']['cor'],
                    'chassi': data['informacoes_veiculo']['chassi'],
                    'municipio': data['informacoes_veiculo']['municipio'],
                    'uf': data['informacoes_veiculo']['uf'],
                    'segmento': data['informacoes_veiculo']['segmento'],
                    'anoModelo': data['informacoes_veiculo']['anoModelo'],
                    'subsegmento': data['informacoes_veiculo']['subsegmento'],
                    'combustivel': data['informacoes_veiculo']['combustivel'],
                    'cilindradas': data['informacoes_veiculo']['cilindradas'],
                }
        except requests.exceptions.RequestException as e:
            # Trata erros de conexão, timeouts, etc.
            print(f"Erro na requisição HTTP: {e}")
        except ValueError as e:
            # Trata erros ao decodificar a resposta JSON
            print(f"Erro ao decodificar a resposta JSON: {e}")
        return {}

    @api.model
    def create(self, vals):
        if 'license_plate' in vals:
            plate = vals['license_plate']
            plate_data = self.action_get_plate_info(plate)
            vals.update(plate_data)
        return super(FleetVehicle, self).create(vals)
