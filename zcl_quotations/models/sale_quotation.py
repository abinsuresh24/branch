# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abin Suresh
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleQuotation(models.Model):
    _name = 'sale.quotation'
    _description = "sale quotation"
    _rec_name = "name"

    name = fields.Char(string="Reference", readonly=True, default=lambda self: _('New'))
    date = fields.Datetime(string="Date", default=fields.Date.today())
    state = fields.Selection([('draft', 'Draft'), ('sale', 'Confirmed'), ('cancel', 'Cancelled')], default='draft')
    partner_id = fields.Many2one('res.partner', string="Customer", domain="[('customer_true', '=', True)]", required=True)
    branch_id = fields.Many2one('res.branch', string="Branch", default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_id, store=True)
    payment_term = fields.Selection([('pdc', 'PDC'), ('lpo', 'LPO')])
    delivery_terms = fields.Char(string="Delivery Terms")
    narration = fields.Text(string="Narration")
    sales_man_id = fields.Many2one('res.partner', string="Sales Man", domain="[('sales_man_true', '=', True)]")
    line_ids = fields.One2many('sale.quotation.line', 'quotation_id', string='Line ids')
    total_qty = fields.Float(string="Quantity", store=True)
    total_stock_in_hand = fields.Float(string="Stock in hand", store=True)
    total_gross = fields.Float(string="Gross", store=True, digits=(16, 3))
    total_bottom_price = fields.Float(string="Bottom Price", store=True, digits=(16, 3))
    total_net_value = fields.Float(string="Net Value", store=True, digits=(16, 3))
    total_vat = fields.Float(string="Vat 5%", store=True, digits=(16, 3))
    total_disc_on_foc = fields.Float(string="Discount on FOC", store=True, digits=(16, 3))
    total_net = fields.Float(string="Net", store=True, digits=(16, 3))
    walkin_customer_bool = fields.Boolean(default=False, store=True)
    gsm_number = fields.Many2one('walkin.customer.line', string="GSM Number")
    gsm_number_customer = fields.Char(string="GSM No")
    customer_name = fields.Char(string="Customer Name", related='gsm_number.name', store=True)
    customer_address = fields.Char(string="Customer Address", related='gsm_number.address', store=True)
    sequence_number = fields.Char(string="Sequence No")

    @api.model
    def create(self, vals_list):
        if vals_list.get('name', 'New') == 'New':
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'sale.quotation.sequence') or 'New'
        result = super().create(vals_list)
        return result

    # def sale_confirm(self):
    #     self.state = "sale"

    def sale_confirm(self):
        for line in self.line_ids:
            if line.rate < line.bottom_price:
                raise ValidationError(
                    "Rate cannot be lower than the bottom price for product '%s'" % line.item_id.name)

        self.state = "sale"

    def sale_cancel(self):
        self.state = "cancel"

    def sale_draft(self):
        self.state = "draft"

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        sl_no = 1
        for line in self.line_ids:
            line.sno = sl_no
            sl_no += 1
        gross_sum = 0
        qty_sum = 0
        stock_sum = 0
        sum_bottom_price = 0
        sum_net_value = 0
        sum_foc = 0
        for rec in self.line_ids:
            gross_sum += rec.gross
            qty_sum += rec.qty
            stock_sum += rec.stock_in_hand
            sum_bottom_price += rec.bottom_price
            sum_net_value += rec.net_value
            sum_foc += rec.discount_on_foc
        self.total_qty = qty_sum
        self.total_stock_in_hand = stock_sum
        self.total_gross = gross_sum
        self.total_bottom_price = sum_bottom_price
        self.total_net_value = sum_net_value
        self.total_disc_on_foc = sum_foc
        self.total_vat = float(self.total_net_value * 5/100)
        self.total_net = float(self.total_vat + self.total_net_value)

    @api.onchange('partner_id')
    def _onchange_partner_ids(self):
        if self.partner_id.id == int(self.env.ref('zcl_contacts.walkin_customer_data').id):
            self.walkin_customer_bool = True
        else:
            self.walkin_customer_bool = False
        if self.partner_id:
            self.gsm_number_customer = self.partner_id.mobile

    # @api.onchange('partner_id')
    # def _onchange_partner_ids(self):
    #     if self.partner_id.id == int(self.env.ref('zcl_contacts.walkin_customer_data').id):
    #         self.walkin_customer_bool = True
    #         self.gsm_num_customer = False  
    #     else:
    #         self.walkin_customer_bool = False
    #         if self.partner_id:
    #             self.gsm_num_customer = self.partner_id.mobile
