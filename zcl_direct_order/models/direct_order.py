# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abin Suresh
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class DirectOrder(models.Model):
    _inherit = 'sale.order'

    def _domain_partner_ids(self):
        domain = [('customer_true', '=', True), ('id', '!=', int(self.env.ref('zcl_contacts.walkin_customer_data').id))]
        return domain

    def _domain_sale_quotation_id(self):
        domain = [('partner_id', '!=', int(self.env.ref('zcl_contacts.walkin_customer_data').id)), ('state', '=', 'sale')]
        return domain

    narration = fields.Html(string="Narration")
    available_balance = fields.Float(string="Available Balance", digits=(16, 3))
    branches_id = fields.Many2one('stock.location', string="Branch", default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_l_id, store=True)
    salesman_id = fields.Many2one('res.partner', string="Salesman", domain="[('sales_man_true', '=', True)]")
    partner_id = fields.Many2one('res.partner', string="Customer", domain=lambda self: self._domain_partner_ids(), required=True)
    gsm_no = fields.Char(string="GSM No")
    customer_no = fields.Char(string="Customer ID")
    over_due_amt = fields.Float(string="Over Due amt", digits=(16, 3))
    sale_quotation_id = fields.Many2one('sale.quotation', string="Quotation", domain=lambda self: self._domain_sale_quotation_id())
    total_quantity = fields.Float(string="Quantity")
    total_net_value = fields.Float(string="Net Value", digits=(16, 3))
    other_charge = fields.Float(string="Other Charge", digits=(16, 3))
    total_gross = fields.Float(string="Gross", digits=(16, 3))
    total_disc_foc = fields.Float(string="Discount on FOC", digits=(16, 3))
    overall_disc = fields.Float(string="Overall Disc", digits=(16, 3))
    disc_percentage = fields.Float(string="Discount %", digits=(16, 3))
    total_bottom_price = fields.Float(string="Bottom price", digits=(16, 3))
    total_vat = fields.Float(string="VAT 5%", digits=(16, 3))
    discount_amount = fields.Float(string="Discount Amt", digits=(16, 3))
    net_amount = fields.Float(string="Net Amt", digits=(16, 3))
    normal_do = fields.Boolean(string="DO")
    internal_direct_order = fields.Boolean(string="Internal DO")
    project_direct_order = fields.Boolean(string="Project DO")
    do_customer_id = fields.Many2one('res.partner', string="Customer", domain="[('do_type','=','do'),('state','=','done')]")
    internal_do_customer_id = fields.Many2one('res.partner', string="Customer", domain="[('do_type','=','internal_do')]")
    project_do_customer_id = fields.Many2one('res.partner', string="Customer", domain="[('do_type','=','project_do')]")
    cash_sale = fields.Boolean(string="Cash Sale")
    cash_sale_customer_id = fields.Many2one('res.partner', string="Customer")
    sale_total_amount = fields.Float(string="Total Amount", digits=(16, 3))
    need_approval = fields.Boolean()
    cash_sale_invoice_count = fields.Integer()
    cash_sale_invoice_ids = fields.Many2one('account.move', string='Invoices')
    sequence_number = fields.Char(string="Sequence No")
    warehouse_sale = fields.Boolean(string="Warehouse Sale")
    wh_customer_id = fields.Many2one('res.partner', string="Customer", domain="[('customer_true','=', True),('state','=','done')]")

    @api.onchange('do_customer_id')
    def _onchange_do_customer(self):
        self.partner_id = self.do_customer_id.id
        self.available_balance = self.partner_id.customer_credit_limit

    @api.onchange('internal_do_customer_id')
    def _onchange_internal_do_customer(self):
        self.partner_id = self.internal_do_customer_id.id
        self.available_balance = self.partner_id.customer_credit_limit

    @api.onchange('project_do_customer_id')
    def _onchange_project_do_customer(self):
        self.partner_id = self.project_do_customer_id.id
        self.available_balance = self.partner_id.customer_credit_limit

    @api.onchange('cash_sale_customer_id')
    def _onchange_cash_sale_customer(self):
        self.partner_id = self.cash_sale_customer_id.id
        self.available_balance = self.partner_id.customer_credit_limit

    @api.onchange('wh_customer_id')
    def _onchange_cash_sale_customer(self):
        self.partner_id = self.wh_customer_id.id
        self.available_balance = self.partner_id.customer_credit_limit

    @api.onchange('sale_quotation_id')
    def _onchange_sale_quotation(self):
        if self.sale_quotation_id:
            self.partner_id = self.sale_quotation_id.partner_id
            self.branches_id = self.sale_quotation_id.branch_id
            self.salesman_id = self.sale_quotation_id.sales_man_id
            self.order_line = [(5, 0, 0)]
            for res in self.sale_quotation_id.line_ids:
                self.order_line = [fields.Command.create({'product_id': res.item_id.id, 'units': res.units, 'qty': res.qty, 'product_uom_qty': res.qty,
                                                          'rate': res.rate, 'gross': res.gross, 'sale_type': res.sale_type,
                                                          'discount_on_foc': res.discount_on_foc, 'bottom_price': res.bottom_price,
                                                          'net_value': res.net_value, "stock_in_hand": res.stock_in_hand})]

    @api.onchange('order_line')
    def _onchange_line_id(self):
        for line in self.order_line:
            if self.normal_do:
                line.price_unit = line.product_id.cntr_max_price
                line.bottom_price = line.product_id.cntr_min_price
                line.stock_in_hand = line.product_id.qty_available
                if line.rate < line.product_id.cntr_max_price:
                    line.discounts = -(line.product_id.cntr_max_price - line.rate)
                else:
                    line.discounts = 0
            if self.internal_direct_order:
                line.bottom_price = line.product_id.cntr_min_price
                line.price_unit = line.product_id.traders_price
                line.stock_in_hand = line.product_id.qty_available
                if line.rate < line.product_id.traders_price:
                    line.discounts = -(line.product_id.traders_price - line.rate)
                else:
                    line.discounts = 0
            if self.project_direct_order:
                line.bottom_price = line.product_id.cntr_min_price
                line.stock_in_hand = line.product_id.qty_available
                line.price_unit = line.product_id.project_price
                if line.rate < line.product_id.project_price:
                    line.discounts = -(line.product_id.project_price - line.rate)
                else:
                    line.discounts = 0
            if self.cash_sale:
                if line.product_id.cash_sale_count:
                    if line.product_uom_qty > line.product_id.cash_sale_count:
                        raise ValidationError("The product "+str(line.product_id.name)+ " have only " +str(line.product_id.cash_sale_count)+" quantity in stock")
                    line.price_unit = line.product_id.cash_sale_price
                    line.bottom_price = line.product_id.cntr_min_price
                    line.stock_in_hand = line.product_id.qty_available
                    if line.rate < line.product_id.cash_sale_price:
                        line.discounts = -(line.product_id.cash_sale_price - line.rate)
                    else:
                        line.discounts = 0
                else:
                    raise ValidationError(line.product_id.name + " have 0 quantity in the stock")

    def action_confirm_do(self):
        if self.total_net < self.available_balance:
            self.sale_types = 'do'
            rec = self.action_confirm()
            self.sale_total_amount = self.total_net
            if rec:
                self.partner_id.customer_credit_limit -= self.total_net
                for order in self.order_line:
                    if order.rate < order.bottom_price:
                        if self.need_approval != True:
                            raise ValidationError("Rate must be greater than Bottom price")
                if self.picking_ids:
                    for rec in self.picking_ids:
                        rec.location_id = self.env.user.branch_l_id.id
                        for res in rec.move_ids:
                            res.quantity_done = res.product_uom_qty
                        rec.button_validate()
                if not self.invoice_ids:
                    if self.cash_sale == True:
                        invoice_date_value = fields.Date.today()
                        invoice = self.env['account.move'].create(
                            {'move_type': 'out_invoice', 'partner_id': self.cash_sale_customer_id.id, 'invoice_origin': self.name,
                             'invoice_type': 'cash_sale',
                             'state': 'draft', 'invoice_date': invoice_date_value, 'gsm_no': self.gsm_no,
                             'salesmen': self.salesman_id,'total_qty': self.total_qty, 'total_gross': self.total_gross,
                             'total_bottom_price': self.total_bottom_price, 'total_disc_on_foc': self.total_disc_on_foc,
                             'total_vat': self.total_vat, 'total_net_value': self.total_net_value, 'total_net': self.total_net,
                             'total_round_off': self.total_round_off, 'ks_global_tax_rate': 5.0, 'discount_amount': self.discount_amount,
                             })
                        for rec in self.order_line:
                            values = {
                                'product_id': rec.product_id.id,
                                'quantity': rec.product_uom_qty,
                                'price_unit': 0 if rec.product_id.foc else rec.rate,
                                'gross': rec.gross,
                                'discounts': rec.discounts,
                                'sale_type': rec.sale_type,
                                'discount_on_foc': rec.discount_on_foc,
                                'net_value': rec.net_value,
                                'bottom_price': rec.bottom_price,
                                'tax_ids': None,
                                'move_id': invoice.id,
                            }
                            self.env['account.move.line'].create(values)

                        invoice.amount_button()
                        invoice.state = 'posted'
                        print('invoiceinvoiceinvoiceinvoice',invoice)
                        if invoice:
                            self.cash_sale_invoice_ids = invoice.id
                            self.invoice_ids = invoice
                            self.invoice_count = 1
                            self.cash_sale_invoice_count = 1
                    else:
                        self._create_invoices()
                        print("test")
                if self.project_direct_order:
                    self.invoice_ids.project_do = True
            if self.cash_sale:
                for rec in self.order_line:
                    rec.product_id.cash_sale_count -= rec.product_uom_qty
        else:
            raise ValidationError("The net amount exceeds the customer's credit limit of" + str(self.available_balance))

    def action_send_to_purchase(self):
        self.need_approval = True

    def action_cash_sale_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'move_type': 'out_invoice',
            'res_id': self.cash_sale_invoice_ids.id,
            'view_id': self.env.ref('zcl_invoice.cash_sale_invoice_form').id,
            'target': 'current'
        }

    def action_view_invoice(self):
        if not self.project_direct_order:
            invoices = self.mapped('invoice_ids')
            action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
            if len(invoices) > 1:
                action['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                form_view = [(self.env.ref('account.view_move_form').id, 'form')]
                if 'views' in action:
                    action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
                else:
                    action['views'] = form_view
                action['res_id'] = invoices.id
            else:
                action = {'type': 'ir.actions.act_window_close'}

            context = {
                'default_move_type': 'out_invoice',
            }
            if len(self) == 1:
                context.update({
                    'default_partner_id': self.partner_id.id,
                    'default_partner_shipping_id': self.partner_shipping_id.id,
                    'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                    'default_invoice_origin': self.name,
                })
            action['context'] = context
            return action


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_unit_of_measure = fields.Char(string="Units")
    discounts = fields.Float(string="Discount", default=0, digits=(16, 3))


class AccountMove(models.Model):
    _inherit = "account.move"

    project_do = fields.Boolean(string="Project DO")
