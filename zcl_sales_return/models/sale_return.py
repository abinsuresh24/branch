# -- coding: utf-8 --
###################################################################################

# Author       :  Abdul Hakeem
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
############################################################

from odoo import fields, models, api, _
from odoo.tests import Form


class SalesReturn(models.Model):
    _inherit = "sale.order"

    name_return = fields.Char(string="Document No", default=lambda self: _('New'), readonly=True)
    sales_account_return = fields.Char(string='Sales Account')
    return_branch_id = fields.Many2one('stock.picking.type', string="Branch")
    return_inv_no = fields.Many2one('customer.invoice', string='INV NO', domain="[('partner_id', '=', partner_id),('state', '=', 'confirm')]")
    return_inv_date = fields.Date(string=" INV Date", default=fields.date.today())
    return_gsm_no = fields.Char(string='GSM No')
    total_round_off = fields.Float(string='Round Off', digits=(16, 3))
    total_gross = fields.Float(string='Gross', digits=(16, 3))
    # total_bottom_price = fields.Float(string='Bottom Price')
    # total_net_value = fields.Float(string='Net Value')
    # total_net = fields.Float(string='Net', )
    # total_disc_on_foc = fields.Float(string='Disc On Foc')
    sale_return = fields.Boolean("Sale Return", invisible=1, default=False)
    picking_count = fields.Integer(compute='_compute_picking_count', string="Transfer")
    debit_count = fields.Integer(compute='_compute_debit_count', string="Debit Note")
    state = fields.Selection(selection_add=[('return', 'Return')])
    search_name = fields.Many2many('product.product', string="Name")
    gt_sale_return = fields.Boolean("Sale Return", default=False)
    gt_cash_memo_return = fields.Boolean("Sale Return", default=False)
    cash_memo_partner_id = fields.Many2one('res.partner', string="customer", default=lambda self: self.env.ref('zcl_contacts.walkin_customer_data').id)
    customer_reference = fields.Char(string="Customer")
    sale_return_invoice_count = fields.Integer()
    sale_return_invoice_ids = fields.Many2one('account.move', string='Invoices')

    @api.onchange('customer_reference')
    def _onchange_customer_reference(self):
        if self.gt_cash_memo_return:
            self.partner_id = self.cash_memo_partner_id.id

    @api.onchange('return_inv_no')
    def _onchange_return_inv_no(self):
        products = self.env['product.product']
        for invoice in self.return_inv_no.customer_invoice_ids:
            products |= invoice.order_id.order_line.mapped('product_id')
        self.search_name = [(6, 0, products.ids)]

    @api.onchange('search_name')
    def _onchange_return_inv_no_lines(self):
        if self.partner_id:
            rec = self.env['customer.invoice'].sudo().search([('id', '=', self.return_inv_no.id)])
            if rec:
                self.order_line = [(5, 0, 0)]
                for res in rec.customer_invoice_ids:
                    if res.order_id:
                        for data in res.order_id.order_line:
                            if data.product_id.id in self.search_name.ids:
                                self.order_line = [fields.Command.create({'order_id': self.id,
                                                                          'product_id': data.product_id,
                                                                          'name': data.name,
                                                                          'price_unit': data.price_unit,
                                                                          'product_uom_qty': data.product_uom_qty,
                                                                          'rate': data.rate,
                                                                          'gross': data.gross,
                                                                          'sales_type': data.sales_type,
                                                                          'discount_on_foc': data.discount_on_foc,
                                                                          'net_value': data.net_value})]

    def action_return(self):
        returns = self.env['stock.picking.type'].search([('return_bool', '=', True)], limit=1)
        stock_picking = self.env['stock.picking'].create({
            'state': 'draft',
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'picking_type_id': returns.id,
            'move_ids_without_package': [{
                'product_id': rec.product_id,
                'location_id': returns.default_location_src_id,
                'location_dest_id': returns.default_location_dest_id,
                'name': "haiii"
            } for rec in self.order_line]
        })
        stock_picking_confirm = stock_picking.action_confirm()

        type=None
        if self.gt_sale_return:
            type = 'sale_return'
        if self.gt_cash_memo_return:
            type = 'cash_memo_return'
        invoice_date_value = fields.Date.today()
        invoice = self.env['account.move'].create(
            {'move_type': 'out_refund', 'partner_id': self.partner_id.id, 'invoice_origin': self.name,
             'invoice_type': type,
             'state': 'draft', 'invoice_date': invoice_date_value, 'gsm_no': self.return_gsm_no,
             'sales_account': self.sales_account, 'total_qty': self.total_qty, 'total_gross': self.total_gross,
             'total_bottom_price': self.total_bottom_price, 'total_disc_on_foc': self.total_disc_on_foc,
             'total_vat': self.total_vat, 'total_net_value': self.total_net_value, 'total_net': self.total_net,
             'total_round_off': self.total_round_off, 'ks_global_tax_rate': 5.0,
             })
        for rec in self.order_line:
            values = {
                'product_id': rec.product_id.id,
                'quantity': rec.product_uom_qty,
                'price_unit': 0 if rec.product_id.foc else rec.rate,
                'gross': rec.gross,
                'sale_type': rec.sale_type,
                'discount_on_foc': rec.discount_on_foc,
                'net_value': rec.net_value,
                'tax_ids': None,
                'move_id': invoice.id,
            }
            self.env['account.move.line'].create(values)

        invoice.amount_button()
        invoice.state = 'posted'
        self.write({'state': 'return'})

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
            self.sale_return_invoice_ids = invoice.id
            self.invoice_ids = invoice
            self.invoice_count = 1
            self.sale_return_invoice_count = 1

    @api.model
    def create(self, vals_list):
        """Declaring function for creating unique sequence number
        for each request"""
        if vals_list.get('name_return', 'New') == 'New':
            vals_list['name_return'] = self.env['ir.sequence'].next_by_code(
                'sales.return.sequence') or 'New'
        result = super().create(vals_list)
        return result


    def action_sale_return_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'move_type': 'out_invoice',
            'res_id': self.sale_return_invoice_ids.id,
            'view_id': self.env.ref('zcl_invoice.sale_return_invoice_form').id,
            'target': 'current'
        }


