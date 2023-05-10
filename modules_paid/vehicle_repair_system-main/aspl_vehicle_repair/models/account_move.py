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

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    work_order_id = fields.Many2one('vehicle.work.order', string='Work Order')
    job_card_id = fields.Many2one('vehicle.job.card', string='Job Card Order')
    vehicle_id = fields.Many2one('vehicle.vehicle', string='Vehicle')
    customer_package_id = fields.Many2one('customer.service.package', string='Customer Package')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
