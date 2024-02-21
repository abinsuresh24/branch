# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Sayooj T K
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models


class ProductMovesWizard(models.Model):

    _name = "product.moves.wizard"
    _description = "Product Move wizard"

    product_id = fields.Many2one('product.product')
    qty = fields.Float(string='Quantity')
    date = fields.Datetime(string='Date scheduled')
    location_id = fields.Many2one('stock.location', string="From", required=True)
    location_dest_id = fields.Many2one('stock.location', string="To", required=True)
    available_qty = fields.Float(string="Available Quantity", store=True)
    requisition_line_id = fields.Many2one('purchase.requisition.line', string='wizard')
