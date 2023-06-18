# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, _
from odoo.tools.misc import formatLang

class StyleFive(models.AbstractModel):
    _name = 'report.dev_product_catalog_report.style_five_template'

    def format_amount(self, amount, popup_id):
        amount = formatLang(popup_id.env, amount, currency_obj=popup_id.currency_id)
        return amount

    def create_product_data(self, product_ids, popup_id):
        all_data = []
        for product_id in product_ids:
            pricelist_price = product_id.list_price
            if popup_id.pricelist_id and popup_id.pricelist_filter:
                pricelist_price = popup_id.pricelist_id.get_products_price(product_id, [1], [self.env.user.partner_id.id])
                pricelist_price = pricelist_price[product_id.id]
            values = {'product_image': product_id.image_1920 or False,
                      'default_code':  product_id.default_code,
                      'name': product_id.name,
                      'category': product_id.categ_id and product_id.categ_id.name or '',
                      'list_price': pricelist_price,
                      'description_sale': product_id.description_sale}
            all_data.append(values)
        return all_data

    def get_products(self, popup_id):
        if popup_id.catalog_type == 'product':
            if popup_id.print_using == 'template':
                product_data = self.create_product_data(popup_id.product_template_ids, popup_id)
            if popup_id.print_using == 'variant':
                product_data = self.create_product_data(popup_id.product_ids, popup_id)
            return product_data
        else:
            all_products = []
            for category in popup_id.category_ids:
                if popup_id.print_using == 'template':
                    product_ids = self.env['product.template'].search([('categ_id', 'child_of', category.id)])
                if popup_id.print_using == 'variant':
                    product_ids = self.env['product.product'].search([('categ_id', 'child_of', category.id)])
                if product_ids:
                    all_products = all_products + product_ids.ids
            if all_products:
                all_products = list(set(all_products))
                if popup_id.print_using == 'template':
                    final_product_ids = self.env['product.template'].browse(all_products)
                if popup_id.print_using == 'variant':
                    final_product_ids = self.env['product.product'].browse(all_products)
                product_data = self.create_product_data(final_product_ids, popup_id)
                return product_data
            else:
                return False

    def _get_report_values(self, docids, data=None):
        docs = self.env['generate.catalog.popup'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'generate.catalog.popup',
            'docs': docs,
            'get_products': self.get_products,
            'create_product_data': self.create_product_data,
            'format_amount': self.format_amount
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: