# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abdul Hakeem T H
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import api, fields, models, _
from odoo.tests import Form


class BankReceipt(models.Model):
    _name = 'bank.receipt'
    _description = "Bank Receipt"
    _rec_name = "name"

    name = fields.Char(string="Name", readonly=True, default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('done', 'Confirmed'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft')
    cash_bank = fields.Many2one('account.account', string="Cash/Bank", default=lambda self: self.env.user.cash_receipt_receivable_acc.id, store=True, readonly=True,)
    cheque_no = fields.Char(string="Cheque No")
    manual_no = fields.Char(string="Manual No")
    branch_id = fields.Many2one('res.branch', string='Branch', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_id, store=True, readonly=True)
    narration = fields.Char(string="Narration")
    net = fields.Float(string="Net", digits=(16, 3))
    omani_riyal = fields.Float(string="Omani riyal", digits=(16, 3))
    line_ids = fields.One2many('bank.receipt.line', 'item_id', string='Line ids')

    @api.model
    def create(self, vals_list):
        if vals_list.get('name', 'New') == 'New':
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'bank.receipt.sequence') or 'New'
        result = super().create(vals_list)
        return result

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        sno = 1
        for line in self.line_ids:
            line.sno = sno
            sno += 1
        net = 0
        for rec in self.line_ids:
            net += rec.amount
        self.net = net

    def bank_receipt_confirm(self):
        # journal = self.env["account.journal"].sudo().search([('type', '=', 'cash')], limit=1)
        # line_ids = None
        # for rec in self.line_ids.reference:
        #     line_ids = rec.invoice_line_ids
        # if self.line_ids:
        #     for rec in self.line_ids:
        #         if not rec.reference:
        #             payment = self.env['account.payment'].create({
        #                 'payment_type': 'inbound',
        #                 'partner_id': rec.customer.id,
        #                 'amount': rec.amount,
        #                 'date': fields.Date.today(),
        #                 'journal_id': journal.id
        #
        #             })
        #             if payment:
        #                 payment.action_post()
        #         else:
        #             return_form = Form(self.env["account.payment.register"].sudo().with_context(
        #                 active_ids=rec.reference.ids,
        #                 active_model="account.move",
        #                 default_amount=rec.amount,
        #                 default_journal_id=journal.id
        #
        #             ))
        #
        #             return_wizard = return_form.save()
        #             action = return_wizard._create_payments()

        self.state = 'done'

    def action_finance_approve(self):
        self.state = 'approve'

    def action_finance_reject(self):
        self.state = 'reject'

class BankhReceiptLine(models.Model):
    _name = 'bank.receipt.line'
    _description = "Bank Receipt Line"

    item_id = fields.Many2one('bank.receipt',)
    sno = fields.Integer(string="Sno")
    customer = fields.Many2one('res.partner', string="Customer", domain="[('customer_true', '=', True)]")
    amount = fields.Float(string="Amount", digits=(16, 3),default=0)
    reference = fields.Many2one('account.move', string="Reference",
                                domain="[('partner_id', '=', customer), ('state', '=', 'posted'), ('move_type', '=', 'out_invoice'), ('payment_state', '!=', 'paid')]",
                                context={'default_partner_id': 'customer', 'state': 'posted', 'move_type': 'out_invoice'})
    remark = fields.Char(string="Remarks")

    @api.onchange('customer')
    def _onchange_customer(self):
        self.reference = False


    def open_invoice_wizard(self):
        print("qqqqqqqqqqqqqqqqqqqqqqq")
        reference_wizard_data = self.env['bank.customer.invoice.wizard']
        reference_wizard_payment_panding = self.env['bank.customer.invoice.wizard'].search([('bank_receipt_line.id', '=', self.id), ('payment_done', '=', False)]).unlink()
        reference_wizard_payment_done = self.env['bank.customer.invoice.wizard'].search([('bank_receipt_line.id', '=', self.id), ('payment_done', '=', True)])
        if not reference_wizard_payment_done:
            posted_invoices = self.env['account.move'].search([
                ('partner_id.id', '=', self.customer.id),
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '!=', 'paid')
            ])
            print("posted_invoices",posted_invoices )
            if posted_invoices:
                print("posted_invoices", posted_invoices)
                line_ids = [(0, 0, {'sno': index + 1, 'invoice': rec.id, 'amount_due': rec.amount_residual}) for index, rec in enumerate(posted_invoices)]

                reference_data = {
                    'bank_receipt_line': self.id,
                    'line_amount': self.amount,
                    'total_amount': self.amount,
                    'line_ids': line_ids,
                }
                reference_wizard_data = self.env['bank.customer.invoice.wizard'].sudo().create(reference_data)

            return {
                'name': 'Invoice Reference',
                'type': 'ir.actions.act_window',
                'res_model': 'bank.customer.invoice.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'res_id': reference_wizard_data.id,
                'domain': [('bank_receipt_line', '=', self.id)],
            }

        else:
            return {
                'name': 'Invoice Reference',
                'type': 'ir.actions.act_window',
                'res_model': 'bank.customer.invoice.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'res_id': reference_wizard_payment_done.id,
                'domain': [('bank_receipt_line', '=', self.id)],
            }
