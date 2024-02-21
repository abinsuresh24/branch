# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abin Suresh
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################
from odoo import fields, models, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = "Grn"

    user_warehouse_id = fields.Many2one('stock.location', default=lambda self: self.env.user.branch_w_id.lot_stock_id.id, store=True)
    user_location_id = fields.Many2one('stock.location', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_l_id, store=True)

    @api.model
    def action_store_grn_window(self):
        domain = [('location_dest_id.id', '=', self.env.user.branch_w_id.lot_stock_id.id)]
        action = {
            'name': 'GRN',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'view_ids': [
                (5, 0, 0),
                (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('zcl_grn.grn_pick_tree').id}),
                (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('zcl_grn.grn_pick_form').id}),
            ],
            'domain': domain,
        }
        return action

    @api.model
    def action_shop_grn_window(self):
        domain = [('location_dest_id.id', '=', self.env.user.branch_l_id.id)]
        action = {
            'name': 'GRN',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'view_ids': [
                (5, 0, 0),
                (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('zcl_grn.grn_pick_tree').id}),
                (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('zcl_grn.grn_pick_form').id}),
            ],
            'domain': domain,
        }
        return action
