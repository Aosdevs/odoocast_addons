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
from odoo.tests import Form


class VehicleWorkOrder(models.Model):
    _name = 'vehicle.work.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Vehicle Work order'

    name = fields.Char(string='Number', copy=False)
    customer_id = fields.Many2one('res.partner', string='Customer', copy=False)
    job_card_id = fields.Many2one('vehicle.job.card', string='Job Card')
    vehicle_id = fields.Many2one('vehicle.vehicle', string='Vehicle', copy=False)
    parts_ids = fields.One2many('vehicle.work.order.parts', 'work_order_id', string='Parts')
    consume_parts_ids = fields.One2many('vehicle.work.order.parts.consume', 'work_order_id', string='Parts')
    labor_ids = fields.One2many('vehicle.work.order.labor', 'work_order_id', string='Labor')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    amount_total_parts = fields.Monetary(string='Total Parts Amount', currency_field="currency_id",
                                         compute='_compute_amount_total_parts_labor')
    amount_parts = fields.Monetary(string='Parts Amount', currency_field="currency_id",
                                         compute='_compute_amount_total_parts_labor')
    amount_total_labor = fields.Monetary(string='Total Labor Amount', currency_field="currency_id",
                                         compute='_compute_amount_total_parts_labor')
    amount_total = fields.Monetary(string='Total Amount', currency_field="currency_id",
                                   compute='_compute_amount_total_parts_labor')
    status = fields.Selection([('draft', 'Draft'),
                               ('progress', 'In Progress'),
                               ('pause', 'Pause'),
                               ('completed', 'Completed'),
                               ('cancel', 'Cancel')],
                              default="draft",
                              string='Status',
                              copy=False,
                              track_visibility='onchange')
    technician_id = fields.Many2one('hr.employee', string='Technician')
    manager_id = fields.Many2one('hr.employee', string='Manager')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id.id)
    branch_id = fields.Many2one('company.branch', string='Branch', required=True,
                                default=lambda self: self.env.user.branch_id.id)
    package_id = fields.Many2one('customer.service.package', string='Package', copy=False)
    note = fields.Text(string='Note')
    vehicle_invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoices')
    stock_transfer_count = fields.Integer(string='Stock Transfer Count', compute='_compute_stock_transfer')
    is_invoice_create = fields.Boolean(string="Invoice Created")

    @api.model
    def create(self, vals):
        if self.env['vehicle.work.order'].search(
                [('job_card_id', '=', vals['job_card_id']), ('status', '!=', 'cancel')]):
            raise ValidationError(_("Job Card Related Work Order Is Not Cancelled."))
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.work.order')
            return super(VehicleWorkOrder, self).create(vals)

    @api.onchange('job_card_id')
    def _onchange_job_card(self):
        if self.job_card_id:
            self.customer_id = self.job_card_id.customer_id
            self.branch_id = self.job_card_id.branch_id
            self.package_id = self.job_card_id.package_id
        else:
            self.vehicle_id = False
            self.package_id = False
            self.customer_id = False
            self.branch_id = False
        return {'domain': {'branch_id': [('id', '=', self.job_card_id.branch_id.id)],
                           'customer_id': [('id', '=', self.job_card_id.customer_id.id)],
                           'vehicle_id': [('id', '=', self.job_card_id.vehicle_id.id)],
                           'package_id': [('id', '=', self.job_card_id.package_id.id)]}}

    @api.onchange('customer_id')
    def _onchange_customer(self):
        if self.customer_id:
            self.vehicle_id = self.job_card_id.vehicle_id
        else:
            self.vehicle_id = False

    @api.onchange('technician_id')
    def _onchange_technician(self):
        self.manager_id = False
        if self.technician_id:
            self.manager_id = self.technician_id.parent_id

    @api.onchange('package_id')
    def _onchange_package(self):
        self.consume_parts_ids = False
        self.labor_ids = False
        if self.package_id:
            for rec in self.package_id.customer_parts_ids:
                self.parts_ids = [(0, 0, {'product_id': rec.product_id,
                                          'quantity': rec.quantity,
                                          'price': rec.price})]
            for rec in self.package_id.customer_labor_ids:
                self.labor_ids = [(0, 0, {'labor_id': rec.labor_id,
                                          'hours': rec.hours,
                                          'rate': rec.rate})]

    @api.depends('consume_parts_ids', 'labor_ids', 'parts_ids')
    def _compute_amount_total_parts_labor(self):
        for rec in self:
            total = 0
            for record in rec.consume_parts_ids:
                total = total + record.amount_subtotal
            rec.amount_total_parts = total
            total = 0
            for record in rec.labor_ids:
                total = total + record.amount
            rec.amount_total_labor = total
            total = 0
            for record in rec.parts_ids:
                total = total + record.amount_subtotal
            rec.amount_parts = total
            # rec.amount_total = rec.amount_total_labor + rec.amount_total_parts

    def _compute_stock_transfer(self):
        self.stock_transfer_count = self.env['stock.picking'].search_count([('work_order_id', '=', self.id)])

    def action_progress(self):
        if self.status == 'draft':
            if not self.technician_id:
                raise ValidationError(_("Technician Is Missing To Start Job."))
            else:
                action_id = self.env.ref('aspl_vehicle_repair.add_product_wizard_action').read()[0]
                return action_id
            self.status = 'progress'
        elif self.status == 'pause':
            self.status = 'progress'

    def action_completed(self):
        action_id = self.env.ref('aspl_vehicle_repair.return_product_wizard_action').read()[0]
        return action_id


    def action_cancel(self):
        stock_ids = self.env['stock.picking'].search([('work_order_id', '=', self.id)])
        if stock_ids:
            for rec in stock_ids:
                rec.action_cancel()
        self.status = 'cancel'

    def action_pause(self):
        self.status = 'pause'

    def create_invoices(self):
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        invoice_lines = []
        for rec in self.consume_parts_ids:
            invoice_lines.append((0, 0, {'product_id': rec.product_id.id,
                                         'name': rec.product_id.name,
                                         'quantity': rec.consume_qty,
                                         'price_unit': rec.price}))
        for rec in self.labor_ids:
            invoice_lines.append(
                (0, 0,
                 {'product_id': rec.labor_id.product_id.id,
                  'name': '(Labor) ' + rec.labor_id.product_id.name,
                  'quantity': rec.hours,
                  'price_unit': rec.rate}))
        if self.job_card_id.check_pickup_drop:
            invoice_lines.append((0, 0, {'product_id': int(
                self.env['ir.config_parameter'].sudo().get_param('aspl_vehicle_repair.drop_product_id')) or False,
                                         'name': 'Pickup/Drop Cost',
                                         'quantity': 1}))
        invoice_record = self.env['account.move'].create({'move_type': 'out_invoice',
                                                          'journal_id': journal.id,
                                                          'partner_id': self.customer_id.id,
                                                          'invoice_date': date.today(),
                                                          'work_order_id': self.id,
                                                          'job_card_id': self.job_card_id.id,
                                                          'vehicle_id': self.vehicle_id.id,
                                                          'customer_package_id': self.package_id.id,
                                                          'branch_id': self.branch_id.id,
                                                          'invoice_line_ids': invoice_lines})
        self.is_invoice_create = True
        return {'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': invoice_record.id,
                'res_model': 'account.move'}

    def _compute_invoices(self):
        self.vehicle_invoice_count = self.env['account.move'].search_count([('work_order_id', '=', self.id)])


