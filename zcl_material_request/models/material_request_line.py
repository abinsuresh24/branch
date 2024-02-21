from odoo import fields, models, api


class Shop(models.Model):
    _name = "material.request.line"
    _description = "Material Request line"

    serial_no = fields.Integer(string="Sl no")
    items_id = fields.Many2one('product.product', string="Items")
    description = fields.Char(related='items_id.name', string="Description")
    requested_to = fields.Many2one('stock.location', string="Requested To")
    qty = fields.Float(string="Quantity")
    mat_id = fields.Many2one('material.request', string='Request')
    state = fields.Selection([('sent','Sent'),('confirmed','Confirmed'),('validate','Validate')], string="Status")

    def action_request(self):
        stock_list = self.env['stock.quant'].search_read([('product_id', '=', self.items_id.id), ('location_id.name', '!=', 'Inventory adjustment')], ['location_id', 'quantity'])
        stock_list = [{'loc_id': rec['location_id'][0], 'quantity': rec['quantity']} for rec in stock_list]
        return {
            'name': 'Material',
            'type': 'ir.actions.act_window',
            'res_model': 'material.stock.wizard',
            'view_mode': 'form',
            'target': "new",
            'context': {'default_line_id': self.id, 'default_material_id': self.mat_id.id, 'default_items_id': self.items_id.id, 'default_material_stock_ids': stock_list}
        }

    # def action_request(self):
    #     stock_list=[]
    #     stock = self.env['stock.quant'].search([('product_id','=',self.items_id.id)])
    #     for rec in stock:
    #         dic ={
    #             'location_id':rec.location_id.id,
    #             'quantity':rec.quantity
    #         }
    #         stock_list.append(dic)
    #     print(stock_list)
    #     return {
    #         'name': 'Material',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'material.stock.wizard',
    #         'view_mode': 'form',
    #         'context': {'default_line_id': self.id,'default_material_stock_ids': [fields.Command.create(stock_list)]}
    #     }
