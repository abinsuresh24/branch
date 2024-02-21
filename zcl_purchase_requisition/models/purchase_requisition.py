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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _description = "Purchase Requisition"
    _rec_name = "name"

    name = fields.Char(string="Document_no", readonly=True, default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('done', 'Confirmed')], default='draft')
    branch = fields.Many2one('stock.location', string='Branch location', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_l_id, store=True)
    branch_id = fields.Many2one('res.branch', string='Branch', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_id, store=True, readonly=True)
    narration = fields.Char(string="Narration")
    date = fields.Date(string="Date")
    line_ids = fields.One2many('purchase.requisition.line', 'item_id', string='Line ids')
    shop_true = fields.Boolean(default=False)
    store_true = fields.Boolean(default=False)

    @api.model
    def create(self, vals_list):
        """Declaring function for creating unique sequence number
        for each PR"""
        user = self.env.user
        if user.branch_id.purchase_requisition_prefix:
            if vals_list.get('name', 'New') == 'New':
                prefix = self.env['ir.sequence'].search(
                    [('code', '=', user.branch_id.purchase_requisition_prefix)])
                if prefix:
                    vals_list['name'] = self.env['ir.sequence'].next_by_code(
                        prefix.code) or _('New')
            result = super().create(vals_list)
            return result
        else:
            if vals_list.get('name', 'New') == 'New':
                vals_list['name'] = self.env['ir.sequence'].next_by_code(
                    'purchase.requisition.sequence') or 'New'
            result = super().create(vals_list)
            return result

    def action_confirm(self):
        if self.line_ids:
            for rec in self.line_ids:
                if rec.product_id and rec.item_id.branch:
                    stock = self.env['stock.quant'].search([('product_id', '=', rec.product_id.id),
                                                            ('location_id', '=', rec.item_id.branch.id)], limit=1)
                    if stock:
                        rec.available_qty = float(stock.available_quantity)
                    else:
                        rec.available_qty = 0

        self.state = 'done'

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        sno = 1
        for line in self.line_ids:
            line.sno = sno
            sno += 1


    class PurchaseRequisitiontLine(models.Model):
        _name = 'purchase.requisition.line'
        _description = "Purchase Requisition Line"

        item_id = fields.Many2one('purchase.requisition')
        sno = fields.Integer(string="Sno")
        product_id = fields.Many2one('product.product', string='item')
        description = fields.Char(string="Description")
        units = fields.Float(string="Units")
        qty = fields.Float(string="Quantity")
        available_qty = fields.Float(string="Available Quantity", store=True)



        def open_return_wizard(self):
            # three_months_ago = datetime.now() - relativedelta(months=3)
            # three_months_ago_str = three_months_ago.strftime('%Y-%m-%d')
            stock_moves_wizard = self.env['product.moves.wizard']
            stock_moves_wizard.search([('requisition_line_id.id', '=', self.id)]).unlink()

            product_moves = self.env['stock.move'].search([
                ('product_id.id', '=', self.product_id.id),
                ('state', '=', 'done'),
                '|',
                ('location_id.id', '=', self.item_id.branch.id),
                ('location_dest_id.id', '=', self.item_id.branch.id)
            ])

            stock = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                    ('location_id', '=', self.item_id.branch.id)], limit=1)

            stock_moves_data = [{
                'requisition_line_id': self.id,
                'product_id': move.product_id.id,
                'qty': move.product_uom_qty,
                'date': str(move.date),
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
                'available_qty': float(stock.available_quantity)
            } for move in product_moves]

            stock_moves_wizard.sudo().create(stock_moves_data)

            return {
                'name': 'Products Moves',
                'type': 'ir.actions.act_window',
                'res_model': 'product.moves.wizard',
                'view_mode': 'tree',
                'view_type': 'tree',
                'target': 'new',
                'domain': [('requisition_line_id', '=', self.id)],
            }