# Copyright (C) 2020 - Hendrix Costa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{  # pylint: disable=C8101,C8103
    'name': 'Chatbot',
    'description': """Chatbot with BERT""",
    'category': 'Localization',
    'license': 'AGPL-3',
    'author': 'Hendrix Costa',
    'website': 'http://www.sunnit.com.br',
    'version': '13.0.0.0.0',
    'depends': ["mail", "queue_job", "im_livechat", "website_livechat", "web_tree_no_open"],
    'data': [
        'views/base_view.xml',
        'views/intent_phrase_view.xml',
        'views/mail_shortcode_view.xml',
        'views/intent_view.xml',
        'views/pretrained_model_view.xml',
        'views/res_config_settings_view.xml',
        'security/ir.model.access.csv',
        # 'data/intent_data.xml',
        # 'data/phrase_data.xml',
        # 'data/pretrained_model_data.xml',
    ],
    'installable': True,
    'auto_install': True,
}
