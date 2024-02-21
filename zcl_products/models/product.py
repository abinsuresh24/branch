# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Syooj T K
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_alias = fields.Char(string='Alias')
    # branch_id = fields.Many2one('res.branch', string='Branch', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_id, store=True, readonly=True)
    product_type = fields.Selection([('finished_good', 'Finished Good'), ('raw_material', 'Raw Material')],
                                    string="Product Type", required=True)
    reorder_level = fields.Float(string='Reorder Level')
    bin_capacity = fields.Integer(string='Bin Capacity')
    valuation_method = fields.Selection(
        [('wt_average', 'Wt Average'), ('lifo', 'LIFO'), ('fifo', 'FIFO'), ('fifo_time', 'FIFO (Consider Tr. Time)')],
        default='wt_average')
    brand = fields.Char(string='Brand')
    warranty = fields.Integer(string='Warranty')
    division_group = fields.Char(string='Division Group')
    item_sub_group = fields.Char(string='Item Sub Group')
    markup = fields.Char(string='Markup %')
    foc = fields.Boolean(string='Foc')
    vendor = fields.Many2one('res.partner', string='Vendor', domain=[('vendor_true', '=', True)])
    country_of_origin_id = fields.Many2one('res.country', 'Country of Origin')
    alternative = fields.Char(string='Alternative 1')
    item_group = fields.Char(string='Item Group')
    item_category = fields.Char(string='Item Category')
    brand_new = fields.Char(string='Brand New')
    movement = fields.Selection([
        ('fast', 'Fast'),
        ('slow', 'Slow'),
        ('medium', 'Medium'),
    ], string="Movement")
    grade = fields.Char(string='Grade')
    item_type = fields.Char(string='Item Type')
    with_effect_from = fields.Date(string='With effect from')
    cntr_max_price = fields.Float(string='Cntr Max Price', digits=(12, 3))
    rate_definition = fields.Selection([('over_all_selling_rate', 'Over all Selling rate'), ('branch', 'Branch')],
                                       default='over_all_selling_rate', string='Rates Definition')
    minimal_selling_price = fields.Float(string="Minimal Selling Price", digits=(12, 3))
    cntr_min_price = fields.Float(string='Cntr Min Price', digits=(12, 3))
    traders_price = fields.Float(string='Traders Price', digits=(12, 3))
    dealer_price = fields.Float(string='Dealer', digits=(12, 3))
    discount = fields.Float(string='Discount', digits=(12, 3))
    project_price = fields.Float(string='Project Price', digits=(12, 3))
    wholesale = fields.Float(string='Wholesale', digits=(12, 3))
    basic_unit = fields.Selection([('no', 'NO'), ('yes', 'YES')], default='no', tracking=True)
    related_units_ids = fields.One2many('unit.line', 'unit_model_id', string='Related Units')
    related_reorders_ids = fields.One2many('reorder.line', 'main_model_id', string='Related Reorders')
    cash_sale_count = fields.Float(string="Cash Sale Count")
    cash_sale_price = fields.Float(string="Cash Sale Price", digits=(12, 3))
    state = fields.Selection([('draft', 'Draft'), ('done', 'Confirmed')],
                             string='Status', default='draft', required=True)
    purchase_uom = fields.Many2one('uom.uom', string="Purchase Unit Of Measure")
    sale_uom = fields.Many2one('uom.uom', string="Sale Unit Of Measure")

    def action_confirm(self):
        self.state = 'done'

    @api.onchange('minimal_selling_price', 'cntr_min_price')
    def onchange_minimal_selling_price(self):
        if self.minimal_selling_price > self.cntr_max_price:
            raise ValidationError("Minimal selling price must be less than Cntr Max Price:" + str(self.cntr_max_price))
        if self.cntr_min_price > self.cntr_max_price:
            raise ValidationError("Cntr Min Price must be less than Cntr Max Price:" + str(self.cntr_max_price))


class Unit(models.Model):
    _name = "unit.line"

    unit_model_id = fields.Many2one('product.product')
    unit = fields.Selection([('length', 'Length'), ('meter', 'Meter'), ('centimeter', 'Centimeter')])
    conversion = fields.Float(string='Conversion', digits=(12, 6))


class Reorder(models.Model):
    _name = "reorder.line"

    main_model_id = fields.Many2one('product.product')
    branch = fields.Char(string='Branch')
    reorder = fields.Char(string='Reorder')
    reorder_2 = fields.Char(string='Reorder2')
    lead_time = fields.Float(string='Lead Time')
