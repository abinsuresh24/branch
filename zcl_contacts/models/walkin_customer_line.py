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


class WalkinCustomerLine(models.Model):
    _name = 'walkin.customer.line'
    _description = "walkin customer details"
    _rec_name = "phone"

    name = fields.Char(string="Name", required=True)
    phone = fields.Char(string="Phone", required=True)
    address = fields.Char(string="Address")
    vat_no = fields.Char(string="VAT No")
    partner_id = fields.Many2one('res.partner',)
    branch_id = fields.Many2one('stock.location', string="Branch", store=True)

    # branch_id = fields.Many2one('stock.location', string="Branch", default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_l_id, store=True)

    _sql_constraints = [
        ('phone_uniq', 'unique (phone)', """Phone number need to unique"""),
    ]
