{
    'name': 'Saúde Bis Customizations',
    'version': '1.0',
    'summary': 'Extensões para carteirinha virtual, telemedicina e dependentes.',
    'author': 'odoocast',
    'website': 'https://odoocast.com.br',
    'depends': ['base', 'web', 'website', 'portal'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/user_profile_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # 'custom_saude_bis/static/src/css/styles.css',
            'custom_saude_bis/static/src/img/carteirinha.svg',
        ],
    },
}
