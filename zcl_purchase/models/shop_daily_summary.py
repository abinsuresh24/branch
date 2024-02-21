# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Manjima V
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################


from odoo import api, fields, models, _


class ShopSummary(models.Model):
    _name = 'shop.summary'
    _description = "Daily Shop Summary"
    _rec_name = "shops_name_id"

    company_id = fields.Char(string="Company", readonly=True)
    shops_name_id = fields.Many2one('stock.location', string="Shop Name", domain="[('shop_location','=',True)]")
    date = fields.Date(String="Date", default=fields.Date.today, readonly=True)
    cash_memo_summary_ids = fields. Many2many('sale.order','relation_table_cash_memo')
    internal_do_summary_ids = fields.Many2many('sale.order', 'relation_table_internal_do')
    project_do_summary_ids = fields.Many2many('sale.order','relation_table_project_do')
    direct_order_summary_ids = fields.Many2many('sale.order','relation_table_direct_order')
    cash_sale_summary_ids = fields.Many2many('sale.order','relation_table_cas_sale')

    @api.onchange('shops_name_id')
    def _onchange_shops_name_id(self):
        self.company_id = self.shops_name_id.company_id.name
        cash_memos = self.env['sale.order'].search(
            [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date','=',self.date),('cash_memo','=',True)]).ids
        print(cash_memos,"sdsssffdssdfsdfdsdfdsdf")
        if cash_memos:
            self.cash_memo_summary_ids = self.env['sale.order'].search(
            [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date','=',self.date),('cash_memo','=',True)]).ids
        else:
            self.cash_memo_summary_ids = False

        internal_do = self.env['sale.order'].search(
            [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('internal_direct_order','=', True)]).ids
        print(internal_do, "asddgggggggggggggggggg")
        if internal_do:
            self.internal_do_summary_ids = self.env['sale.order'].search(
                [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('internal_direct_order','=', True)]).ids
        else:
            self.internal_do_summary_ids = False

        project_do = self.env['sale.order'].search(
            [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('project_direct_order','=', True)]).ids
        print(project_do, "qqqqqqqqqqqqqqqqq")
        if project_do:
            self.project_do_summary_ids = self.env['sale.order'].search(
                [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('project_direct_order','=', True)]).ids
        else:
            self.project_do_summary_ids = False

        direct_order = self.env['sale.order'].search(
            [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('normal_do','=', True)]).ids
        print(cash_memos, "sdsssffdssdfsdfdsdfdsdf")
        if direct_order:
            self.direct_order_summary_ids = self.env['sale.order'].search(
                [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('normal_do','=', True)]).ids
        else:
            self.direct_order_summary_ids = False

        cash_sale = self.env['sale.order'].search(
            [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('cash_sale','=', True)]).ids
        print(cash_memos, "aaaaaaaaaaaaaaa")
        if cash_sale:
            self.cash_sale_summary_ids = self.env['sale.order'].search(
                [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('cash_sale','=', True)]).ids
        else:
            self.cash_sale_summary_ids = False






    # @api.onchange('shops_name_id')
    # def onchange_shops_name_id(self):
    #     self.company_id = self.shops_name_id.company_id.name
    #     cash_memos = self.env['sale.order'].search(
    #         [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date)])
    #     for order in cash_memos:
    #         if order.cash_memo:
    #             self.is_cash_memo = True
    #             print(cash_memos, "saaaaaaaaaaaaaa")
    #             print(self.shops_name_id.branch_id.name, "yuuutrrrrrrrerrr")
    #             print(self.cash_memo_summary_ids.branch_id.name, "yrrtfddgfdgdgd")
    #             if self.is_cash_memo:
    #                 cash_memo_lines = [(0, 0,
    #                                     {'customer': order.customer, 'branches_id': order.branches_id,
    #                                      'salesmen': order.salesmen,
    #                                      'sales_account': order.sales_account})]
    #                 self.cash_memo_summary_ids = cash_memo_lines



