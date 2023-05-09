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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tests import Form

class ReturnProductWizard(models.TransientModel):
    _name = "return.product.wizard"
    _description = 'Return Products wizard'

    product_return = fields.Boolean(string="Parts Move In Stock")
    return_product_detail_ids = fields.One2many('return.product.line.wizard', 'return_wizard_id', string='Products')

    @api.model
    def default_get(self, fields):
        result = super(ReturnProductWizard, self).default_get(fields)
        if self.env.context and self.env.context.get('active_id'):
            work_order_id = self.env['vehicle.work.order'].browse(self.env.context.get('active_id'))
            return_line = []
            for line in work_order_id.consume_parts_ids:
                return_line.append((0, 0, {'product_id': line.product_id.id,
                                           'return_qty': line.consume_qty,
                                           }))
            result['return_product_detail_ids'] = return_line
        return result

    def return_product(self):
        if self.env.context and self.env.context.get('active_id'):
            work_order_id = self.env['vehicle.work.order'].browse(self.env.context.get('active_id'))
            return_product = []
            return_pro_line = []
            if self.product_return:
                flage = False
                for return_line in self.return_product_detail_ids:
                    return_product.append(return_line.product_id.id)
                    return_pro_line.append((0, 0, {'product_id': return_line.product_id.id,
                                                   'name': return_line.product_id.name,
                                                   'product_uom_qty': return_line.return_qty,
                                                   'product_uom': return_line.product_id.uom_id,
                                                   }))
                
                for line in work_order_id.consume_parts_ids.filtered(lambda line: line.product_id.id in return_product):
                    for re_line in self.return_product_detail_ids:
                        if line.product_id.id == re_line.product_id.id:
                            if line.consume_qty < re_line.return_qty:
                                raise ValidationError(_("Not return more then consume Qty."))
                            else:
                                line.consume_qty -= re_line.return_qty
                                flage = True
                if flage:
                    picking_id = self.env['stock.picking.type'].search([('code', '=', 'internal')])
                    if not picking_id:
                        raise ValidationError(_("First Configuare internal picking type ."))
                    service_location = self.env['ir.config_parameter'].sudo().get_param(
                        'aspl_vehicle_repair.service_location_id')
                    if not service_location:
                        raise ValidationError(_("First Set Service Location In config."))

                    internal_transfer_id = self.env['stock.picking'].create(
                        {'picking_type_id': picking_id.id,
                         'location_dest_id': picking_id.default_location_src_id.id,
                         'location_id': int(
                             service_location) if service_location else picking_id.default_location_dest_id.id,
                         'work_order_id': work_order_id.id,
                         'move_ids_without_package': return_pro_line
                         })
                    internal_transfer_id.action_confirm()
                    internal_transfer_id.action_assign()

                    wiz_act = internal_transfer_id.button_validate()
                    wizard = Form(self.env[(wiz_act.get('res_model'))].with_context(wiz_act['context'])).save()
                    wizard.process()

        location_dest_id = self.env['ir.config_parameter'].sudo().get_param(
            'aspl_vehicle_repair.delivery_location_id')
        if not location_dest_id:
            raise ValidationError(_("First Set Customer Location In config."))
        service_location = self.env['ir.config_parameter'].sudo().get_param(
            'aspl_vehicle_repair.service_location_id')
        if not service_location:
            raise ValidationError(_("First Set Service Location In config."))
        done_pickng = []
        for line in work_order_id.consume_parts_ids:
            done_pickng.append((0, 0, {'product_id': line.product_id.id,
                                       'name': line.product_id.name,
                                       'product_uom_qty': line.consume_qty,
                                       'product_uom': line.product_id.uom_id,
                               }))
        delivery_picking_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        delivery_transfer_id = self.env['stock.picking'].create(
            {'picking_type_id': delivery_picking_id.id,
             'location_id': int(service_location),
             'location_dest_id': int(
                 location_dest_id) if location_dest_id else delivery_picking_id.default_location_dest_id.id,
             'work_order_id': work_order_id.id,
             'move_ids_without_package': done_pickng
             })
        delivery_transfer_id.action_confirm()
        delivery_transfer_id.action_assign()
        wiz_act = delivery_transfer_id.button_validate()
        wizard = Form(self.env[(wiz_act.get('res_model'))].with_context(wiz_act['context'])).save()
        wizard.process()
        work_order_id.status = 'completed'

        return True

class ReturnProductLineWizard(models.TransientModel):
    _name = "return.product.line.wizard"
    _description = 'Return Products Line wizard'

    return_wizard_id = fields.Many2one("return.product.wizard")
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Integer(string='Return Quantity', default=1)
    return_qty = fields.Integer(string="Return Qty")
