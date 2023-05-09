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
from datetime import date


class VehicleModel(models.Model):
    _name = 'vehicle.model'
    _description = 'Vehicle Model'

    name = fields.Char(string='Model Name')
    model_year = fields.Char(string='Model Year')
    seats_number = fields.Integer(string='Seat Capacity')
    doors_number = fields.Integer(string='Doors Number')
    manufacture_id = fields.Many2one('vehicle.manufacture', string='Manufacture')
    type = fields.Many2one('vehicle.type', string='Vehicle Type')
    check_door = fields.Boolean(string='Check door')
    transmission = fields.Selection([('manual', 'Manual'),
                                     ('auto', 'Automatic')],
                                    string='Transmission')
    fuel_type = fields.Selection([('diesel', 'Diesel'),
                                  ('petrol', 'Petrol'),
                                  ('lpg', 'LPG'),
                                  ('electric', 'Electric'),
                                  ('gas', 'Gasoline'),
                                  ('hybrid', 'Hybrid')],
                                 string='Fuel Type')
    engine_type = fields.Many2one('engine.type', string='Engine Type')
    engine_capacity = fields.Many2one('engine.capacity', string='Engine Capacity')
    max_speed = fields.Float(string='Max Speed')

    @api.constrains('model_year', 'seats_number')
    def _check_model_year_seats(self):
        for record in self:
            if len(str(record.model_year)) != 4:
                raise ValidationError(_("The Model Year Is Not Valid."))
            if int(record.model_year) > date.today().year:
                raise ValidationError(_("The Manufacture Year %(year)s is Grater Than Current Year",
                                        year=record.model_year))
            if record.seats_number < 1:
                raise ValidationError(_("The Total Seats %(seat)s Is Not Valid.",
                                        seat=record.seats_number))

    @api.onchange('model_year')
    def _onchange_model_year(self):
        if self.model_year:
            try:
                self.model_year = int(self.model_year)
            except:
                raise ValidationError(_('manufacture year %(year)s is not valid year.', year=self.model_year))

    @api.onchange('type')
    def _onchange_type(self):
        self.check_door = False
        if self.type and self.type.wheel > 2:
            self.check_door = True


class VehicleVehicle(models.Model):
    _name = 'vehicle.vehicle'
    _description = 'Vehicle Vehicle'

    customer_id = fields.Many2one('res.partner', string='Customer')
    model_id = fields.Many2one('vehicle.model', string='Model')
    license_plate = fields.Char(string='License Plate')
    chassis_number = fields.Char(string='Chassis Number')
    color = fields.Char(string='Color')
    registration_date = fields.Date(string='Registration Date')
    manufactured_year = fields.Char(string='Manufactured Year')
    manufactured_month = fields.Integer(string='Manufactured Month')

    _sql_constraints = [('license_uniq', 'unique (license_plate)', "Licence Plate already exists !"),
                        ('chassis_uniq', 'unique (chassis_number)', "Chassis No. already exists !"), ]

    @api.constrains('manufactured_month', 'manufactured_year')
    def _check_manufacture_month_year(self):
        for record in self:
            if len(str(record.manufactured_year)) != 4:
                raise ValidationError(_("the manufacture year %(year)s is not valid",
                                        year=record.manufactured_year))
            if int(record.manufactured_year) > date.today().year:
                raise ValidationError(_("the manufacture year %(year)s is Grater Than Current Year",
                                        year=record.manufactured_year))
            if record.manufactured_month < 1 or record.manufactured_month > 12:
                raise ValidationError(_("the manufacture month %(month)s is not valid",
                                        month=record.manufactured_month))
            if int(record.manufactured_year) == date.today().year and record.manufactured_month > date.today().month:
                raise ValidationError(
                    _("the manufacture year is %(year)s and month %(month)s is grater than current month",
                      month=record.manufactured_month, year=record.manufactured_year))

    def name_get(self):
        res = []
        for record in self:
            name = '[' + str(record.license_plate) + "] - " + str(record.model_id.name)
            res.append((record.id, name))
        return res

    @api.onchange('manufactured_year')
    def _onchange_manufactured_year(self):
        try:
            self.manufactured_year = int(self.manufactured_year)
        except:
            raise ValidationError(_("the manufacture year is not valid Year"))

    @api.onchange('model_id')
    def _onchange_model(self):
        if self.model_id:
            self.manufactured_year = int(self.model_id.model_year)
        else:
            self.manufactured_year = False

    @api.constrains('registration_date')
    def _check_registration_date(self):
        for rec in self:
            if rec.registration_date:
                if str(rec.registration_date.year) < rec.manufactured_year or \
                        (str(rec.registration_date.year) == rec.manufactured_year and
                         int(rec.registration_date.month) < rec.manufactured_month):
                    raise ValidationError(_("Registration Date is not valid."))


class VehicleManufacture(models.Model):
    _name = 'vehicle.manufacture'
    _description = 'Vehicle Manufacture'

    name = fields.Char(string='Name')
    code = fields.Integer(string='Code')


class VehicleInsurance(models.Model):
    _name = 'vehicle.insurance'
    _description = 'Vehicle Insurance Details'

    vehicle_id = fields.Many2one('vehicle.vehicle', string='Vehicle')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    insurance_id = fields.Many2one('res.partner', string='Insurance Company')

    def name_get(self):
        res = []
        for record in self:
            name = '[' + str(record.vehicle_id.license_plate) + '] - ' + str(record.vehicle_id.model_id.name)
            res.append((record.id, name))
        return res


class VehicleType(models.Model):
    _name = 'vehicle.type'
    _description = 'Vehicle Type'

    name = fields.Char(string='Name')
    wheel = fields.Integer(string='Wheels')

    def name_get(self):
        res = []
        for record in self:
            name = '[' + str(record.wheel) + ' - Wheeler] - ' + str(record.name)
            res.append((record.id, name))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