class SalesReturnLine(models.Model):
    _inherit = "sale.order.line"

    # serial_no = fields.Integer(string="Sl no")
    sale_return = fields.Boolean(related='order_id.sale_return', string="Sale Return")
    serial_no = fields.Integer(string="Sl no", readonly=False, compute="_get_line_numbers")
    rate = fields.Float(string='Rate')
    gross = fields.Float(string='Gross')
    sales_type = fields.Selection([('sale', 'Sale'), ('foc', 'FOC')], 'Sales Type', default='sale')
    stock_in_hand = fields.Char('Stock In Hand')
    check_box = fields.Boolean(string="   ", default=False)

    def _get_line_numbers(self):
        print("aaaaaaa")

    def open_return_wizard(self):
        product_list = []
        print("iddddddddddddd", self.order_id.partner_id.id)
        sale_order = self.env['sale.order'].search([('partner_id', '=', self.order_id.partner_id.id), ('state', '=', 'sale'), ('sale_return', '=', False)])
        print("sale_order", sale_order)
        for sale in sale_order:
            order_lines = self.env['sale.order.line'].search([('order_id', '=', sale.id), ('product_id', '=', self.product_id.id), ('product_uom_qty', '>=', self.product_uom_qty)])
            print("order_lines", order_lines)
            for line in order_lines:
                if not self.env['sale.return.wizard'].search(
                        [('sale_order', '=', sale.id), ('sale_order_line', '=', line.id),
                         ('sale_return_wizard_id', '=', self.id)]):
                    component = {
                        'sale_order': sale.id,
                        'sale_order_line': line.id,
                        'sale_return_wizard_id': self.id,
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'unit': line.product_uom_qty,
                    }
                    wizard_line = self.env['sale.return.wizard'].create(component)
                    print("wizard_linr", wizard_line)
            return {
                'name': 'Products',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.return.wizard',
                'view_mode': 'tree',
                'view_type': 'tree',
                'target': 'new',
                'domain': [('sale_return_wizard_id', '=', self.id)],
            }
