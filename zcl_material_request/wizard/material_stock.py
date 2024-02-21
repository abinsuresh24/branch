# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MaterialStockWizard(models.Model):
    _name = "material.stock.wizard"
    _description = "Material stock wizard"

    material_stock_ids = fields.One2many('material.stock.line', 'material_stock_id')
    line_id = fields.Integer(string="ID")
    items_id = fields.Many2one('product.product')
    material_id = fields.Integer(string="MID")

    # def confirm_request(self):
    #     for rec in self.material_stock_ids:
    #         if rec.req_qty:
    #             self.env['material.request.line'].sudo().create({'items_id': self.items_id.id,
    #                                                              'requested_to': rec.loc_id.id,
    #                                                              'qty': rec.req_qty, 'mat_request_id': self.line_id})
    def confirm_request(self):
        for rec in self.material_stock_ids:
            mt = self.env['material.request'].browse(self.material_id).exists()
            if rec.req_qty:
                self.env['material.request.line'].sudo().create({
                    'items_id': self.items_id.id,
                    'requested_to': rec.loc_id.id,
                    'qty': rec.req_qty,
                    'mat_id': mt.id
                })


class MaterialStockLine(models.Model):
    _name = "material.stock.line"

    loc_id = fields.Many2one('stock.location', string="Location")
    quantity = fields.Float(string="Quantity")
    req_qty = fields.Float(string="Requested Quantity")
    material_stock_id = fields.Many2one("material.stock.wizard")

    @api.onchange('req_qty')
    def _onchange_req_qty(self):
        if self.req_qty > self.quantity:
            raise ValidationError("Required quantity must be less than available quantity")
