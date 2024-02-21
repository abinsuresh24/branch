from odoo import models, fields, exceptions, api, _
from datetime import date, datetime
from odoo.exceptions import Warning, ValidationError, UserError
from lxml import etree


class SaleReturnWizardsLine(models.TransientModel):
    _name = "sale.return.wizard"

    sale_order = fields.Many2one('sale.order', 'Sale Order')
    sale_order_line = fields.Many2one('sale.order.line', 'Sale Order')
    sale_return_wizard_id = fields.Many2one('sale.order.line', string='wizard')
    product_id = fields.Many2one('product.product', string='Item', required=True)
    name = fields.Char("Description")
    unit = fields.Float(string="Unit")


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        for node_form in doc.xpath("//tree"):
            node_form.set("create", 'false')
            node_form.set("edit", 'false')
            res['arch'] = etree.tostring(doc)
        for node_form in doc.xpath("//form"):
            node_form.set("create", 'false')
            node_form.set("edit", 'false')
            res['arch'] = etree.tostring(doc)
        return res
    # def add_to_the_line(self):
    #     self.sale_return_wizard_id.price_unit = self.price_unit
    #     order_lines = self.env['sale.order.line'].search([('id', '=', self.sale_order_line.id)])
    #     self.sale_return_wizard_id.tax_id = order_lines.tax_id.ids
    def add_to_the_line(self):
        self.sale_return_wizard_id.item_code = self.item_code
        order_lines = self.env['sale.order.line'].search([('id', '=', self.sale_order_line.id)])
        self.sale_return_wizard_id.unit = order_lines.unit
