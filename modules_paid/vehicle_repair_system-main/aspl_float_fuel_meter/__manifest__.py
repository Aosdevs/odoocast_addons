# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Float Fuel meter',
    'version': '1.0',
    'category': 'All',
    'summary': "Float Fuel meter helps you to add Fuel meter widget in float field.",
    'description': "Float Fuel meter helps you to add Fuel meter widget in float field.",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    "depends": ['web', 'base'],
    'currency': 'EUR',
    'price': 0.0,
    "data": [
        'views/templates.xml',
    ],
    'qweb': [
        "static/src/xml/widget.xml"
    ],
    'images': ['static/description/fuel_meter.png'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
