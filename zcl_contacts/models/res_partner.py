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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    verified_notverified = fields.Boolean(string="Verified", default=False, store=True)
    customer_true = fields.Boolean(string="Customer")
    vendor_true = fields.Boolean(string="Vendor")
    sales_man_true = fields.Boolean(string="Sales Man")
    walkin_customer = fields.Boolean(string="Walk-in Customer")
    walkin_customer_ids = fields.One2many('walkin.customer.line', 'partner_id', string="Walk-in customer")
    id_card = fields.Char(string="ID Card", required=True)
    phone = fields.Char(required=True)
    cr_no = fields.Char(string="CR No", required=True)
    payment_details = fields.Many2one('payments.terms')
    customer_credit_limit = fields.Float(string="Credit Limit")
    credit_limit_days = fields.Integer(string="Customer Days Notification")
    user_id = fields.Many2one('res.users', string="User")
    # cash_memo_receivable_acc = fields.Many2one('account.account', string="Cash memo receivable account", domain="[('account_type', '=', 'asset_receivable')]")
    # do_receivable_acc = fields.Many2one('account.account', string="DO receivable account", domain="[('account_type', '=', 'asset_receivable')]")
    # cash_receipt_receivable_acc = fields.Many2one('account.account', string="Cash receipt receivable account", domain="[('account_type', '=', 'asset_receivable')]")
    # sale_return_payable_acc = fields.Many2one('account.account', string="Sale return payable account", domain="[('account_type', '=', 'liability_payable')]")
    do_type = fields.Selection([('do', 'Direct Order'), ('internal_do', 'Internal DO'), ('project_do', 'Project DO')], default='do', string="DO Type")
    sales_man_type = fields.Selection([('normal', 'Normal Salesperson'), ('assistant', 'Assistant Sales person'), ('showroom', 'Showroom In charge')], default='normal', string="Sales Man Type")


    @api.depends('user_id')
    def _compute_used_user_ids(self):
        for partner in self:
            partner.used_user_ids = partner.user_id and [(6, 0, [partner.user_id.id])] or [(5,)]

    @api.constrains('user_id')
    def _check_unique_user_per_partner(self):
        for partner in self:
            if partner.user_id:
                partner_with_same_user = self.search([
                    ('id', '!=', partner.id),
                    ('user_id', '=', partner.user_id.id)
                ])
                if partner_with_same_user:
                    raise ValidationError(
                        "This user is already assigned to another sale person. Please choose a different user.")
