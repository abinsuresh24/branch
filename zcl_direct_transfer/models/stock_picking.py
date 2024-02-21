# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Anoop Jayaprakash
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################


from odoo import fields, models, api, _


class Store(models.Model):
    _inherit = "stock.picking"
    _description = "Transfer"

    checked = fields.Boolean(default=False)
    sto_no = fields.Char(string="STO No")
    direct_from_warehouse_id = fields.Many2one('stock.warehouse')
    direct_to_warehouse_id = fields.Many2one('stock.warehouse')
    direct_transfer = fields.Boolean(string="Direct Transfer")

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for val in vals_list:
    #         if val.get('direct_transfer', False):
    #             move_ids_without_package = val.get('move_ids_without_package')
    #             if move_ids_without_package and move_ids_without_package[0][2]:
    #                 move_ids_without_package[0][2]['quantity_done'] = \
    #                     move_ids_without_package[0][2]['product_uom_qty']
    #     return super().create(vals_list)

    def confirm_action_store(self):
        print("k")
    #     self.transfer_type = 'store_store'
    #     self.checked = True
    #     self.action_confirm()
    #     if not self.show_check_availability:
    #         self.state = 'to_approve'
    #         self.store_store_transfer_type = 'store_store_in'
    #
    # def confirm_action_shop(self):
    #     self.transfer_type = 'store_shop'
    #     self.checked = True
    #     self.action_confirm()
    #     if not self.show_check_availability:
    #         self.button_validate()

    # def confirm_action_shop_store(self):
    #     self.transfer_type = 'shop_store_rqst'
    #     self.checked = True
    #     self.action_confirm()
    #     if not self.show_check_availability:
    #         self.state = 'to_approve'
    #         self.store_shop_transfer_type = 'shop_store_rqst'
    #
    # def action_confirm(self):
    #     if not self.checked:
    #         self.transfer_type = 'store_store_direct'
    #     return super().action_confirm()
