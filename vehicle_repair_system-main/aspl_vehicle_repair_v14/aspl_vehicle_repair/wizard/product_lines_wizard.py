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
from odoo import models, fields, api


class ProductLineWizard(models.TransientModel):
    _name = "product.line.wizard"
    _description = "Product Lines Wizard"

    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Integer(string='Quantity', default=1)
    product_price = fields.Float(string='Price')
    qty_available = fields.Float(string="On Hand", related="product_id.qty_available")

    wizard_id = fields.Many2one('add.product.wizard', string='Wizard')

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.product_price = self.product_id.list_price
            # self.qty_available = self.product_id.qty_available

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
