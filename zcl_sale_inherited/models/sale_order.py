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
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # commen field
    total_vat = fields.Float("VAT 5%", digits=(16, 3), widget='percentage')
    total_qty = fields.Float(string='Quantity')
    total_gross = fields.Float(string='Gross', digits=(16, 3))
    total_bottom_price = fields.Float(string='Bottom Price', digits=(16, 3))
    total_net_value = fields.Float(string='Net Value', digits=(16, 3))
    total_net = fields.Float(string='Net', digits=(16, 3))
    total_disc_on_foc = fields.Float(string='Disc On Foc', digits=(16, 3))

    sale_types = fields.Selection(
        selection=[
            ('cm', "cm"),
            ('do', "do")])

    state = fields.Selection(
        selection=[
            ('draft', "Drafted"),
            ('sent', "Quotation Sent"),
            ('sale', "Confirmed"),
            ('done', "Locked"),
            ('cancel', "Cancelled"),
            ('invoiced', 'Invoiced')
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    @api.onchange('order_line')
    def _onchange_line_ids(self):
        serial_no = 1
        for line in self.order_line:
            line.serial_no = serial_no
            serial_no += 1
        gross_sum = 0
        qty_sum = 0
        # stock_sum = 0
        sum_bottom_price = 0
        sum_net_value = 0
        sum_foc = 0
        sum_disc = 0
        for rec in self.order_line:
            rec.gross = float(rec.rate * rec.product_uom_qty)
            rec.net_value = rec.gross
            if rec.sale_type:
                rec.discount_on_foc = -(rec.rate)
                rec.net_value = 0
            # if rec.rate < rec.bottom_price:
            #     raise ValidationError("Rate must be greater than Bottom price")
            # if rec.rate < rec.product_id.cntr_max_price:
            #     rec.discounts = -(rec.product_id.cntr_max_price - rec.rate)
            # else:
            #     rec.discounts = 0
            gross_sum += rec.gross
            qty_sum += rec.product_uom_qty
            # stock_sum += rec.stock_in_hand
            sum_bottom_price += rec.bottom_price
            sum_net_value += rec.net_value
            sum_foc += rec.discount_on_foc
            sum_disc += rec.discounts
        self.total_qty = qty_sum
        # self.total_stock_in_hand = stock_sum
        self.total_gross = gross_sum
        self.total_bottom_price = sum_bottom_price
        self.total_net_value = sum_net_value
        self.discount_amount = -(sum_disc)
        self.total_disc_on_foc = -(sum_foc)
        self.total_vat = float(self.total_net_value * 5 / 100)
        self.total_net = float(self.total_vat + self.total_net_value)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sno = fields.Integer(string="Sno", store=True)
    units = fields.Float(string="Units", default=1)
    # qty = fields.Float(string="Qty")
    rate = fields.Float(string="Rate", digits=(16, 3))
    gross = fields.Float(string="Gross", digits=(16, 3))
    sale_type = fields.Char(string="Sale Type")
    discount_on_foc = fields.Float(string="Discount on FOC", digits=(16, 3))
    bottom_price = fields.Float(string="Bottom Price", digits=(16, 3))
    net_value = fields.Float(string="Net Value", digits=(16, 3))
    stock_in_hand = fields.Float(string="Stock in hand")

    @api.onchange('product_id')
    def _find_data(self):
        # self.rate = self.product_id.cntr_max_price
        # self.bottom_price = self.product_id.cntr_min_price
        # self.stock_in_hand = self.product_id.qty_available
        self.sale_type = 'FOC' if self.product_id.foc else None
        if self.order_id.normal_do:
            self.rate = self.product_id.cntr_max_price
        if self.order_id.normal_do:
            self.rate = self.product_id.cntr_max_price
        if self.order_id.internal_direct_order:
            self.rate = self.product_id.traders_price
        if self.order_id.project_direct_order:
            self.rate = self.product_id.project_price
        if self.order_id.cash_sale:
            self.rate = self.product_id.cash_sale_price

    # @api.onchange('product_uom_qty', 'product_id')
    # def _calculate_gross(self):
    #     self.gross = float(self.rate * self.product_uom_qty)

    # @api.onchange('sale_type', 'product_id', 'gross')
    # def _net_value(self):
    #     if not self.sale_type:
    #         self.net_value = float(self.gross)
    #     else:
    #         self.net_value = None

    @api.onchange('rate')
    def _calculate_gross_rate(self):
        if self.rate < self.bottom_price:
            raise ValidationError("Rate must be greater than Bottom price")

