from odoo import fields, models, api, _




class ShopTransfer(models.Model):
    _name = "shop.transfer"
    _description = "Shop Transfer"
    _order = 'reference desc'
    _rec_name = 'reference'


# ref

    reference = fields.Char(readonly=True, copy=False, default=lambda self: _('New'))
    branch_id = fields.Many2one('res.branch', string="Branch", default=lambda self: self.env.user.branch_id.id)
    requested_to = fields.Many2one('stock.location', domain="[('usage', '=', 'internal')]", string="Requested To")
    date = fields.Date(string='Date', default=fields.Date.today())
    narration = fields.Char("Narration")
    order_lines = fields.One2many('shop.transfer.line', 'shop_transfer_id', string='Order Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
    ], string='Status', default='draft', track_visibility='onchange')
    location_dest_id = fields.Many2one('stock.picking', string="Transfer To")
    location_id = fields.Many2one('stock.location', default=lambda self: self.env.user.branch_l_id.id, store=True, readonly=True, string="Requested From")

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('shop.transfer') or _('New')
        res = super(ShopTransfer, self).create(vals)
        return res

    def action_confirm(self):
        user = self.env.user
        if user.branch_l_id:
            warehouse = self.env['stock.picking.type'].search(
                [('warehouse_id', '=', self.requested_to.warehouse_id.id), ('code', '=', 'internal')])
            transfer = self.env['stock.picking'].create(
                {'location_dest_id': user.branch_l_id.id, 'location_id': self.requested_to.id,
                 'picking_type_id': warehouse.id, 'shop_transfer': True,
                 'move_ids_without_package': [{'name': rec.items_id.name,
                                               'product_id': rec.items_id.id,
                                               'product_uom_qty': rec.qty,
                                               'reserved_availability': rec.qty,
                                               'quantity_done': rec.qty,
                                               'location_id': self.requested_to.id,
                                               'location_dest_id': user.branch_l_id.id} for rec in self.order_lines]})
            self.state = 'requested'


# if self.shop_materials:
#     if user.branch_l_id:
#         for rec in self.line_ids:
#             if rec.requested_to:
#                 transfer = self.env['stock.picking.type'].search([('warehouse_id', '=', rec.requested_to.warehouse_id.id), ('code', '=', 'internal')])
#                 self.env['stock.picking'].create({'picking_type_id': transfer.id, 'location_dest_id': user.branch_l_id.id,
#                                                   'location_id': rec.requested_to.id, 'store_mat_req': True, 'move_ids_without_package': [(0, 0, {
#                         'name': rec.items_id.name,
#                         'product_id': rec.items_id.id,'location_id':rec.requested_to.id,'location_dest_id': user.branch_w_id.lot_stock_id.id,
#                         'product_uom_qty': rec.qty, })], })
# self.state = 'requested'

    @api.model
    def shop_transfer_action_python(self):
       domain = [
           ('branch_id', 'in', self.env.user.branch_ids.ids),
       ]

       action = {
           'name': 'Shop Transfer',
           'type': 'ir.actions.act_window',
           'res_model': 'shop.transfer',
           'view_mode': 'tree,form',
           'view_ids': [
               (5, 0, 0),
               (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('zcl_shop.shop_transfer_tree').id}),
               (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('zcl_shop.view_shop_transfer_form').id}),
           ],
           'context': {},
           'domain': domain,
       }
       return action







class ShopTransferLine(models.Model):
    _name = "shop.transfer.line"
    _description = "Shop Transfer line"

    serial_no = fields.Integer(string="Sl no" ,default=1)
    items_id = fields.Many2one('product.product',string="Items")
    description = fields.Char(related='items_id.name', string="Description")
    # requested_to = fields.Many2one('stock.location', string="Requested To")
    units =fields.Float(string='Units')
    qty = fields.Float(string="Quantity")
    shop_transfer_id = fields.Many2one('shop.transfer', string='Shop Transfer')
    link_1 = fields.Char(string="Link_1")

    @api.model
    def create(self, values):
        if not values.get('serial_no'):
            last_record = self.search([], order='serial_no desc', limit=1)
            values['serial_no'] = last_record.serial_no + 1 if last_record else 1
        return super(ShopTransferLine, self).create(values)

