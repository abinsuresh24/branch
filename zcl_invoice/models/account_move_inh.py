# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Sayooj Tk
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import api, fields, models


class CustomInvoice(models.Model):
    _inherit = 'account.move'

    total_vat = fields.Float("VAT 5%", digits=(16, 3), widget='percentage')
    total_qty = fields.Float(string='Quantity')
    total_gross = fields.Float(string='Gross', digits=(16, 3))
    total_bottom_price = fields.Float(string='Bottom Price', digits=(16, 3))
    total_net_value = fields.Float(string='Net Value', digits=(16, 3))
    total_net = fields.Float(string='Net', digits=(16, 3))
    total_disc_on_foc = fields.Float(string='Disc On Foc', digits=(16, 3))
    total_quantity = fields.Float(string='Quantity')
    total_stock_in_hand = fields.Float(string='Stock in Hand')
    total_round_off = fields.Float(string='Round off', digits=(16, 3))
    discount_amount = fields.Float(string="Discount Amt", digits=(16, 3))

    default_vat_5 = fields.Float(string='Universal Tax Rate', default=5.0, digits=(16, 3))



    invoice_type = fields.Selection([('cash_memo', 'Cash memo'), ('cash_sale', 'Cash sale'), ('sale_return', 'Sale return'), ('cash_memo_return', 'Cash memo return')])

    sales_account = fields.Char(string='Sales Account')
    branches_id = fields.Many2one('stock.location', string='Branch', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_l_id, store=True)
    narration = fields.Html(string='Narration')
    gsm_no = fields.Char(string='GSM No')
    date = fields.Date(string='Date', default=fields.Date.today())
    salesmen = fields.Many2one('res.partner', string="Sales Man", domain="[('sales_man_true', '=', True)]")
    address = fields.Char(string='Address')
    customer = fields.Char(string="Customer")
    vat_no = fields.Char(string='VAT No')



    # @api.depends('amount_untaxed', 'default_vat_5', 'total_net', 'total_net')
    # def _compute_amount(self):
    #     print("heyyyyyyyyyyyyyyyyy")
    #     super(CustomInvoice, self)._compute_amount()
    #
    #     for invoice in self:
    #         invoice.amount_total = invoice.total_net + invoice.total_net
    #         invoice.amount_residual = invoice.total_net + invoice.total_vat




class CustomInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    sno = fields.Integer(string="Sno", store=True)
    units = fields.Float(string="Units", default=1)
    gross = fields.Float(string='Gross', digits=(16, 3), readoly=True)
    sale_type = fields.Char(string='Sales Type')
    discount_on_foc = fields.Float('Discount On FOC', digits=(16, 3))
    net_value = fields.Float(string='Net Value', digits=(16, 3), readoly=True)
    bottom_price = fields.Float(string='Bottom Price', digits=(16, 3), readoly=True)
    discounts = fields.Float(string="Discount", default=0, digits=(16, 3))

    stock_in_hand = fields.Integer('Stock In Hand')



