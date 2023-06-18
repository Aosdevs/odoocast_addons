# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Odoo Integration',
    'version': '14.0.2.2.1',
    'category': 'Tools',
    'author': 'InTechual Solutions',
    'license': 'OPL-1',
    'summary': 'WhatsApp Integration with Odoo',
    'description': """
This module can be used to send messages to WhatsApp
----------------------------------------------------
Send Messages via WhatsApp
Core module for WhatsApp Odoo Integration
""",
    'depends': ['base', 'base_setup'],
    'data': [
        'data/whatsapp_cron.xml',
        'security/ir.model.access.csv',
        'wizard/send_wp_msg_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/mobile_widget.xml',
    ],
    'external_dependencies': {'python': ['phonenumbers', 'selenium']},
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'sequence': 1,
    'auto_install': False,
    'currency': 'EUR',
    'price': 25,

}
