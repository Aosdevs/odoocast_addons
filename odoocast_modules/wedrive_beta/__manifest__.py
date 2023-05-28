{
    'name': 'wedrive_beta',
    'version': '14.0.0.0.0.1',
    'license': 'LGPL-3',
    'summary': 'Módulo para gerenciar prontuário de veículos,baseado no fleet',
    'category': 'Fleet',
    
    'depends': ['fleet',
    'base'],
    'data': [
        'views/fleet_vehicle_ext_views.xml',
        # 'views/fleet_translation.xml',
    ],
    

    'author': 'Alexandre Santos',
    'website': 'www.wedrive.com.br',


    'installable': True,
    'application': True,
    'auto_install': False,

    'images': [
        'static/description/icon.png',
        'static/description/icon_menu.png',
    ],
}
