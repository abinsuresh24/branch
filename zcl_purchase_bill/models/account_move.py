# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Sayooj T K
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_import = fields.Boolean(string="Purchase Import")
    purchase_local = fields.Boolean(string="Purchase Local")
    project_do = fields.Boolean(string="Project DO")

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.project_do:
            sale_order = self.env['sale.order'].search([('invoice_ids.id', '=', self.id)])
            if sale_order:
                sale_order.state = 'invoiced'
        return res
