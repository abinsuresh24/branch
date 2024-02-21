# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Anoop Jayaprakash
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################


from odoo import models, api, _


class LocationInherits(models.Model):
    _inherit = "stock.location"
    _description = "Shop"

    @api.onchange('name')
    def _onchange_name(self):
        self.shop_location = True

    @api.model
    def create(self, vals):
        recordset = self.env['stock.location'].search([('id', '!=', False)], limit=1, order="id desc")
        previous_id = recordset.ids[0]
        if 'shop_location' in vals:
            if vals['shop_location']:
                customer_vals = {
                    'name': 'Walk-in Customer',
                    'id_card': 000,
                    'phone': 000,
                    'customer_true': True,
                    'walkin_customer': True,
                    'is_shop_customer': True,
                    'branch_id': vals.get('branch_id'),
                    'shop_id': int(previous_id+1),
                }
                customer = self.env['res.partner'].create(customer_vals)
                if vals.get('reference', _('New')) == _('New'):
                    vals['reference'] = self.env['ir.sequence'].next_by_code('zcl_shop.sequence_shop') or _('New')
                res = super(LocationInherits, self).create(vals)
                res.update({'location_id': self.env['stock.location'].sudo().search([('usage', '=', 'view'), ('warehouse_id', '=', int(self.env.ref('zcl_store.shop_warehouse').id))], limit=1), 'shop_location': True})
                self.invalidate_model(['warehouse_id'])
                return res
            else:
                return super(LocationInherits, self).create(vals)
        else:
            return super(LocationInherits, self).create(vals)

    def oh_hand_stock(self):
        return {
            'name': 'Store Stock',
            'view_mode': 'tree',
            'res_model': 'stock.quant',
            'domain': [('location_id.id', '=', self.id)],
            'res_id': self.id,
            # 'view_id': self.env.ref('zcl_shop.action_store_product_stock_form').id,
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
        }


class StockInherits(models.Model):
    _inherit = "stock.quant"

    @api.model
    def shop_store_stock_in_hand(self):
        return {
            'name': 'Stock in hand',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.quant',
            'view_mode': 'tree',
            'view_ids': [
                (5, 0, 0),
                (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('stock.view_stock_quant_tree')}),
            ],
            'domain': [('location_id', '=', self.env.user.branch_l_id.id)],

        }
