from odoo import fields, models


class Stocks(models.Model):
    _inherit = "stock.move"
    _description = "Transfer"

    serial_no = fields.Integer(string="Sl no")
    link_1 = fields.Char(string="Link-1")
    units = fields.Float(string="Units")


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"

    direct_transfer = fields.Boolean(string="Direct transfer")
    shop_transfer = fields.Boolean(string="Shop transfer")
    damage_stock_out = fields.Boolean(string="Damage stock out")
    damage_stock_in = fields.Boolean(string="Damage stock in")
