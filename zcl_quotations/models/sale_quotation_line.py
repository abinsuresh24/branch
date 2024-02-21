# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abin Suresh
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models, api


class SaleQuotationLine(models.Model):
    _name = 'sale.quotation.line'
    _description = "sale quotation line"

    sno = fields.Integer(string="Sno", store=True)
    item_id = fields.Many2one('product.product', string="Item", required=True)
    description = fields.Char(string="Description")
    units = fields.Float(string="Units", default=1)
    qty = fields.Float(string="Qty", default=0.0)
    rate = fields.Float(string="Rate", digits=(16, 3))
    gross = fields.Float(string="Gross", digits=(16, 3), readoly=True)
    sale_type = fields.Char(string="Sale Type", readoly=True)
    discount_on_foc = fields.Float(string="Discount on FOC", digits=(16, 3))
    bottom_price = fields.Float(string="Bottom Price", digits=(16, 3), readoly=True)
    net_value = fields.Float(string="Net Value", digits=(16, 3), readoly=True)
    stock_in_hand = fields.Float(string="Stock in hand")
    quotation_id = fields.Many2one('sale.quotation')

    @api.onchange('item_id')
    def _find_data(self):
        self.rate = self.item_id.cntr_max_price
        self.bottom_price = self.item_id.cntr_min_price
        self.sale_type = 'Foc' if self.item_id.foc else None

    @api.onchange('qty', 'item_id')
    def _calculate_gross(self):
        self.gross = float(self.rate * self.qty)

    @api.onchange('sale_type', 'item_id', 'gross')
    def _net_value(self):
        if not self.sale_type:
            self.net_value = float(self.gross)
        else:
            self.net_value = None

    @api.onchange('rate')
    def _calculate_gross_rate(self):
        self.gross = float(self.rate * self.qty)





