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
from datetime import date
from odoo.exceptions import ValidationError


class CustomerServicePackage(models.Model):
    _name = "customer.service.package"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Customer Service Packages"

    customer_id = fields.Many2one('res.partner', string='Customer')
    vehicle_id = fields.Many2one('vehicle.vehicle', string='Vehicle')
    package_template_id = fields.Many2one('service.package.template', string='Package')
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    drive_km = fields.Float(string=' Drive KM')
    status = fields.Selection([('draft', 'Draft'),
                               ('confirm', 'Confirmed'),
                               ('expire', 'Expired'),
                               ('cancel', 'Cancelled')],
                              default='draft',
                              copy=False,
                              string='Status',
                              track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 related='package_template_id.company_id')
    branch_id = fields.Many2one('company.branch', string='Branch')
    customer_parts_ids = fields.One2many('customer.service.package.parts', 'customer_package_id')
    customer_labor_ids = fields.One2many('customer.service.package.labors', 'customer_package_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    amount_part = fields.Monetary(string='Parts Total Price', currency_field="currency_id",
                                  compute='_compute_total_parts_labor_price')
    amount_labor = fields.Monetary(string='Labor Total Price', currency_field="currency_id",
                                   compute='_compute_total_parts_labor_price')
    total_amount = fields.Monetary(string='Total Amount', currency_field="currency_id",
                                   compute='_compute_total_parts_labor_price')
    package_2_invoice_count = fields.Integer(string='Package Invoice Count', compute='_compute_invoices')

    def name_get(self):
        res = []
        for record in self:
            name = '[' + str(record.package_template_id.name) + "] - " + str(record.customer_id.name)
            res.append((record.id, name))
        return res

    @api.onchange('customer_id')
    def _onchange_customer(self):
        self.vehicle_id = False
        self.drive_km = False

    @api.onchange('package_template_id')
    def _onchange_package_template(self):
        self.customer_parts_ids = False
        self.customer_labor_ids = False
        self.branch_id = False
        if self.package_template_id:
            self.branch_id = self.package_template_id.branch_id.id
            for rec in self.package_template_id.part_ids:
                self.customer_parts_ids = [(0, 0, {'product_id': rec.product_id,
                                                   'quantity': rec.quantity,
                                                   'price': rec.price})]
            for rec in self.package_template_id.labor_ids:
                self.customer_labor_ids = [(0, 0, {'labor_id': rec.labor_id,
                                                   'hours': rec.hours,
                                                   'rate': rec.rate, })]

    @api.constrains('date_end')
    def _check_date_change(self):
        if self.date_start and self.date_end:
            if str(self.date_end) < str(self.date_start):
                raise ValidationError(_("The Start Date and End Date is not valid."))

    @api.depends('customer_parts_ids', 'customer_labor_ids')
    def _compute_total_parts_labor_price(self):
        for rec in self:
            total = 0
            for record in rec.customer_parts_ids:
                total = total + record.amount_subtotal
            rec.amount_part = total
            total = 0
            for record in rec.customer_labor_ids:
                total = total + record.amount_subtotal
            rec.amount_labor = total
            rec.total_amount = rec.amount_part + rec.amount_labor

    def _compute_invoices(self):
        self.package_2_invoice_count = self.env['account.move'].search_count([('customer_package_id', '=', self.id)])

    def action_draft(self):
        self.status = 'draft'

    def action_confirm(self):
        self.status = 'confirm'
        if self.date_end == date.today():
            self.status = 'expire'

    def action_cancel(self):
        self.status = 'cancel'

    def _auto_expire_customer_package(self):
        records = self.env['customer.service.package'].search(
            [('status', '=', 'confirm'), ('date_end', '=', date.today())])
        records.status = 'expire'

    def create_invoices(self):
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        invoice_lines = []
        for rec in self.customer_parts_ids:
            invoice_lines.append((0, 0, {'product_id': rec.product_id.id,
                                         'name': rec.product_id.name,
                                         'quantity': rec.quantity,
                                         'price_unit': rec.price}))
        for rec in self.customer_labor_ids:
            invoice_lines.append((0, 0, {
                # 'product_id': int(self.env['ir.config_parameter'].sudo().get_param('aspl_vehicle_repair.labor_id')) or False,
                'product_id': rec.labor_id.product_id.id,
                'name': '(Labor) ' + rec.labor_id.product_id.name,
                'quantity': rec.hours,
                'price_unit': rec.rate}))
        invoice_record = self.env['account.move'].create({'move_type': 'out_invoice',
                                                          'journal_id': journal.id,
                                                          'currency_id': self.currency_id.id,
                                                          'partner_id': self.customer_id.id,
                                                          'invoice_date': date.today(),
                                                          'customer_package_id': self.id,
                                                          'vehicle_id': self.vehicle_id.id,
                                                          'branch_id': self.branch_id.id,
                                                          'invoice_line_ids': invoice_lines})
        return {'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': invoice_record.id,
                'res_model': 'account.move'}


class CustomerServiceParts(models.Model):
    _name = "customer.service.package.parts"
    _description = "Customer Service Packages Parts"

    customer_package_id = fields.Many2one('customer.service.package', string='Customer Service Package')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.00)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    price = fields.Monetary(string='Price', currency_field="currency_id")
    amount_subtotal = fields.Monetary(string='Subtotal', currency_field="currency_id", compute='_compute_subtotal')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 related="customer_package_id.company_id")
    branch_id = fields.Many2one('company.branch', string='Branch', related="customer_package_id.branch_id")

    @api.onchange('product_id')
    def _onchange_product(self):
        self.price = False
        if self.product_id:
            self.price = self.product_id.list_price

    @api.depends('price', 'quantity')
    def _compute_subtotal(self):
        for rec in self:
            rec.amount_subtotal = rec.price * rec.quantity


class CustomerServiceLabors(models.Model):
    _name = "customer.service.package.labors"
    _description = "Customer Service Packages labors"

    customer_package_id = fields.Many2one('customer.service.package', string='Service Package')
    labor_id = fields.Many2one('vehicle.labor', string='Name')
    description = fields.Text(string='Description')
    hours = fields.Float(string='Hours', default=1.00)
    rate = fields.Monetary(string='Rate', currency_field="currency_id")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    amount_subtotal = fields.Monetary(string='Subtotal', currency_field="currency_id",
                                      compute='_compute_amount_subtotal')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 related="customer_package_id.company_id")
    branch_id = fields.Many2one('company.branch', string='Branch', related="customer_package_id.branch_id")

    @api.onchange('labor_id')
    def _onchange_labor(self):
        self.rate = False
        if self.labor_id:
            self.rate = self.labor_id.amount

    @api.depends('hours', 'rate')
    def _compute_amount_subtotal(self):
        for rec in self:
            rec.amount_subtotal = rec.hours * rec.rate

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
