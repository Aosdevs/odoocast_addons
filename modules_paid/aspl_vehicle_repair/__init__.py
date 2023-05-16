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

from . import models
from . import wizard


def uninstall_hook(cr, registry):
    cr.execute(
        "DELETE FROM ir_config_parameter WHERE key in ('aspl_vehicle_repair.drop_product_id','aspl_vehicle_repair.check_pickup_drop','aspl_vehicle_repair.labor_id')"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
