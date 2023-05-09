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

class AddProductWizard(models.TransientModel):
    _name = "add.product.wizard"
    _description = 'Addons Products wizard'

    product_detail_ids = fields.One2many('product.line.wizard', 'wizard_id', string='Products')

    @api.model
    def default_get(self, fields):
        result = super(AddProductWizard, self).default_get(fields)
        if self.env.context and self.env.context.get('active_id'):
            work_order_id = self.env['vehicle.work.order'].browse(self.env.context.get('active_id'))
            part_line = []
            consume_product_dict = {}
            part_product = []
            for consume_line in work_order_id.consume_parts_ids:
                consume_product_dict.update({consume_line.product_id.id: consume_line.consume_qty})
            for line in work_order_id.parts_ids:
                if line.product_id.qty_available > 0.0:
                    if line.product_id.id in consume_product_dict.keys():
                        if line.quantity > consume_product_dict.get(line.product_id.id):
                            part_line.append((0, 0, {'product_id': line.product_id.id,
                                                     'product_qty': line.quantity - consume_product_dict.get(line.product_id.id),
                                                     'product_price': line.price,
                                                     'qty_available': line.product_id.qty_available}))
                    else:
                        part_line.append((0, 0, {'product_id': line.product_id.id,
                                                 'product_qty': line.quantity,
                                                 'product_price': line.price,
                                                 'qty_available': line.product_id.qty_available}))
            result['product_detail_ids'] = part_line
        return result

    def add_product(self):
        # if self.product_detail_ids.filtered(lambda line: line.qty_available <= 0):
        for line in self.product_detail_ids:
            if line.qty_available <= 0:
                raise ValidationError(_("'%s' product without on hand qty not consume.", line.product_id.name))
        # if self.product_detail_ids.filtered(lambda line: line.product_qty > line.qty_available):
        for line in self.product_detail_ids:
            if line.product_qty > line.qty_available:
                raise ValidationError(_("Not use more then on hand qty for '%s' product.", line.product_id.name))
        work_order_id = self.env['vehicle.work.order'].browse(self._context.get('active_id'))
        stock_lines = []
        for rec in self.product_detail_ids:
            stock_lines.append((0, 0, {'product_id': rec.product_id.id,
                                       'name': rec.product_id.name,
                                       'product_uom_qty': rec.product_qty,
                                       'product_uom': rec.product_id.uom_id,
                                       }))

        picking_id = self.env['stock.picking.type'].search([('code', '=', 'internal')])
        if not picking_id:
            raise ValidationError(_("First Configuare internal picking type ."))
        storage_location_id = self.env['ir.config_parameter'].sudo().get_param(
            'aspl_vehicle_repair.service_location_id')
        if not storage_location_id:
            raise ValidationError(_("First Set Service Location In config."))
        internal_transfer_id = self.env['stock.picking'].create(
            {'picking_type_id': picking_id.id,
             'location_id': picking_id.default_location_src_id.id,
             'location_dest_id': int(
                 storage_location_id) if storage_location_id else picking_id.default_location_dest_id.id,
             'work_order_id': work_order_id.id,
             'move_ids_without_package': stock_lines
             })
        internal_transfer_id.action_confirm()
        internal_transfer_id.action_assign()

        wiz_act = internal_transfer_id.button_validate()
        wizard = Form(self.env[(wiz_act.get('res_model'))].with_context(wiz_act['context'])).save()
        wizard.process()

        for line in self.product_detail_ids:
            consume_id = self.env['vehicle.work.order.parts.consume'].search([('work_order_id', '=', work_order_id.id),
                                                                              ('product_id', '=', line.product_id.id)])
            if consume_id:
                consume_id.quantity += line.product_qty
                consume_id.consume_qty += line.product_qty
            else:
                self.env['vehicle.work.order.parts.consume'].create({
                    'work_order_id': work_order_id.id,
                    'product_id': line.product_id.id,
                    'quantity': line.product_qty,
                    'price': line.product_price,
                    'consume_qty': line.product_qty
                })
        work_order_id.status = "progress"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
