# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Sayooj T K
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models, api, _
from odoo.tests import Form


class CustomerInvoiceWizard(models.Model):

    _name = "customer.invoice.wizard"
    _description = "Customer Invoice Wizard"

    cash_receipt_line = fields.Many2one('cash.receipt.line', string='wizard')
    line_amount = fields.Float(string='Line Amount',  store=True, digits=(16, 3))
    total_amount = fields.Float(string='Total Amount', digits=(16, 3), store=True, compute='_calculate_total', depends=['line_ids.payment_amount'])
    line_ids = fields.One2many('customer.invoice.wizard.line', 'items_id', string=' ')
    payment_done = fields.Boolean(default=False, string='Payment_done')


    def _calculate_total(self):
        total = sum(line.payment_amount for line in self.line_ids)
        self.write({'total_amount': total})

    @api.onchange('total_amount')
    def _validation_for_total_amount(self):
        if self.total_amount > self.line_amount:
            raise models.ValidationError(_('Amount cannot be greater than enter amount.'))


    def confirm_request(self):
        journal = self.env["account.journal"].sudo().search([('type', '=', 'cash')], limit=1)
        balance_amount = self.line_amount
        for rec in self.line_ids:
            if rec.payment_amount:
                return_form = Form(self.env["account.payment.register"].sudo().with_context(
                    active_ids=rec.invoice.ids,
                    active_model="account.move",
                    default_amount=rec.payment_amount,
                    default_journal_id=journal.id
                ))
                return_wizard = return_form.save()
                action = return_wizard._create_payments()
                balance_amount -= rec.payment_amount

        if balance_amount:
            payment = self.env['account.payment'].create({
                'payment_type': 'inbound',
                'partner_id': self.cash_receipt_line.customer.id,
                'amount': balance_amount,
                'date': fields.Date.today(),
                'journal_id': journal.id
            })
            if payment:
                payment.action_post()

        self.payment_done = True


class CustomerInvoiceWizardLine(models.Model):

    _name = "customer.invoice.wizard.line"
    _description = "Customer Invoice Wizard Line"

    sno = fields.Integer(string='Sno', readonly=True)
    invoice = fields.Many2one('account.move', string="Reference", readonly=True)
    amount_due = fields.Float(string='Amount due', readonly=True, digits=(16, 3))
    payment_amount = fields.Float(string='Payment amount', digits=(16, 3))
    items_id = fields.Many2one('customer.invoice.wizard', string="Items")

    @api.onchange('payment_amount')
    def _validation_for_amount(self):
        if self.payment_amount > self.amount_due:
            self.write({'payment_amount': 0.0})
            raise models.ValidationError(_('Amount cannot be greater than or equal to Amount Due.'))
        if self.payment_amount < 0:
            self.write({'payment_amount': 0.0})
            raise models.ValidationError(_('Amount must be greater than zero.'))
        if self.items_id.total_amount > self.items_id.total_amount:
            raise models.ValidationError(_('Amount cannot be greater than enter amount.'))


