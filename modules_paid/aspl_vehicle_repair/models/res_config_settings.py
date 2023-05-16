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

import ast
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # labor_id = fields.Many2one('product.product', string='Labor')
    drop_product_id = fields.Many2one('product.product', string='PickUp/Drop')
    check_pickup_drop = fields.Boolean(string='Pickup/Drop-off Charges')
    service_location_id = fields.Many2one('stock.location', string='Service Center Location')
    delivery_location_id = fields.Many2one('stock.location', string='Vehicle Service Location')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        # if get_param('aspl_vehicle_repair.labor_id'):
        #     res.update(
        #         labor_id=ast.literal_eval(get_param('aspl_vehicle_repair.labor_id') or False)
        #     )
        if get_param('aspl_vehicle_repair.service_location_id'):
            res.update(
                service_location_id=ast.literal_eval(get_param('aspl_vehicle_repair.service_location_id') or False)
            )
        if get_param('aspl_vehicle_repair.delivery_location_id'):
            res.update(
                delivery_location_id=ast.literal_eval(get_param('aspl_vehicle_repair.delivery_location_id') or False)
            )
        if get_param('aspl_vehicle_repair.check_pickup_drop'):
            res.update(
                check_pickup_drop=ast.literal_eval(get_param('aspl_vehicle_repair.check_pickup_drop') or False)
            )
        if get_param('aspl_vehicle_repair.drop_product_id'):
            res.update(
                drop_product_id=ast.literal_eval(get_param('aspl_vehicle_repair.drop_product_id') or False)
            )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        # set_param('aspl_vehicle_repair.labor_id', self.labor_id.id or False)
        set_param('aspl_vehicle_repair.service_location_id', self.service_location_id.id or False)
        set_param('aspl_vehicle_repair.delivery_location_id', self.delivery_location_id.id or False)
        set_param('aspl_vehicle_repair.drop_product_id', self.drop_product_id.id or False)
        set_param('aspl_vehicle_repair.check_pickup_drop', self.check_pickup_drop or False)

    @api.onchange('check_pickup_drop')
    def _onchange_check_pickup_drop(self):
        if not self.check_pickup_drop:
            self.drop_product_id = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
