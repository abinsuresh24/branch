from odoo import fields, models, api, _


class Shop(models.Model):
    _name = "material.request"
    _description = "Material Request"

    name = fields.Char(string="Document No", default=lambda self: _('New'))
    branch_id = fields.Many2one('stock.location', string='Branch', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_l_id, store=True, readonly=True)
    date = fields.Date(string="Date", default=fields.date.today())
    state = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'),
                              ('cancel', 'Cancelled')],
                             default='draft')
    narration = fields.Text(string="Narration")
    store_materials = fields.Boolean(string="Store Materials")
    shop_materials = fields.Boolean(string="shop Materials")
    line_ids = fields.One2many('material.request.line', 'mat_id', string='Operations')
    sale_order_no = fields.Char(string="Sale Order No")

    @api.model
    def create(self, vals_list):
        """Declaring function for creating unique sequence number
        for each MR"""
        user = self.env.user
        if user.branch_id.material_requisition_prefix:
            if vals_list.get('name', 'New') == 'New':
                prefix = self.env['ir.sequence'].search(
                    [('code', '=', user.branch_id.material_requisition_prefix)])
                if prefix:
                    vals_list['name'] = self.env['ir.sequence'].next_by_code(
                        prefix.code) or _('New')
            result = super().create(vals_list)
            return result
        else:
            if vals_list.get('name', 'New') == 'New':
                vals_list['name'] = self.env['ir.sequence'].next_by_code(
                    'material.request.sequence') or 'New'
            result = super().create(vals_list)
            return result

    def confirm_button_action(self):
        user = self.env.user
        if self.store_materials:
            if user.branch_w_id.lot_stock_id:
                for rec in self.line_ids:
                    if rec.requested_to:
                        transfer = self.env['stock.picking.type'].search([('warehouse_id', '=', rec.requested_to.warehouse_id.id), ('code', '=', 'internal')])
                        self.env['stock.picking'].create({'picking_type_id': transfer.id, 'location_dest_id': user.branch_w_id.lot_stock_id.id,
                                                          'location_id': rec.requested_to.id, 'shop_mat_req': True, 'move_ids_without_package': [(0, 0, {
                                'name': rec.items_id.name,
                                'product_id': rec.items_id.id, 'location_id': rec.requested_to.id, 'location_dest_id': user.branch_w_id.lot_stock_id.id,
                                'product_uom_qty': rec.qty, 'reserved_availability': rec.qty, 'quantity_done': rec.qty, })], })
        if self.shop_materials:
            if user.branch_l_id:
                for rec in self.line_ids:
                    if rec.requested_to:
                        transfer = self.env['stock.picking.type'].search([('warehouse_id', '=', rec.requested_to.warehouse_id.id), ('code', '=', 'internal')])
                        self.env['stock.picking'].create({'picking_type_id': transfer.id, 'location_dest_id': user.branch_l_id.id,
                                                          'location_id': rec.requested_to.id, 'store_mat_req': True, 'move_ids_without_package': [(0, 0, {
                                'name': rec.items_id.name,
                                'product_id': rec.items_id.id, 'location_id': rec.requested_to.id, 'location_dest_id': user.branch_w_id.lot_stock_id.id,
                                'product_uom_qty': rec.qty, 'reserved_availability': rec.qty, 'quantity_done': rec.qty, })], })
        self.state = 'requested'

    @api.onchange('line_ids')
    def _onchange_line(self):
        serial_no = 1
        for line in self.line_ids:
            line.serial_no = serial_no
            serial_no += 1
