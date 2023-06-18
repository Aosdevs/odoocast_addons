# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Product Catalog Generator',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Tools',
    'description':
        """
        This Module add below functionality into odoo

        1.Product Catalog Report\n

odoo app to print Product Catalog Report in different style, print Product Catalog, product catalog with category, custom product catalog, product catalog with price, send mail for product catalog, print catalog for product, customize product catalog, multiple Product Catalog


    """,
    'summary': 'odoo app to print Product Catalog Report in different style, print Product Catalog, product catalog with category, custom product catalog, product catalog with price, send mail for product catalog, print catalog for product, customize product catalog, multiple Product Catalog',
    'depends': ['product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/catalog_sequence.xml',
        'data/catalog_template.xml',
        'views/main_menus.xml',
        'views/generated_catalog.xml',
        'wizard/generate_catalog_popup.xml',
        'report/paperformat.xml',
        'report/header_footer.xml',
        'report/style_one_template.xml',
        'report/style_one_action.xml',
        'report/style_two_template.xml',
        'report/style_two_action.xml',
        'report/style_three_template.xml',
        'report/style_three_action.xml',
        'report/style_four_template.xml',
        'report/style_four_action.xml',
        'report/style_five_template.xml',
        'report/style_five_action.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':35.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
