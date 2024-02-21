# -- coding: utf-8 --
###################################################################################

# Author       :  Abdul Hakeem
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
############################################################

from odoo import fields, models, api
from datetime import date
from odoo.tests import Form


READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'sale', 'done', 'cancel'}
}


class SaleInherit(models.Model):
    _inherit = "sale.order"

    sales_account = fields.Char(string='Sales Account')
    branches_id = fields.Many2one('stock.location', string='Branch', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_l_id, store=True)
    narration = fields.Html(string='Narration')
    gsm_no = fields.Char(string='GSM No')
    date = fields.Date(string='Date', default=fields.Date.today())
    salesmen = fields.Many2one('res.partner', string="Sales Man", domain="[('sales_man_true', '=', True)]")
    address = fields.Char(string='Address')
    customer = fields.Char(string="Customer")
    vat_no = fields.Char(string='VAT No')
    total_vat = fields.Float("VAT 5%", digits=(16, 3), widget='percentage')
    total_quantity = fields.Float(string='Quantity')
    total_stock_in_hand = fields.Float(string='Stock in Hand')
    total_round_off = fields.Float(string='Round off', digits=(16, 3))
    cash_memo_invoice_count = fields.Integer()
    cash_memo_invoice_ids = fields.Many2one('account.move', string='Invoices')
    cash_memo = fields.Boolean(string="Cash Memo")




    @api.onchange('customer')
    def _onchange_customer(self):
        self.partner_id = int(self.env.ref('zcl_contacts.walkin_customer_data').id)

    def action_confirm_cash_memo(self):
        self.sale_types = 'cm'
        self.action_confirm()
        branch_id = self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1)
        walk_customer = self.env['res.partner'].search([('shop_id', '=', branch_id.branch_l_id.id)], limit=1,)
        self.env['walkin.customer.line'].sudo().create({
            'name': self.customer,
            'partner_id': walk_customer.id,
            'phone': self.gsm_no,
            'address': self.address,
            'vat_no': self.vat_no
        })
        # value = self._create_invoices(final=True)
        # if value:
        #     value.action_post()
        if self.picking_ids:
            if self.picking_ids.state == 'assigned':
                for rec in self.picking_ids:
                    for res in rec.move_ids:
                        res.quantity_done = res.product_uom_qty
                    rec.button_validate()

        invoice_date_value = fields.Date.today()
        invoice = self.env['account.move'].create(
            {'move_type': 'out_invoice', 'partner_id': self.partner_id.id, 'invoice_origin': self.name, 'invoice_type': 'cash_memo',
             'state': 'draft', 'invoice_date': invoice_date_value, 'gsm_no': self.gsm_no,
             'address': self.address, 'vat_no': self.vat_no,
             'salesmen': self.salesmen, 'sales_account': self.sales_account, 'total_qty': self.total_qty,
             'total_gross': self.total_gross, 'total_net_value': self.total_net_value, 'total_disc_on_foc': self.total_disc_on_foc,
             'total_stock_in_hand': self.total_stock_in_hand, 'total_bottom_price': self.total_bottom_price, 'total_round_off': self.total_round_off,
             'total_vat': self.total_vat, 'total_net': self.total_net,'ks_global_tax_rate': 5.0,
             })
        for rec in self.order_line:
            if rec.product_id.foc == True:
                self.env['account.move.line'].create(
                    {'product_id': rec.product_id.id,
                     'quantity': rec.product_uom_qty,
                     'price_unit': 0,
                     'gross': rec.gross,
                     'sale_type': rec.sale_type,
                     'discount_on_foc': rec.discount_on_foc,
                     'net_value': rec.net_value,
                     'bottom_price': rec.bottom_price,
                     'tax_ids': None,
                     'move_id': invoice.id})
            else:
                self.env['account.move.line'].create(
                    {'product_id': rec.product_id.id,
                     'quantity': rec.product_uom_qty,
                     'price_unit': rec.rate,
                     'gross': rec.gross,
                     'sale_type': rec.sale_type,
                     'discount_on_foc': rec.discount_on_foc,
                     'net_value': rec.net_value,
                     'bottom_price': rec.bottom_price,
                     'tax_ids': None,
                     'move_id': invoice.id})

        invoice.amount_button()
        invoice.state = 'posted'
        journal = self.env["account.journal"].sudo().search([('type', '=', 'cash')], limit=1)
        return_form = Form(self.env["account.payment.register"].sudo().with_context(
            active_ids=invoice.ids,
            active_model="account.move",
            default_amount=invoice.total_net,
            default_journal_id=journal.id
        ))
        return_wizard = return_form.save()
        action = return_wizard._create_payments()
        if invoice:
            self.cash_memo_invoice_ids = invoice.id
            self.invoice_ids = invoice
            self.invoice_count = 1
            self.cash_memo_invoice_count = 1
    def action_view_cash_memo_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'move_type': 'out_invoice',
            'res_id': self.cash_memo_invoice_ids.id,
            'view_id': self.env.ref('zcl_invoice.cash_memo_invoice_form').id,
            'target': 'current'
        }


    # @api.onchange('order_line')
    # def _onchange_line_ids(self):
    #     serial_no = 1
    #     for line in self.order_line:
    #         line.serial_no = serial_no
    #         serial_no += 1
    #     gross_sum = 0
    #     qty_sum = 0
    #     stock_sum = 0
    #     sum_bottom_price = 0
    #     sum_net_value = 0
    #     sum_foc = 0
    #     for rec in self.order_line:
    #         gross_sum += rec.gross
    #         qty_sum += rec.product_uom_qty
    #         stock_sum += rec.stock_in_hand
    #         sum_bottom_price += rec.bottom_price
    #         sum_net_value += rec.net_value
    #         sum_foc += rec.discount_on_foc
    #     self.total_qty = qty_sum
    #     self.total_stock_in_hand = stock_sum
    #     self.total_gross = gross_sum
    #     self.total_bottom_price = sum_bottom_price
    #     self.total_net_value = sum_net_value
    #     self.total_disc_on_foc = sum_foc
    #     self.total_vat = float(self.total_net_value * 5/100)
    #     self.total_net = float(self.total_vat + self.total_net_value)


class SalesLine(models.Model):
    _inherit = "sale.order.line"

    serial_no = fields.Integer(string="Sl no", readonly=False, compute="_get_line_numbers")
    rate = fields.Float(string='Rate', digits=(16, 3))
    gross = fields.Float(string='Gross', digits=(16, 3), )
    sale_type = fields.Char(string='Sales Type')
    discount_on_foc = fields.Float('Discount On FOC', digits=(16, 3))
    stock_in_hand = fields.Integer('Stock In Hand')
    bottom_price = fields.Float(string='Bottom Price', digits=(16, 3), )
    net_value = fields.Float(string='Net Value', digits=(16, 3), )



    # @api.onchange('product_id')
    # def _find_data(self):
    #     self.rate = self.product_id.cntr_max_price
    #     self.bottom_price = self.product_id.cntr_min_price
    #     self.stock_in_hand = self.product_id.qty_available
    #     self.sale_type = 'Foc' if self.product_id.foc else None

    # @api.onchange('product_uom_qty', 'product_id')
    # def _calculate_gross(self):
    #     self.gross = float(self.rate * self.product_uom_qty)

    # @api.onchange('sale_type', 'product_id', 'gross')
    # def _net_value(self):
    #     if not self.sale_type:
    #         self.net_value = float(self.gross)
    #     else:
    #         self.net_value = None

    # @api.onchange('rate')
    # def _calculate_gross_rate(self):
    #     self.gross = float(self.rate * self.product_uom_qty)




