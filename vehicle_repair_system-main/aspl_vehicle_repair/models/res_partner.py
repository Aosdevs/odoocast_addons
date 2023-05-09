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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vehicle_line_ids = fields.One2many('vehicle.vehicle', 'customer_id', string='Vehicle Line')
    vehicle_work_order_count = fields.Integer(string='Work Order Count', compute='_compute_vehicle_counts')
    vehicle_job_card_count = fields.Integer(string='Job Card Count', compute='_compute_vehicle_counts')
    vehicle_appointment_count = fields.Integer(string='Vehicle Appointment Count',
                                               compute='_compute_vehicle_counts')

    def _compute_vehicle_counts(self):
        self.vehicle_work_order_count = self.env['vehicle.work.order'].search_count([('customer_id', '=', self.id)])
        self.vehicle_job_card_count = self.env['vehicle.job.card'].search_count([('customer_id', '=', self.id)])
        self.vehicle_appointment_count = self.env['vehicle.appointment'].search_count([('customer_id', '=', self.id)])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
