# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def default_get(self, default_fields):
        res = super(StockPicking, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id': self.env.user.branch_id.id or False
            })
        return res

    branch_id = fields.Many2one('res.branch', string="Branch")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            user = self.env.user
            if not vals.get('name') or vals['name'] == _('New'):
                if vals.get('direct_transfer') == True:
                    if user.branch_id.direct_transfer_out_prefix:
                        do_prefix = self.env['ir.sequence'].search(
                            [('code', '=', user.branch_id.direct_transfer_out_prefix)])
                        if do_prefix:
                            vals['name'] = self.env['ir.sequence'].next_by_code(
                                do_prefix.code) or _('New')
                elif vals.get('shop_transfer') == True:
                    if user.branch_id.stock_transfer_out_prefix:
                        prefix = self.env['ir.sequence'].search(
                            [('code', '=', user.branch_id.stock_transfer_out_prefix)])
                        if prefix:
                            vals['name'] = self.env['ir.sequence'].next_by_code(prefix.code) or _(
                                'New')
                elif vals.get('damage_stock_out') == True:
                    if user.branch_id.damage_stock_out_prefix:
                        prefix = self.env['ir.sequence'].search(
                            [('code', '=', user.branch_id.damage_stock_out_prefix)])
                        if prefix:
                            vals['name'] = self.env['ir.sequence'].next_by_code(prefix.code) or _(
                                'New')
                elif vals.get('damage_stock_in') == True:
                    if user.branch_id.damage_stock_in_prefix:
                        prefix = self.env['ir.sequence'].search(
                            [('code', '=', user.branch_id.damage_stock_in_prefix)])
                        if prefix:
                            vals['name'] = self.env['ir.sequence'].next_by_code(prefix.code) or _(
                                'New')
                else:
                    print("d")
        return super().create(vals_list)

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise UserError("Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.")