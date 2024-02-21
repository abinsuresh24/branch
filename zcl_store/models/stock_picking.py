# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Anoop Jayaprakash
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################


from odoo import fields, models


class Store(models.Model):
    _inherit = "stock.picking"
    _description = "Transfer"

    state = fields.Selection(selection_add=[('to_approve', 'To Approve'), ('approve', 'Approved')])
    gf_transfer_type = fields.Selection([('store_store', 'store_store'), ('store_shop', 'store_shop'), ('shop_store', 'shop_store')])
    branch = fields.Char(string="Branch")
    narration = fields.Char(string="Narration")
    sto_no = fields.Char(string="STO No")
