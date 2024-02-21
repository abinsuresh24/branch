# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Sayooj T K
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################


from odoo import api, fields, models, _


class MaterialRequest(models.Model):
    _inherit = "stock.picking"
    _description = "Damage stock"
    _order = 'id desc'

    damage_stock_out = fields.Boolean(string="damage stock Out", deault=False)
    damage_stock_in = fields.Boolean(string="damage stock in", deault=False)
    damage_stock_id = fields.Many2one('damage.stock', string="damage stock Out")
    damage_stock_state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft')

    def action_damage_approve(self):
        self.action_confirm()
        self.damage_stock_state = 'approve'
        self.damage_stock_id.state = 'approve'
        self.damage_stock_in = True

    def action_damage_reject(self):
        self.action_cancel()
        self.damage_stock_state = 'reject'
        self.damage_stock_id.state = 'reject'

