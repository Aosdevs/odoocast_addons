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
from datetime import datetime
from odoo.exceptions import ValidationError


class VehicleAppointment(models.Model):
    _name = 'vehicle.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Vehicle Appointment'

    name = fields.Char(string='Number', copy=False)
    customer_id = fields.Many2one('res.partner', string='Customer')
    schedule_date = fields.Datetime(string='Schedule Date')
    status = fields.Selection([('draft', 'Draft'),
                               ('confirm', 'Confirmed'),
                               ('cancel', 'Cancelled')],
                              default='draft',
                              string='Status',
                              copy=False,
                              track_visibility='onchange')
    is_pickup = fields.Boolean(string='Pickup')
    is_dropoff = fields.Boolean(string='Drop Off')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id.id)
    branch_id = fields.Many2one('company.branch', string='Branch', required=True,
                                default=lambda self: self.env.user.branch_id.id)
    vehicle_id = fields.Many2one('vehicle.vehicle', string='Vehicle')
    symptom = fields.Text(string='Symptoms')
    check_drive_point = fields.Boolean(string='Check Drive Point', copy=False)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.appointment')
        return super(VehicleAppointment, self).create(vals)

    def action_confirm(self):
        self.status = 'confirm'

    def action_cancel(self):
        self.status = 'cancel'

    def action_drive_point(self):
        self.ensure_one()
        drive_id = self.env['vehicle.drive.point'].search([('appointment_id', '=', self.id)])
        if not drive_id:
            drive_id = self.env['vehicle.drive.point'].create({'appointment_id': self.id,
                                                               'customer_id': self.customer_id.id,
                                                               'date': self.schedule_date,
                                                               'branch_id': self.branch_id.id,
                                                               'check_pickup': self.is_pickup,
                                                               'check_drop_off': self.is_dropoff})
            self.check_drive_point = True
            template_id = self.env.ref('aspl_vehicle_repair.email_template_for_create_drive_point')
            if template_id:
                template_id.send_mail(self.id, force_send=True)
        return {'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': drive_id.id,
                'res_model': 'vehicle.drive.point'}


class VehicleDrivePoint(models.Model):
    _name = 'vehicle.drive.point'
    _description = 'Vehicle Drive Point'

    customer_id = fields.Many2one('res.partner', string='Customer')
    date = fields.Datetime(string='Record Date', default=datetime.now())
    check_pickup = fields.Boolean(string='Pickup')
    check_drop_off = fields.Boolean(string='Drop off')
    pickup_street = fields.Char(string='Pickup Street')
    pickup_street2 = fields.Char(string='Pickup Street 2')
    pickup_city = fields.Char(string='Pickup city')
    pickup_state_id = fields.Many2one('res.country.state', string='Pickup State Id')
    pickup_country_id = fields.Many2one('res.country', string='Pickup Country Id')
    pickup_zip = fields.Integer(string='Pickup Zip Code')
    pickup_date = fields.Datetime(string='PickUp Date')
    pickup_latitude = fields.Char(string='Pickup Latitude')
    pickup_longitude = fields.Char(string='Pickup Longitude')
    dropoff_latitude = fields.Char(string='Drop Off Latitude')
    dropoff_longitude = fields.Char(string='Drop Off Longitude')
    dropoff_date = fields.Datetime(string='Drop Date')
    dropoff_street = fields.Char(string='Drop Off Street')
    dropoff_street2 = fields.Char(string='Drop Off Street 2')
    dropoff_city = fields.Char(string='Drop Off city')
    dropoff_state_id = fields.Many2one('res.country.state', string='Drop Off State Id')
    dropoff_country_id = fields.Many2one('res.country', string='Drop Off Country Id')
    dropoff_zip = fields.Integer(string='Drop Off Zip Code')
    pickup_driver_id = fields.Many2one('res.users', string='PickUp Driver')
    drop_off_driver_id = fields.Many2one('res.users', string='Drop Driver')
    appointment_id = fields.Many2one('vehicle.appointment', string='Appointment')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id.id)
    branch_id = fields.Many2one('company.branch', string='Branch', required=True,
                                default=lambda self: self.env.user.branch_id.id)
    check_default_address = fields.Boolean(string='Do You Want To Copy Previous Address ?')
    select_address_id = fields.Many2one('vehicle.drive.point', string='Previous Drive Point')

    _sql_constraints = [
        ('appointment_uniq', 'unique (appointment_id)', "Appointment Related Drive Point Already Exist.")]

    def name_get(self):
        res = []
        for record in self:
            name = '[' + str(record.appointment_id.name) + "] - " + str(record.customer_id.name)
            res.append((record.id, name))
        return res

    @api.model
    def create(self, vals):
        result = super(VehicleDrivePoint, self).create(vals)
        result.appointment_id.check_drive_point = True
        return result

    def unlink(self):
        self.appointment_id.check_drive_point = False
        return super(VehicleDrivePoint, self).unlink()

    @api.onchange('appointment_id')
    def _onchange_appointment(self):
        self.branch_id = self.appointment_id.branch_id
        self.select_address_id = False
        if self.appointment_id:
            self.customer_id = self.appointment_id.customer_id
            self.check_pickup = self.appointment_id.is_pickup
            self.check_drop_off = self.appointment_id.is_dropoff

    @api.onchange('select_address_id')
    def _onchange_select_address_id(self):
        if self.select_address_id:
            if self.check_pickup and self.select_address_id.check_pickup:
                self.pickup_street = self.select_address_id.pickup_street
                self.pickup_street2 = self.select_address_id.pickup_street2
                self.pickup_city = self.select_address_id.pickup_city
                self.pickup_state_id = self.select_address_id.pickup_state_id
                self.pickup_country_id = self.select_address_id.pickup_country_id
                self.pickup_zip = self.select_address_id.pickup_zip
            else:
                self.pickup_street = False
                self.pickup_street2 = False
                self.pickup_city = False
                self.pickup_state_id = False
                self.pickup_country_id = False
                self.pickup_zip = False

            if self.check_drop_off and self.select_address_id.check_drop_off:
                self.dropoff_street = self.select_address_id.dropoff_street
                self.dropoff_street2 = self.select_address_id.dropoff_street2
                self.dropoff_city = self.select_address_id.dropoff_city
                self.dropoff_state_id = self.select_address_id.dropoff_state_id
                self.dropoff_country_id = self.select_address_id.dropoff_country_id
                self.dropoff_zip = self.select_address_id.dropoff_zip
            else:
                self.dropoff_street = False
                self.dropoff_street2 = False
                self.dropoff_city = False
                self.dropoff_state_id = False
                self.dropoff_country_id = False
                self.dropoff_zip = False

    @api.constrains('dropoff_date', 'pickup_date')
    def check_date_change(self):
        if str(self.pickup_date) < str(self.date):
            raise ValidationError(_("The PickUp Date is not valid."))
        if str(self.dropoff_date) < str(self.date):
            raise ValidationError(_("The Drop Date is not valid."))
        if self.pickup_date and self.dropoff_date:
            if str(self.dropoff_date) < str(self.pickup_date):
                raise ValidationError(_("The PickUp Date and Drop Date is not valid."))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
