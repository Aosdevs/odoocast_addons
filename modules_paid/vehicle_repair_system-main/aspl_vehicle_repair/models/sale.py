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
from datetime import datetime as dt


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def apply_promotion(self):
        promotion_ids = self.env['promotion.promotion'].search(
            [('active', '=', 1), ('promotion_type', '=', 'buy_x_get_y'), ('from_date', '<=', dt.now()),
             ('to_date', '>=', dt.now())])

        if promotion_ids:
            self.order_line.filtered(lambda sol: sol.is_promotion).unlink()
            for promotion in promotion_ids:
                for order_line in self.order_line:
                    for promotion_line in promotion.free_product_condition_ids.filtered(lambda pml: pml.product_x_id.id == order_line.product_id.id):
                        if (promotion_line.operator == 'is_eql_to') and (
                                order_line.product_uom_qty == promotion_line.quantity):
                            self.env['sale.order.line'].create({
                                'order_id': self.id,
                                'product_id': promotion_line.product_y_id.id,
                                'name': promotion_line.product_y_id.name + " [Promotion]",
                                'product_uom_qty': promotion_line.quantity_y,
                                'price_unit': 0.00,
                                'is_promotion': True,
                            })
                        elif (promotion_line.operator == 'greater_than_or_eql') and (
                                order_line.product_uom_qty >= promotion_line.quantity):
                            self.env['sale.order.line'].create({
                                'order_id': self.id,
                                'product_id': promotion_line.product_y_id.id,
                                'name': promotion_line.product_y_id.name + " [Promotion]",
                                'product_uom_qty': promotion_line.quantity_y,
                                'price_unit': 0.00,
                                'is_promotion': True,
                            })


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_promotion = fields.Boolean(string="Promotion")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