class VehicleWorkOrderLabor(models.Model):
    _name = 'vehicle.work.order.labor'
    _description = 'Vehicle Work order Labor'

    work_order_id = fields.Many2one('vehicle.work.order', string='Work Order')
    labor_id = fields.Many2one('vehicle.labor', string='Name')
    hours = fields.Float(string='Hours', default=1.00)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    rate = fields.Monetary(string='Rate', currency_field="currency_id")
    amount = fields.Monetary(string='Subtotal', currency_field="currency_id", compute='_compute_amount')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, related="work_order_id.company_id")
    branch_id = fields.Many2one('company.branch', string='Branch', related="work_order_id.branch_id")

    @api.onchange('labor_id')
    def _onchange_labor(self):
        self.rate = False
        if self.labor_id:
            self.rate = self.labor_id.amount

    @api.depends('hours', 'rate')
    def _compute_amount(self):
        for rec in self:
            rec.amount = 0.00
            if rec.rate > 0 and rec.hours > 0:
                rec.amount = rec.hours * rec.rate


class VehicleWorkOrderParts(models.Model):
    _name = 'vehicle.work.order.parts'
    _description = 'Vehicle Work order Parts'

    work_order_id = fields.Many2one('vehicle.work.order', string='Work Order')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.00)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    price = fields.Monetary(string='Price', currency_field="currency_id")
    amount_subtotal = fields.Monetary(string='Subtotal', currency_field="currency_id", compute='_compute_subtotal')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, related="work_order_id.company_id")
    branch_id = fields.Many2one('company.branch', string='Branch', related="work_order_id.branch_id")
    qty_available = fields.Float(string="On Hand", related="product_id.qty_available")

    @api.onchange('product_id')
    def _onchange_product(self):
        self.price = False
        if self.product_id:
            self.price = self.product_id.list_price
            # self.qty_available = self.product_id.qty_available

    @api.depends('price', 'quantity')
    def _compute_subtotal(self):
        for rec in self:
            rec.amount_subtotal = 0.00
            if rec.price > 0 and rec.quantity > 0:
                rec.amount_subtotal = rec.price * rec.quantity


class VehicleWorkOrderPartsConsume(models.Model):
    _name = 'vehicle.work.order.parts.consume'
    _description = 'Vehicle Work order Consume Parts'

    work_order_id = fields.Many2one('vehicle.work.order', string='Work Order')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.00)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    price = fields.Monetary(string='Price', currency_field="currency_id")
    amount_subtotal = fields.Monetary(string='Subtotal', currency_field="currency_id", compute='_compute_subtotal')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, related="work_order_id.company_id")
    branch_id = fields.Many2one('company.branch', string='Branch', related="work_order_id.branch_id")
    consume_qty = fields.Float(string='Consume Quantity')

    @api.onchange('product_id')
    def _onchange_product(self):
        self.price = False
        if self.product_id:
            self.price = self.product_id.list_price

    @api.depends('price', 'quantity')
    def _compute_subtotal(self):
        for rec in self:
            rec.amount_subtotal = 0.00
            if rec.price > 0 and rec.consume_qty > 0:
                rec.amount_subtotal = rec.price * rec.consume_qty

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
