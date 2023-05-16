{
    'name': 'wedrive',
    'version': '14.0.0.0.0.1',
    'category': 'Services',
    'license': 'LGPL-3',
    'summary': 'Módulo para gerenciar prontuário de veículos',
    'depends': [
        'base', 'fleet',
        'contacts',
        'product',
    ],
    'author': 'Alexandre Santos',
    'website': 'www.wedrive.com.br',

    'data': [
        'views/vehicle_view.xml',
        'views/customer_view.xml',
        'views/professional_view.xml',
        'views/service_view.xml',
        'views/history_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

    'images': [
        'static/description/icon.png',
        'static/description/icon_menu.png',
    ],
}
