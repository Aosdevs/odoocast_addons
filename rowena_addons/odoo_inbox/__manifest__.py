# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Mailbox (Odoo Inbox)',
    'version': '14.0.1.3',
    'summary': 'This module is used to send or receive mail through the recipient, user can do the following types of message-send message, inbox message, starred or unstarred message, etc.',
    'category': 'Website/Website',
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'description':
        """
Mailbox (Odoo Inbox)
====================
        """,
    'depends': ['portal', 'mail', 'contacts'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/template.xml',
        'views/mail_message.xml',
        'views/res_users_views.xml',
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'bootstrap': True,  # load translations for login screen
    'application': True,
    'price': 250,
    'currency': 'EUR',
}
