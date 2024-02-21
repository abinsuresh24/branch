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
from odoo.tests import Form


class DamageStock(models.Model):
    _name = 'damage.stock'
    _description = "Damage Stock"
    _rec_name = "name"
    _order = 'id desc'

    name = fields.Char(string="Document_no", readonly=True, default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('done', 'Confirmed'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft')
    branch = fields.Many2one('res.branch', default=lambda self: self.env.user.branch_id.id, string="Branch", readonly=True, store=True)
    narration = fields.Char(string="Narration")
    date = fields.Date(string="Date")
    transfer_from = fields.Many2one("stock.location", string="Transfer From",  default=lambda self: self.env.user.branch_l_id.id, readonly=True, store=True)
    transfer_to = fields.Many2one('stock.location', string="Transfer To", domain="[('usage', '=', 'inventory')]")
    line_ids = fields.One2many('damage.stock.line', 'item_id', string='Line ids')
    store_true = fields.Boolean(default=False)
    shop_true = fields.Boolean(default=False)



    @api.model
    def create(self, vals_list):
        if vals_list.get('name', 'New') == 'New':
            vals_list['name'] = self.env['ir.sequence'].next_by_code('damage.stock.sequence') or 'New'
        result = super().create(vals_list)
        return result

    def action_confirm(self):
        user = self.env.user
        if user.branch_w_id.lot_stock_id:
            if self.transfer_from:
                transfer = self.env['stock.picking.type'].search([
                    ('warehouse_id', '=', self.transfer_from.warehouse_id.id),
                    ('code', '=', 'internal')])
                picking = self.env['stock.picking'].create(
                    {'picking_type_id': transfer.id,
                     'location_dest_id': user.branch_w_id.lot_stock_id.id,
                     'location_id': self.transfer_to.id,
                     'damage_stock_out': True,
                     'branch_id': self.branch.id,
                     'damage_stock_id': self.id,
                     'move_ids_without_package': [{
                         'name': rec.item_id.name,
                         'product_id': rec.product_id.id,
                         'location_id': self.transfer_to.id,
                         'location_dest_id': user.branch_w_id.lot_stock_id.id,
                         'product_uom_qty': rec.qty}for rec in self.line_ids]})
        self.state = 'done'


    class DamageStock(models.Model):
        _name = 'damage.stock.line'
        _description = "Damage Stock Line"

        item_id = fields.Many2one('damage.stock')
        sno = fields.Integer(string="Sno")
        product_id = fields.Many2one('product.product', String='Item')
        description = fields.Char(String='Description')
        units = fields.Float(String='Units')
        qty = fields.Float(String='Quantity')
        remark = fields.Char(string="Remarks")

