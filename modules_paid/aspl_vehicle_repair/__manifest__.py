# -*- coding: utf-8 -*-
#################################################################################
# Author : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
###########################################################################

{
    'name': "Vehicle Repair System",
    'sequence': 1,
    'summary': "Repairing Vehicles",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'version': '1.0',
    'website': 'https://acespritech.com/',
    'description':
        """
Vehicle Repairing System
========================

We Give Best Vehicle Services.
______________________________
This Vehicle repair service is all about the time and quality. if customer got any problem related to vehicle,we manage that problem and gives best service.
    
    """,
    'category': '',
    'depends': ['base', 'hr', 'contacts', 'hr_skills', 'account', 'aspl_company_branch', 'aspl_float_fuel_meter',
                'aspl_float_speedometer'],
    'data': [
        'security/vehicle_repair_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'data/email_template.xml',
        'wizard/add_product_wizard.xml',
        'wizard/product_lines_wizard.xml',
        'views/vehicle_appointment.xml',
        'views/vehicle_vehicle.xml',
        'views/vehicle_insurance.xml',
        'views/vehicle_service_package.xml',
        'views/vehicle_model.xml',
        'views/vehicle_manufacture.xml',
        'views/vehicle_job_card.xml',
        'views/vehicle_workorder.xml',
        'views/vehicle_drive_point.xml',
        'views/vehicle_labor.xml',
        'views/vehicle_type.xml',
        'views/vehicle_engine.xml',
        'views/customer_service_package.xml',
        'views/res_partner.xml',
        'views/account_move_views.xml',
        'views/promotion_view.xml',
        'views/vehicle_res_config_settings.xml',
        'views/sale_view.xml',
        'views/stock.xml',
        'views/templates.xml',
        'wizard/return_product_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
