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


class VehicleLabor(models.Model):
    _name = 'vehicle.labor'
    _description = 'Vehicle Labor'

    product_id = fields.Many2one('product.product', string="Labor Name")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)
    amount = fields.Monetary(string='Rate', currency_field="currency_id", store=True)
    type_id = fields.Many2one('labor.type', string='Labor Type')
    estimate_time = fields.Float(string='Estimate Time Spent')

    def name_get(self):
        res = []
        for record in self:
            name = '[' + str(record.type_id.name) + '] - ' + str(record.product_id.name)
            res.append((record.id, name))
        return res


class LaborType(models.Model):
    _name = 'labor.type'
    _description = 'Labor Type'

    name = fields.Char(string='Labor Type')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
