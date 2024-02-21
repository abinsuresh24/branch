# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Sayooj t k
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import api, fields, models


class PartnerInherit(models.Model):
    _inherit = 'res.users'

    make_shop_visible = fields.Boolean(string="User", compute='get_shop_user')
    make_store_visible = fields.Boolean(string="User", compute='get_store_user')
    branch_l_id = fields.Many2one('stock.location', string="Branch")
    branch_w_id = fields.Many2one('stock.warehouse', string="Branch")
    cash_memo_receivable_acc = fields.Many2one('account.account', string="Cash memo receivable account",
                                               domain="[('account_type', '=', 'asset_receivable')]")
    do_receivable_acc = fields.Many2one('account.account', string="DO receivable account",
                                        domain="[('account_type', '=', 'asset_receivable')]")
    cash_receipt_receivable_acc = fields.Many2one('account.account', string="Cash receipt receivable account",
                                                  domain="[('account_type', '=', 'asset_receivable')]")
    sale_return_payable_acc = fields.Many2one('account.account', string="Sale return payable account",
                                              domain="[('account_type', '=', 'liability_payable')]")
    tax_account_id = fields.Many2one('account.account',string="Tax Account Receivable",
                                     domain="[('name', '=', 'Tax Received')]")

    @api.depends('make_shop_visible')
    def get_shop_user(self, ):
        res_user = self.env['res.users'].search([('id', '=', self.id)])
        if res_user.has_group('zcl_contacts.group_for_shop'):
            self.make_shop_visible = False
        else:
            self.make_shop_visible = True

    @api.depends('make_store_visible')
    def get_store_user(self, ):
        res_user = self.env['res.users'].search([('id', '=', self.id)])
        if res_user.has_group('zcl_contacts.group_for_store'):
            self.make_store_visible = False
        else:
            self.make_store_visible = True
