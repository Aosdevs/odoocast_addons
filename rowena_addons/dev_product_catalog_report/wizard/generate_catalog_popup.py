# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from odoo.http import request
import base64
from datetime import datetime
from odoo.exceptions import ValidationError


class GenerateCatalogPopup(models.TransientModel):
    _name = 'generate.catalog.popup'
    _description = 'Generate Product Catalog Popup'

    @api.onchange('print_price')
    def onchange_print_price(self):
        if not self.print_price:
            self.pricelist_filter = False

    catalog_type = fields.Selection(string='Catalog Type',
                                    selection=[('product', 'Product'),
                                               ('category', 'Product Category')],
                                    default='product', required=True)
    product_ids = fields.Many2many('product.product', string='Variants')
    product_template_ids = fields.Many2many('product.template', string='Products')
    category_ids = fields.Many2many('product.category', string='Categories')
    print_image = fields.Boolean(string='Image')
    image_size= fields.Selection(string='Image Size',
                                 selection=[('small', 'Small'),
                                            ('medium', 'Medium'),
                                            ('large', 'Large')], default='small')
    print_price = fields.Boolean(string='Price')
    pricelist_filter = fields.Boolean(string='Apply Pricelist')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    style= fields.Selection(string='Style', selection=[('1', 'Style 1'),
                                                       ('2', 'Style 2'),
                                                       ('3', 'Style 3'),
                                                       ('4', 'Style 4'),
                                                       ('5', 'Style 5')], default='1', required=True)
    print_description = fields.Boolean(string='Description')
    print_product_link = fields.Boolean(string='Product Link')
    print_internal_reference = fields.Boolean(string='Internal Reference')
    break_page = fields.Integer(string='Break Page after products')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    box_per_row = fields.Selection(string='Box Per Row',
                                   selection=[('2', 'Two Boxes'),
                                              ('3', 'Three Boxes')], default='3')
    border_color = fields.Char(string='Border Color', default='#581845')
    content_color = fields.Char(string='Content Color', default='#FFC300')
    border_style = fields.Selection(string='Border Style',
                                   selection=[('solid', 'Solid'),
                                              ('dashed', 'Dashed'),
                                              ('dotted', 'Dotted')], default='solid')
    title_color = fields.Char(string='Title Color', default='#581845')
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.user.company_id)
    print_using = fields.Selection(selection=[('template', 'Products'), ('variant', 'Variants')],
                               default='template', string='Print By', required=True)

    def create_entry(self, pdf_file):
        values = {'pdf_catalog_report': pdf_file,
                  'generated_on': datetime.now(),
                  'user_id': self.env.user.id
                  }
        entry_id = self.env['generated.catalog'].create(values)
        if entry_id:
            self.env['ir.attachment'].create({'name': entry_id.name,
                                              'datas': pdf_file,
                                              'res_id': entry_id.id,
                                              'res_model': 'generated.catalog'})

    def check_product_availability(self):
        all_products = []
        for category in self.category_ids:
            product_ids = False
            if self.print_using == 'template':
                product_ids = self.env['product.template'].search([('categ_id', 'child_of', category.id)])
            if self.print_using == 'variant':
                product_ids = self.env['product.product'].search([('categ_id', 'child_of', category.id)])
            if product_ids:
                all_products = product_ids.ids
                break
        if all_products:
            pass
        else:
            raise ValidationError(_('''Products not Found'''))

    def print_product_catalog_report(self):
        if self.catalog_type == 'product':
            if self.print_using == 'template':
                if not self.product_template_ids:
                    raise ValidationError(_('''Please add some Products'''))
            if self.print_using == 'variant':
                if not self.product_ids:
                    raise ValidationError(_('''Please add some Variants'''))
        if self.catalog_type == 'category':
            if not self.category_ids:
                raise ValidationError(_('''Please add some product categories'''))
            else:
                self.check_product_availability()

        if self.style == '1':
            pdf_file = request.env.ref('dev_product_catalog_report.action_style_one_template').sudo()._render(self.ids, data=False)[0]
            pdf_catalog_report = base64.b64encode(pdf_file)
            if pdf_catalog_report:
                self.create_entry(pdf_catalog_report)
            return self.env.ref('dev_product_catalog_report.action_style_one_template').report_action(self)

        if self.style == '2':
            if not self.print_image:
                raise ValidationError(_('''Printing Image is necessary for Style 2'''))
            pdf_file = request.env.ref('dev_product_catalog_report.action_style_two_template').sudo()._render(self.ids, data=False)[0]
            pdf_catalog_report = base64.b64encode(pdf_file)
            if pdf_catalog_report:
                self.create_entry(pdf_catalog_report)
            return self.env.ref('dev_product_catalog_report.action_style_two_template').report_action(self)

        if self.style == '3':
            if not self.print_image:
                raise ValidationError(_('''Printing Image is necessary for Style 3'''))
            pdf_file = request.env.ref('dev_product_catalog_report.action_style_three_template').sudo()._render(self.ids, data=False)[0]
            pdf_catalog_report = base64.b64encode(pdf_file)
            if pdf_catalog_report:
                self.create_entry(pdf_catalog_report)
            return self.env.ref('dev_product_catalog_report.action_style_three_template').report_action(self)

        if self.style == '4':
            if not self.print_image:
                raise ValidationError(_('''Printing Image is necessary for Style 4'''))
            if not self.print_price:
                raise ValidationError(_('''Printing Price is necessary for Style 4'''))
            pdf_file = request.env.ref('dev_product_catalog_report.action_style_four_template').sudo()._render(self.ids, data=False)[0]
            pdf_catalog_report = base64.b64encode(pdf_file)
            if pdf_catalog_report:
                self.create_entry(pdf_catalog_report)
            return self.env.ref('dev_product_catalog_report.action_style_four_template').report_action(self)

        if self.style == '5':
            if not self.print_image:
                raise ValidationError(_('''Printing Image is necessary for Style 5'''))
            pdf_file = request.env.ref('dev_product_catalog_report.action_style_five_template').sudo()._render(self.ids, data=False)[0]
            pdf_catalog_report = base64.b64encode(pdf_file)
            if pdf_catalog_report:
                self.create_entry(pdf_catalog_report)
            return self.env.ref('dev_product_catalog_report.action_style_five_template').report_action(self)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
