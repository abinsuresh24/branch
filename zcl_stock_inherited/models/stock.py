# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abin Suresh
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models

from odoo import fields, models, api, _


class LocationInherits(models.Model):
    _inherit = "stock.location"
    _description = "Shop"
    _rec_name = 'name'

    name = fields.Char('Shop Name', required=True)
    shop_location = fields.Boolean(default=False, store=True)
    reference = fields.Char(readonly=True, required=True, copy=False, default=lambda self: _('New'))


class WarehouseInherits(models.Model):
    _inherit = "stock.warehouse"
    _description = "warehouse"
    _rec_name = 'name'

    reference = fields.Char(readonly=True, required=True, copy=False, default=lambda self: _('New'))
    name = fields.Char('Store', required=True, default="")
    code = fields.Char('Short Name', required=True, size=5, help="Short name used to identify your store")
    store_warehouse = fields.Boolean(default=False)
