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

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class VehicleJobCard(models.Model):
    _name = 'vehicle.job.card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Vehicle Job Card'

    name = fields.Char(string='Number', copy=False)
    customer_id = fields.Many2one('res.partner', string='Customer')
    appointment_id = fields.Many2one('vehicle.appointment', string='Appointment')
    vehicle_id = fields.Many2one('vehicle.vehicle', string='Vehicle')
    date = fields.Datetime(string='Date', default=datetime.now())
    fuel_level = fields.Float(string='Fuel Level')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string='Responsible User')
    job_inspection_ids = fields.One2many('vehicle.job.inspection', 'job_id', string='Inspection')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id.id)
    branch_id = fields.Many2one('company.branch', string='Branch', required=True,
                                default=lambda self: self.env.user.branch_id.id)
    package_id = fields.Many2one('customer.service.package', string='Package')
    status = fields.Selection([('draft', 'Draft'),
                               ('confirm', 'Confirmed'),
                               ('cancel', 'Cancelled')],
                              default='draft',
                              copy=False,
                              string='Status',
                              track_visibility='onchange')
    note = fields.Text(string='Note')
    work_order_count = fields.Integer(string='Work Order Count', compute='_compute_work_order')
    check_pickup_drop = fields.Boolean(string='Pickup/Drop-off Charges', copy=False)
    check_bool = fields.Boolean(string='check bool', compute='_compute_check_bool', copy=False)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.job.card')
        return super(VehicleJobCard, self).create(vals)

    def _compute_check_bool(self):
        if self.env['ir.config_parameter'].sudo().get_param('aspl_vehicle_repair.check_pickup_drop'):
            self.check_bool = True
        else:
            self.check_bool = False

    @api.onchange('appointment_id')
    def _onchange_appointment(self):
        if self.appointment_id:
            self.customer_id = self.appointment_id.customer_id
            self.vehicle_id = self.appointment_id.vehicle_id
            self.branch_id = self.appointment_id.branch_id
            return {'domain': {'branch_id': [('id', '=', self.appointment_id.branch_id.id)],
                               'customer_id': [('id', '=', self.appointment_id.customer_id.id)],
                               'vehicle_id': [('id', '=', self.appointment_id.vehicle_id.id)]}}
        else:
            self.vehicle_id = False
            self.package_id = False
            return {'domain': {'customer_id': [('id', 'in', self.env['res.partner'].search([]).ids)],
                               'vehicle_id': False}}

    @api.onchange('customer_id')
    def _onchange_customer(self):
        if self.customer_id or self.appointment_id:
            self.vehicle_id = self.appointment_id.vehicle_id
            return {'domain': {'appointment_id': [('customer_id', '=', self.customer_id.id)]}}
        else:
            self.vehicle_id = False
            self.package_id = False
            return {'domain': {'appointment_id': [('id', 'in', self.env['vehicle.appointment'].search([]).ids)]}}

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        self.package_id = False

    @api.constrains('fuel_level')
    def _check_fuel_level(self):
        if self.fuel_level > 100 or self.fuel_level < 0.00:
            raise ValidationError(_("Fuel level is between 0 to 100."))

    def _compute_work_order(self):
        self.work_order_count = self.env['vehicle.work.order'].search_count([('job_card_id', '=', self.id)])

    def action_draft(self):
        self.status = 'draft'

    def action_confirm(self):
        self.status = 'confirm'

    def action_cancel(self):
        orders = self.env['vehicle.work.order'].search([('job_card_id', '=', self.id)])
        flag = 0
        if orders:
            for rec in orders:
                if rec.status != 'cancel':
                    flag = 1
                else:
                    flag = 0
        if flag == 1:
            raise ValidationError(_("Job Card Related Work Order Is Not Cancelled."))
        else:
            self.status = 'cancel'

    def create_work_order(self):
        part_lines = []
        labor_lines = []
        for rec in self.package_id.customer_parts_ids:
            part_lines.append((0, 0, {'product_id': rec.product_id.id,
                                      'quantity': rec.quantity,
                                      'price': rec.price}))
        for rec in self.package_id.customer_labor_ids:
            labor_lines.append((0, 0, {'labor_id': rec.labor_id.id,
                                       'hours': rec.hours,
                                       'rate': rec.rate}))
        work_id = self.env['vehicle.work.order'].create({'job_card_id': self.id,
                                                         'customer_id': self.customer_id.id,
                                                         'vehicle_id': self.vehicle_id.id,
                                                         'package_id': self.package_id.id,
                                                         'branch_id': self.branch_id.id,
                                                         'parts_ids': part_lines,
                                                         'labor_ids': labor_lines})
        return {'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': work_id.id,
                'res_model': 'vehicle.work.order'}

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context and self._context.get('jobcard'):
            order_ids = self.env['vehicle.work.order'].search([('job_card_id', '!=', False)])
            job_lst = []
            for each in order_ids:
                job_lst.append(each.job_card_id.id)
            recs = self.search([('id', 'not in', job_lst)])
            return recs.name_get()
        else:
            return super(VehicleJobCard, self).name_search(name=name, args=args, operator=operator, limit=limit)


class VehicleJobInspection(models.Model):
    _name = 'vehicle.job.inspection'
    _description = 'Vehicle Inspection'

    job_id = fields.Many2one('vehicle.job.card', string='Job')
    type_id = fields.Many2one('inspection.type', string='Inspection Type')
    description = fields.Text(string='Description')
    inspection_image_ids = fields.One2many('vehicle.job.inspection.image', 'inspection_id', string='Images')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, related="job_id.company_id")
    branch_id = fields.Many2one('company.branch', string='Branch', related='job_id.branch_id')

    def name_get(self):
        res = []
        for record in self:
            name = '[' + str(record.job_id.name) + "] - " + str(record.type_id.name)
            res.append((record.id, name))
        return res


class VehicleJobInspectionImage(models.Model):
    _name = 'vehicle.job.inspection.image'
    _description = 'Vehicle Inspection Image'

    name = fields.Char(string='Name')
    inspection_id = fields.Many2one('vehicle.job.inspection', string='Inspection')
    image = fields.Image(string='Image')
    file_name = fields.Char(string='File Name')


class InspectionType(models.Model):
    _name = 'inspection.type'
    _description = 'Inspection Type'

    name = fields.Char(string='Inspection Type')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
