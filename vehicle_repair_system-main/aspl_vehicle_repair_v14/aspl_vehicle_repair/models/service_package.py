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

from odoo import fields, models, api


class ServicePackageTemplate(models.Model):
    _name = 'service.package.template'
    _description = 'Service Package Template'

    name = fields.Char(string='Package Name')
    part_ids = fields.One2many('service.package.parts', 'package_id', string='Parts')
    labor_ids = fields.One2many('service.package.labor', 'package_id', string='Labor')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id.id)
    branch_id = fields.Many2one('company.branch', string='Branch', required=True,
                                default=lambda self: self.env.user.branch_id.id)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    amount_part = fields.Monetary(string='Parts Total Price', currency_field="currency_id",
                                  compute='_compute_total_parts_labor_price')
    amount_labor = fields.Monetary(string='Labor Total Price', currency_field="currency_id",
                                   compute='_compute_total_parts_labor_price')
    total_amount = fields.Monetary(string='Total Amount', currency_field="currency_id",
                                   compute='_compute_total_parts_labor_price')

    @api.depends('part_ids', 'labor_ids')
    def _compute_total_parts_labor_price(self):
        for rec in self:
            total = 0
            for record in rec.part_ids:
                total = total + record.amount_subtotal
            rec.amount_part = total
            total = 0
            for record in rec.labor_ids:
                total = total + record.amount_subtotal
            rec.amount_labor = total
            rec.total_amount = rec.amount_part + rec.amount_labor


class ServicePackageParts(models.Model):
    _name = 'service.package.parts'
    _description = 'Service Package Parts'

    package_id = fields.Many2one('service.package.template', string='Service Package')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.00)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    price = fields.Monetary(string='Price', currency_field="currency_id")
    amount_subtotal = fields.Monetary(string='Subtotal', currency_field="currency_id", compute='_compute_subtotal')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, related="package_id.company_id")
    branch_id = fields.Many2one('company.branch', string='Branch', related="package_id.branch_id")

    @api.onchange('product_id')
    def _onchange_product(self):
        self.price = False
        if self.product_id:
            self.price = self.product_id.list_price

    @api.depends('price', 'quantity')
    def _compute_subtotal(self):
        for rec in self:
            rec.amount_subtotal = rec.price * rec.quantity


class ServicePackageLabor(models.Model):
    _name = 'service.package.labor'
    _description = 'Service Package Labor'

    package_id = fields.Many2one('service.package.template', string='Service Package')
    labor_id = fields.Many2one('vehicle.labor', string='Name')
    description = fields.Text(string='Description')
    hours = fields.Float(string='Hours', default=1.00)
    rate = fields.Monetary(string='Rate', currency_field="currency_id")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    amount_subtotal = fields.Monetary(string='Subtotal', currency_field="currency_id",
                                      compute='_compute_amount_subtotal')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, related="package_id.company_id")
    branch_id = fields.Many2one('company.branch', string='Branch', related="package_id.branch_id")

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
