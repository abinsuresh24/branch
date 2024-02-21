from odoo import fields, models, api, _


class MaterialRequest(models.Model):
    _inherit = "stock.picking"
    _description = "Material Request"

    shop_material_req_out = fields.Boolean(string="Shop Out")
    shop_mat_req = fields.Boolean(string="Shop Out")
    store_mat_req = fields.Boolean(string="Store Out")

