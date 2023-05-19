{
    'name': 'wedrive',
    'version': '14.0.0.0.0.1',
    'category': 'Services',
    'license': 'LGPL-3',
    'summary': 'Módulo para gerenciar prontuário de veículos',
    'depends': [
        'base',
    ],
    'author': 'Alexandre Santos',
    'website': 'www.wedrive.com.br',

    'data': [
        'views/vehicle_ocr_api_view.xml',
        'static/src/js/web_camera.js',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

    'images': [
        'static/description/icon.png',
        'static/description/icon_menu.png',
    ],
}
