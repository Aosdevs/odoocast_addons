# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Promotion(models.Model):
    _name = 'promotion.promotion'
    _order = "sequence"
    _rec_name = 'promotion_code'
    _description = 'Promotion'

    # AVAILABLE_TIMES = [
    #     ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
    #     ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'),
    #     ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'),
    #     ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23')
    # ]

    promotion_code = fields.Char('Promotion Code', require=True)
    promotion_type = fields.Selection([('buy_x_get_y', 'Buy X Get Y Free'),
                                       ('buy_x_get_ser_free', 'Buy X Get Free Services'),],
                                      default="buy_x_get_y", require=True)
    from_date = fields.Datetime('From')
    to_date = fields.Datetime('To')
    # from_time = fields.Selection(AVAILABLE_TIMES, string="From Time")
    # to_time = fields.Selection(AVAILABLE_TIMES, string="To Time")
    free_product_condition_ids = fields.One2many('free.promotion.conditions', 'promotion_id')
    # free_services_condition_ids = fields.One2many('promotion.free.services', 'promotion_id')
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of promotions.")
    #invoice page
    active = fields.Boolean(default=True)

    @api.constrains('from_date','to_date')
    def date_check(self):
        if self.from_date > self.to_date:
            raise ValidationError("To Date must be greater than From date")

    @api.constrains('from_time', 'to_time')
    def time_check(self):
        if self.from_time and not self.to_time:
            raise ValidationError("You have to set 'To' Time.")
        if not self.from_time and self.to_time:
            raise ValidationError("You have to set 'From' Time.")
        if self.from_time and self.to_time and int(self.from_time) > int(self.to_time):
            raise ValidationError("To Time must be greater than From Time")


class FreeProductConditions(models.Model):
    _name = 'free.promotion.conditions'
    _description = 'Free Product Conditions'

    promotion_id = fields.Many2one('promotion.promotion')
    product_x_id = fields.Many2one('product.product', 'Product(X)')
    operator = fields.Selection([('is_eql_to', 'Is Equal To'),
                                 ('greater_than_or_eql', 'Greater Than Or Equal')])
    quantity = fields.Float('Quantity(X)')
    product_y_id = fields.Many2one('product.product', 'Free Product Product(Y)')
    quantity_y = fields.Float('Free Product Quantity(Y)')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: