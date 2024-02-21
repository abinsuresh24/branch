# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abin Suresh
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models
from odoo.exceptions import ValidationError


class SalesmanIncentive(models.Model):
    _name = 'salesman.incentive'
    _description = "Incentive"

    name = fields.Char(string="Name", required=True)
    branch_id = fields.Many2one('res.branch', string='Branch',
                                default=lambda self: self.env.user.branch_id.id)
    amount = fields.Float(string="Amount", required=True, digits=(16, 3))
    showroom_incharge = fields.Float(string="Showroom Incharge Amount", digits=(16, 3))
    assistant_amount = fields.Float(string="Assistant Amount", digits=(16, 3))
    salesman_amount = fields.Float(string="Salesman Amount", digits=(16, 3))
    amount_achieved = fields.Float(string="Amount Achieved", digits=(16, 3))
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)

    def action_compute_incentive(self):
        if self.branch_id:
            if self.date_from and self.date_to:
                total_sale_amt = 0
                total_payment_amt = 0
                sales = self.env['sale.order'].search(
                    [('state', '=', 'sale'), ('branch_id', '=', self.branch_id.id),
                     ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])
                print(sales, "sales")
                for rec in sales:
                    total_sale_amt += rec.amount_total
                payments = self.env['account.payment'].search(
                    [('partner_type', '=', 'customer'), ('branch_id', '=', self.branch_id.id), ('is_internal_transfer', '=', False),
                     ('state', '=', 'posted')])
                for rec in payments:
                    total_payment_amt += rec.amount_company_currency_signed
                if total_sale_amt > self.amount:
                    if total_payment_amt > self.amount:
                        self.amount_achieved = total_payment_amt
                        balance = total_payment_amt - self.amount
                        percentage_achieved = (balance / self.amount) * 100
                        if percentage_achieved > 10:
                            multiple = int(percentage_achieved / 10) + 1
                            self.showroom_incharge = self.showroom_incharge * multiple
                            self.assistant_amount = self.assistant_amount * multiple
                            self.salesman_amount = self.salesman_amount * multiple
                            salesman = self.env['res.partner'].search([('sales_man_true','=',True)])
                            for rec in salesman:
                                if rec.sales_man_type == 'showroom':
                                    rec.incentive_amount = self.showroom_incharge
                                elif rec.sales_man_type == 'assistant':
                                    rec.incentive_amount = self.assistant_amount
                                elif rec.sales_man_type == 'normal':
                                    rec.incentive_amount = self.salesman_amount
                                else:
                                    rec.incentive_amount = 0
                    else:
                        raise ValidationError('Total payment is less than incentive amount')
                else:
                    raise ValidationError('Total sale amount is less than incentive amount')
