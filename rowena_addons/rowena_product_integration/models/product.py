import re
import base64
import requests

from odoo import models
from odoo.exceptions import UserError
from requests import Session
from urllib.parse import urlparse


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def sync_asia_import_products(self):
        url = "https://asia.ajung.site/api/products?name=asc"
        headers = {"appKey": self.env.company.asia_pass, "accept": "application/json"}
        page = 1

        while True:
            query = {"page": page, "name": "asc"}
            response = requests.get(url, headers=headers, params=query)
            response.raise_for_status()
            try:
                response_json = response.json()
            except ValueError:
                print(response.content)
                continue

            self.create_products_asia(response_json["products"])
            self.env.cr.commit()

            page += 1
            if response_json["products"]["current_page"] == response_json["products"]["last_page"]:
                break

    def sync_xbz_products(self):
        url_base = "https://api.minhaxbz.com.br:5001"
        end_point = "/api/clientes/GetListaDeProdutos?"
        params = "cnpj={}&token={}"

        user = re.sub("[^0-9]", "", self.env.company.xbz_user)

        url = (
                url_base
                + end_point
                + params.format(user, self.env.company.xbz_token)
        )

        session = Session()
        response = session.get(url)

        if response.status_code != 200:
            raise UserError(
                "Error while trying to get data! \n Reason: " + response.reason
            )

        self.create_products_xbz(response.json())

    def create_products_asia(self, json):
        for product in json["data"]:

            product_name = product.get("name")
            if not product_name:
                continue

            for color in product["colors"]:
                product_ref = color.get("code")
                price = color.get("price", 0) or product.get("price_final")
                standard_price = float(price)
                vals = {
                    "name": product_name + " - " + color["color"]["name"],
                    "default_code": product_ref,
                    "standard_price": standard_price * 0.90,
                    "type": "product",
                    "sale_ok": False,
                    "categ_id": 101,
                    "route_ids": [(6, None, [1, 5])],
                }

                product_id = self.search([("default_code", "=", product_ref)])
                if product_id:
                    if product_id.seller_ids.filtered(lambda x: x.is_api_create):
                        product_id.seller_ids.filtered(lambda x: x.is_api_create).write(
                            {'price': standard_price * 0.90})
                    else:
                        vals.update({"seller_ids": [(0, 0, {
                            'name': 407124,
                            'product_name': product_name + " - " + color["color"]["name"],
                            'product_code': product_ref,
                            'price': standard_price * 0.90,
                            'delay': '',
                            'is_api_create': True,
                        })], })
                    product_id.write(vals)
                else:
                    vals.update({"seller_ids": [(0, 0, {
                        'name': 407124,
                        'product_name': product_name + " - " + color["color"]["name"],
                        'product_code': product_ref,
                        'price': standard_price * 0.90,
                        'delay': '',
                        'is_api_create': True,
                    })], })
                    self.create(vals)


    def create_products_xbz(self, json):
        count_commit = 0
        count_commit_2 = 0
        for product in json:
            codigo_amigavel = None
            codigo_composto = product.get("CodigoComposto")
            if codigo_composto:
                codigo_amigavel = codigo_composto.split("-")[0]

            product_ref = codigo_amigavel or product.get("referencia")
            product_name = product.get("Nome") or product.get("nome")
            if not product_name:
                continue

            standard_price = float(product.get("PrecoVenda"))

            vals = {
                "name": product_name,
                "default_code": codigo_composto,
                "standard_price": standard_price,
                "type": "product",
                "sale_ok": False,
                "categ_id": 13,
                "route_ids": [(6, None, [1, 5])],

            }
            link_imagem = product.get("ImageLink")

            def uri_validator(link_imagem):
                try:
                    result = urlparse(link_imagem)
                    return all([result.scheme, result.netloc])
                except:
                    return False

            product_id = self.search([("default_code", "=", codigo_composto)])
            if product_id:
                if product_id.seller_ids.filtered(lambda x: x.is_api_create):
                    product_id.seller_ids.filtered(lambda x: x.is_api_create).write(
                        {'price': standard_price})
                else:
                    vals.update({"seller_ids": [(0, 0, {
                        'name': 391707,
                        'product_name': product_name,
                        'product_code': codigo_composto,
                        'price': standard_price,
                        'delay': '',
                        'is_api_create': True,
                    })], })
                product_id.write(vals)
                count_commit_2 += 1
                if count_commit_2 == 50:
                    self.env.cr.commit()
                    count_commit_2 = 0
            else:
                vals.update({"seller_ids": [(0, 0, {
                    'name': 391707,
                    'product_name': product_name,
                    'product_code': codigo_composto,
                    'price': standard_price,
                    'delay': '',
                    'is_api_create': True,
                })], })
                if uri_validator(link_imagem) == True:
                    response = requests.get(link_imagem)
                    if response.status_code == 200:
                        encoded_string = base64.b64encode(response.content)
                        vals["image_1920"] = encoded_string.decode("utf-8")
                self.create(vals)

                count_commit += 1
                if count_commit == 50:
                    self.env.cr.commit()
                    count_commit = 0
