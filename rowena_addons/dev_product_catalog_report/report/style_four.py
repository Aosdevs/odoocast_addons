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


class StyleFour(models.AbstractModel):
    _name = 'report.dev_product_catalog_report.style_four_template'

    def format_amount(self, amount, popup_id):
        amount = formatLang(popup_id.env, amount, currency_obj=popup_id.currency_id)
        return amount

    def create_product_data(self, p_id, popup_id):
        if popup_id.print_using == 'template':
            product_id = self.env['product.template'].browse(int(p_id))
        if popup_id.print_using == 'variant':
            product_id = self.env['product.product'].browse(int(p_id))
        pricelist_price = product_id.list_price
        if popup_id.pricelist_id and popup_id.pricelist_filter:
            pricelist_price = popup_id.pricelist_id.get_products_price(product_id, [1], [self.env.user.partner_id.id])
            pricelist_price = pricelist_price[product_id.id]
        values = {'product_image': product_id.image_1920 or False,
                  'default_code':  product_id.default_code or False,
                  'name': product_id.name,
                  'category': product_id.categ_id and product_id.categ_id.name or '',
                  'list_price': pricelist_price,
                  'description_sale': product_id.description_sale or False}
        return values

    def get_products(self, popup_id):
        if popup_id.catalog_type == 'product':
            if popup_id.print_using == 'template':
                chunks = [popup_id.product_template_ids.ids[i:i + 2] for i in range(0, len(popup_id.product_template_ids.ids), 2)]
            if popup_id.print_using == 'variant':
                chunks = [popup_id.product_ids.ids[i:i + 2] for i in range(0, len(popup_id.product_ids.ids), 2)]
            return chunks
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
                chunks = [all_products[i:i + 2] for i in range(0, len(all_products), 2)]
                return chunks
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