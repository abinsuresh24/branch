# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.osv import expression

class ResBranch(models.Model):
    _name = 'res.branch'
    _description = 'Branch'
    _sql_constraints = [
        ('unique_do_prefix', 'unique (do_prefix)', _('Prefix code DO already exists!')),
        ('unique_internal_do_prefix', 'unique (internal_do_prefix)',
         _('Prefix code Internal DO already exists!')),
        ('unique_project_do_prefix', 'unique (project_do_prefix)',
         _('Prefix code Project DO already exists!')),
        ('unique_cash_sale_prefix', 'unique (cash_sale_prefix)',
         _('Prefix code Cash sale already exists!')),
        ('unique_cash_memo_prefix', 'unique (cash_memo_prefix)',
         _('Prefix code Cash memo already exists!')),
        ('unique_sale_quotation_prefix', 'unique (sale_quotation_prefix)',
         _('Prefix code sale quotation already exists!')),
        ('unique_sale_return_prefix', 'unique (sale_return_prefix)',
         _('Prefix code sale return already exists!')),
        ('unique_cash_sale_return_prefix', 'unique (cash_sale_return_prefix)',
         _('Prefix code cash sale return already exists!')),
        ('unique_do_prefix_letter', 'unique (do_prefix_letter)',
         _('Prefix letter DO already exists!')),
        ('unique_internal_do_prefix_letter', 'unique (internal_do_prefix_letter)',
         _('Prefix letter Internal DO already exists!')),
        ('unique_project_do_prefix_letter', 'unique (project_do_prefix_letter)',
         _('Prefix letter Project DO already exists!')),
        ('unique_cash_sale_prefix_letter', 'unique (cash_sale_prefix_letter)',
         _('Prefix letter Cash sale already exists!')),
        ('unique_cash_memo_prefix_letter', 'unique (cash_memo_prefix_letter)',
         _('Prefix letter Cash memo already exists!')),
        ('unique_sale_quotation_prefix_letter', 'unique (sale_quotation_prefix_letter)',
         _('Prefix letter sale quotation already exists!')),
        ('unique_sale_return_prefix_letter', 'unique (sale_return_prefix_letter)',
         _('Prefix letter sale return already exists!')),
        ('unique_cash_sale_return_prefix_letter', 'unique (cash_sale_return_prefix_letter)',
         _('Prefix letter Cash sale return already exists!')),
        ('unique_purchase_quotation_prefix', 'unique (purchase_quotation_prefix)',
         _('Prefix code Purchase Quotation already exists!')),
        ('unique_purchase_quotation_prefix_letter', 'unique (purchase_quotation_prefix_letter)',
         _('Prefix letter Purchase Quotation already exists!')),
        ('unique_purchase_requisition_prefix', 'unique (purchase_requisition_prefix)',
         _('Prefix code Purchase Requisition already exists!')),
        ('unique_purchase_requisition_prefix_letter', 'unique (purchase_requisition_prefix_letter)',
         _('Prefix letter Purchase Requisition already exists!')),
        ('unique_po_local_prefix', 'unique (po_local_prefix)',
         _('Prefix code Purchase Order-Local already exists!')),
        ('unique_po_local_letter', 'unique (po_local_letter)',
         _('Prefix letter Purchase Order-Local already exists!')),
        ('unique_mrn_local_prefix', 'unique (mrn_local_prefix)',
         _('Prefix code MRN-Local already exists!')),
        ('unique_mrn_local_prefix_letter', 'unique (mrn_local_prefix_letter)',
         _('Prefix letter MRN-Local already exists!')),
        ('unique_mrn_import_prefix', 'unique (mrn_import_prefix)',
         _('Prefix code MRN-Import already exists!')),
        ('unique_mrn_import_prefix_letter', 'unique (mrn_import_prefix_letter)',
         _('Prefix letter MRN-Import already exists!')),
        ('unique_pv_local_prefix', 'unique (pv_local_prefix)',
         _('Prefix code Purchase Voucher-Local already exists!')),
        ('unique_pv_local_prefix_letter', 'unique (pv_local_prefix_letter)',
         _('Prefix letter Purchase Voucher-Local already exists!')),
        ('unique_pv_import_prefix', 'unique (pv_import_prefix)',
         _('Prefix code Purchase Voucher-Import already exists!')),
        ('unique_pv_import_prefix_letter', 'unique (pv_import_prefix_letter)',
         _('Prefix letter Purchase Voucher-Import already exists!')),
        ('unique_pr_local_prefix', 'unique (pr_local_prefix)',
         _('Prefix code Purchase Return-Local already exists!')),
        ('unique_pr_local_prefix_letter', 'unique (pr_local_prefix_letter)',
         _('Prefix letter Purchase Return-Local already exists!')),
        ('unique_pr_import_prefix', 'unique (pr_import_prefix)',
         _('Prefix code Purchase Return-Import already exists!')),
        ('unique_pr_import_prefix_letter', 'unique (pr_import_prefix_letter)',
         _('Prefix letter Purchase Return-Import already exists!')),
        ('unique_po_import_prefix', 'unique (po_import_prefix)',
         _('Prefix code Purchase Order-Import already exists!')),
        ('unique_po_import_prefix_letter', 'unique (po_import_prefix_letter)',
         _('Prefix letter Purchase Order-Import already exists!')),
        ('unique_cash_purchase_prefix', 'unique (cash_purchase_prefix)',
         _('Prefix code Cash Purchase already exists!')),
        ('unique_cash_purchase_prefix_letter', 'unique (cash_purchase_prefix_letter)',
         _('Prefix letter Cash Purchase already exists!')),
        ('unique_cash_purchase_return_prefix', 'unique (cash_purchase_return_prefix)',
         _('Prefix code Cash Purchase Return already exists!')),
        ('unique_cash_purchase_return_prefix_letter', 'unique (cash_purchase_return_prefix_letter)',
         _('Prefix letter Cash Purchase Return already exists!')),
        ('unique_purchase_prefix_name', 'unique (purchase_prefix_name)',
         _('Prefix name already exists!')),
        ('unique_material_requisition_prefix', 'unique (material_requisition_prefix)',
         _('Material Requisition Prefix Code already exists!')),
        ('unique_material_requisition_prefix_letter', 'unique (material_requisition_prefix_letter)',
         _('Material Requisition Prefix Letter already exists!')),
        ('unique_shop_requisition_prefix', 'unique (shop_requisition_prefix)',
         _('Shop Requisition Prefix Code already exists!')),
        ('unique_shop_requisition_prefix_letter', 'unique (shop_requisition_prefix_letter)',
         _('Shop Requisition Prefix Letter already exists!')),
        ('unique_stock_transfer_out_prefix', 'unique (stock_transfer_out_prefix)',
         _('Stock Transfer Out Prefix Code already exists!')),
        ('unique_stock_transfer_out_prefix_letter', 'unique (stock_transfer_out_prefix_letter)',
         _('Stock Transfer Out Prefix Letter already exists!')),
        ('unique_stock_transfer_in_prefix', 'unique (stock_transfer_in_prefix)',
         _('Stock Transfer In Prefix Code already exists!')),
        ('unique_stock_transfer_in_prefix_letter', 'unique (stock_transfer_in_prefix_letter)',
         _('Stock Transfer In Prefix Letter already exists!')),
        ('unique_shop_transfer_out_prefix', 'unique (shop_transfer_out_prefix)',
         _('Shop Transfer Out Prefix Code already exists!')),
        ('unique_shop_transfer_out_prefix_letter', 'unique (shop_transfer_out_prefix_letter)',
         _('Shop Transfer Out Prefix Letter already exists!')),
        ('unique_shop_transfer_in_prefix', 'unique (shop_transfer_in_prefix)',
         _('Shop Transfer In Prefix Code already exists!')),
        ('unique_shop_transfer_in_prefix_letter', 'unique (shop_transfer_in_prefix_letter)',
         _('Shop Transfer In Prefix Letter already exists!')),
        ('unique_direct_transfer_out_prefix', 'unique (direct_transfer_out_prefix)',
         _('Direct Transfer Out Prefix Code already exists!')),
        ('unique_direct_transfer_out_prefix_letter', 'unique (direct_transfer_out_prefix_letter)',
         _('Direct Transfer Out Prefix Letter already exists!')),
        ('unique_direct_transfer_in_prefix', 'unique (direct_transfer_in_prefix)',
         _('Direct Transfer In Prefix Code already exists!')),
        ('unique_direct_transfer_in_prefix_letter', 'unique (direct_transfer_in_prefix_letter)',
         _('Direct Transfer In Prefix Letter already exists!')),
        ('unique_damage_stock_out_prefix', 'unique (damage_stock_out_prefix)',
         _('Damage Stock Out Prefix Code already exists!')),
        ('unique_damage_stock_out_prefix_letter', 'unique (damage_stock_out_prefix_letter)',
         _('Damage Stock Out Prefix Letter already exists!')),
        ('unique_damage_stock_in_prefix', 'unique (damage_stock_in_prefix)',
         _('Damage Stock In Prefix Code already exists!')),
        ('unique_damage_stock_in_prefix_letter', 'unique (damage_stock_in_prefix_letter)',
         _('Damage Stock In Prefix Letter already exists!')),
        ('unique_branch_code', 'unique (branch_code)', _('Branch Code already exists!')),
    ]

    name = fields.Char(required=True)
    stock_location = fields.Many2one('stock.location', string="Branch location", domain="[('usage', '=', 'internal')]")
    company_id = fields.Many2one('res.company', required=True)
    telephone = fields.Char(string='Telephone No')
    address = fields.Text('Address')
    # sequence = fields.Integer(default=10)
    prefix_name = fields.Char("Prefix Name")
    do_prefix = fields.Char(string="DO Prefix Code")
    do_prefix_letter = fields.Char(string="DO Prefix")
    do_padding = fields.Integer("DO Padding")
    internal_do_prefix = fields.Char(string="Internal DO Prefix Code")
    internal_do_prefix_letter = fields.Char(string="Internal DO Prefix")
    internal_do_padding = fields.Integer("Internal DO Padding")
    project_do_prefix = fields.Char(string="Project DO Prefix Code")
    project_do_prefix_letter = fields.Char(string="Project DO Prefix")
    project_do_padding = fields.Integer("Project DO Padding")
    cash_sale_prefix = fields.Char(string="Cash Sale Prefix Code")
    cash_sale_prefix_letter = fields.Char(string="Cash Sale Prefix")
    cash_sale_padding = fields.Integer("Cash Sale Padding")
    cash_memo_prefix = fields.Char(string="Cash Memo Prefix Code")
    cash_memo_prefix_letter = fields.Char(string="Cash Memo Prefix")
    cash_memo_padding = fields.Integer("Cash Memo Padding")
    sale_quotation_prefix = fields.Char(string="Sale Quotation Prefix Code")
    sale_quotation_prefix_letter = fields.Char(string="Sale Quotation Prefix")
    sale_quotation_padding = fields.Integer("Sale Quotation Padding")
    sale_return_prefix = fields.Char(string="Sale Return Prefix Code")
    sale_return_prefix_letter = fields.Char(string="Sale Return Prefix")
    sale_return_padding = fields.Integer("Sale Return Padding")
    cash_sale_return_prefix = fields.Char(string="Cash Sale Return Prefix Code")
    cash_sale_return_prefix_letter = fields.Char(string="Cash Sale Return Prefix")
    cash_sale_return_padding = fields.Integer("Cash Sale Return Padding")
    purchase_quotation_prefix = fields.Char(string="Purchase Quotation Prefix Code")
    purchase_quotation_prefix_letter = fields.Char(string="Purchase Quotation Prefix")
    purchase_quotation_padding = fields.Integer("Purchase Quotation Padding")
    purchase_requisition_prefix = fields.Char(string="Purchase Requisition Prefix Code")
    purchase_requisition_prefix_letter = fields.Char(string="Purchase Requisition Prefix")
    purchase_requisition_padding = fields.Integer("Purchase Requisition Padding")
    po_local_prefix = fields.Char(string="Purchase Order-Local Prefix Code")
    po_local_letter = fields.Char(string="Purchase Order-Local Prefix")
    po_local_padding = fields.Integer("Purchase Order-Local Padding")
    mrn_local_prefix = fields.Char(string="MRN-Local Prefix Code")
    mrn_local_prefix_letter = fields.Char(string="MRN-Local Prefix")
    mrn_local_padding = fields.Integer("MRN-Local Padding")
    mrn_import_prefix = fields.Char(string="MRN-Import Prefix Code")
    mrn_import_prefix_letter = fields.Char(string="MRN-Import Prefix")
    mrn_import_padding = fields.Integer("MRN-Import Padding")
    pv_local_prefix = fields.Char(string="Purchase Voucher-Local Prefix Code")
    pv_local_prefix_letter = fields.Char(string="Purchase Voucher-Local Prefix")
    pv_local_padding = fields.Integer("Purchase Voucher-Local Padding")
    pv_import_prefix = fields.Char(string="Purchase Voucher-Import Prefix Code")
    pv_import_prefix_letter = fields.Char(string="Purchase Voucher-Import Prefix")
    pv_import_padding = fields.Integer("Purchase Voucher-Import Padding")
    pr_local_prefix = fields.Char(string="Purchase Return-Local Prefix Code")
    pr_local_prefix_letter = fields.Char(string="Purchase Return-Local Prefix")
    pr_local_padding = fields.Integer("Purchase Return-Local Padding")
    pr_import_prefix = fields.Char(string="Purchase Return-Import Prefix Code")
    pr_import_prefix_letter = fields.Char(string="Purchase Return-Import Prefix")
    pr_import_padding = fields.Integer("Purchase Return-Import Padding")
    po_import_prefix = fields.Char(string="Purchase Order-Import Prefix Code")
    po_import_prefix_letter = fields.Char(string="Purchase Order-Import Prefix")
    po_import_padding = fields.Integer("Purchase Order-Import Padding")
    cash_purchase_prefix = fields.Char(string="Cash Purchase Prefix Code")
    cash_purchase_prefix_letter = fields.Char(string="Cash Purchase Prefix")
    cash_purchase_padding = fields.Integer("Cash Purchase Padding")
    cash_purchase_return_prefix = fields.Char(string="Cash Purchase Return Prefix Code")
    cash_purchase_return_prefix_letter = fields.Char(string="Cash Purchase Return Prefix")
    cash_purchase_return_padding = fields.Integer("Cash Purchase Return Padding")
    purchase_prefix_name = fields.Char("Prefix Name")
    inventory_prefix_name = fields.Char("Prefix Name")
    material_requisition_prefix = fields.Char(string="Material Requisition Prefix Code")
    material_requisition_prefix_letter = fields.Char(string="Material Requisition Prefix")
    material_requisition_padding = fields.Integer("Material Requisition Padding")
    shop_requisition_prefix = fields.Char(string="Shop Requisition Prefix Code")
    shop_requisition_prefix_letter = fields.Char(string="Shop Requisition Prefix")
    shop_requisition_padding = fields.Integer("Shop Requisition Padding")
    stock_transfer_out_prefix = fields.Char(string="Stock Transfer Out Prefix Code")
    stock_transfer_out_prefix_letter = fields.Char(string="Stock Transfer Out Prefix")
    stock_transfer_out_padding = fields.Integer("Stock Transfer Out Padding")
    stock_transfer_in_prefix = fields.Char(string="Stock Transfer In Prefix Code")
    stock_transfer_in_prefix_letter = fields.Char(string="Stock Transfer In Prefix")
    stock_transfer_in_padding = fields.Integer("Stock Transfer In Padding")
    shop_transfer_out_prefix = fields.Char(string="Shop Transfer Out Prefix Code")
    shop_transfer_out_prefix_letter = fields.Char(string="Shop Transfer Out Prefix")
    shop_transfer_out_padding = fields.Integer("Shop Transfer Out Padding")
    shop_transfer_in_prefix = fields.Char(string="Shop Transfer In Prefix Code")
    shop_transfer_in_prefix_letter = fields.Char(string="Shop Transfer In Prefix")
    shop_transfer_in_padding = fields.Integer("Shop Transfer In Padding")
    direct_transfer_out_prefix = fields.Char(string="Direct Transfer Out Prefix Code")
    direct_transfer_out_prefix_letter = fields.Char(string="Direct Transfer Out Prefix")
    direct_transfer_out_padding = fields.Integer("Direct Transfer Out Padding")
    direct_transfer_in_prefix = fields.Char(string="Direct Transfer In Prefix Code")
    direct_transfer_in_prefix_letter = fields.Char(string="Direct Transfer In Prefix")
    direct_transfer_in_padding = fields.Integer("Direct Transfer In Padding")
    damage_stock_out_prefix = fields.Char(string="Damage Stock Out Prefix Code")
    damage_stock_out_prefix_letter = fields.Char(string="Damage Stock Out Prefix")
    damage_stock_out_padding = fields.Integer("Damage Stock Out Padding")
    damage_stock_in_prefix = fields.Char(string="Damage Stock In Prefix Code")
    damage_stock_in_prefix_letter = fields.Char(string="Damage Stock In Prefix")
    damage_stock_in_padding = fields.Integer("Damage Stock In Padding")
    branch_code = fields.Char(string="Code")


    def prefix_generate(self):
        if not self.env['ir.sequence'].search([('code', '=',  self.do_prefix)]):
            code_do = self.env['ir.sequence'].sudo().create({
                'name': self.prefix_name,
                'code': self.do_prefix,
                'prefix': self.do_prefix_letter,
                'padding': self.do_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.project_do_prefix)]):
            code_project_do = self.env['ir.sequence'].sudo().create({
                'name': self.prefix_name,
                'code': self.project_do_prefix,
                'prefix': self.project_do_prefix_letter,
                'padding': self.project_do_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.internal_do_prefix)]):
            code_internal_do = self.env['ir.sequence'].sudo().create({
                'name': self.prefix_name,
                'code': self.internal_do_prefix,
                'prefix': self.internal_do_prefix_letter,
                'padding': self.internal_do_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.cash_sale_prefix)]):
            code_cash_sale = self.env['ir.sequence'].sudo().create({
                'name': self.prefix_name,
                'code': self.cash_sale_prefix,
                'prefix': self.cash_sale_prefix_letter,
                'padding': self.cash_sale_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.cash_memo_prefix)]):
            code_cash_memo = self.env['ir.sequence'].sudo().create({
                'name': self.prefix_name,
                'code': self.cash_memo_prefix,
                'prefix': self.cash_memo_prefix_letter,
                'padding': self.cash_memo_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.sale_quotation_prefix)]):
            code_sale_quotation = self.env['ir.sequence'].sudo().create({
                'name': self.prefix_name,
                'code': self.sale_quotation_prefix,
                'prefix': self.sale_quotation_prefix_letter,
                'padding': self.sale_quotation_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.sale_return_prefix)]):
            code_sale_return = self.env['ir.sequence'].sudo().create({
                'name': self.prefix_name,
                'code': self.sale_return_prefix,
                'prefix': self.sale_return_prefix_letter,
                'padding': self.sale_return_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.cash_sale_return_prefix)]):
            code_cash_sale_return = self.env['ir.sequence'].sudo().create({
                'name': self.prefix_name,
                'code': self.cash_sale_return_prefix,
                'prefix': self.cash_sale_return_prefix_letter,
                'padding': self.cash_sale_return_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.purchase_quotation_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.purchase_quotation_prefix,
                'prefix': self.purchase_quotation_prefix_letter,
                'padding': self.purchase_quotation_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.purchase_requisition_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.purchase_requisition_prefix,
                'prefix': self.purchase_requisition_prefix_letter,
                'padding': self.purchase_requisition_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.po_local_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.po_local_prefix,
                'prefix': self.po_local_letter,
                'padding': self.po_local_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.mrn_local_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.mrn_local_prefix,
                'prefix': self.mrn_local_prefix_letter,
                'padding': self.mrn_local_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.mrn_import_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.mrn_import_prefix,
                'prefix': self.mrn_import_prefix_letter,
                'padding': self.mrn_import_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.pv_local_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.pv_local_prefix,
                'prefix': self.pv_local_prefix_letter,
                'padding': self.pv_local_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.pv_import_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.pv_import_prefix_letter,
                'prefix': self.pv_local_prefix_letter,
                'padding': self.pv_import_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.pr_local_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.pr_local_prefix,
                'prefix': self.pr_local_prefix_letter,
                'padding': self.pr_local_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.pr_import_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.pr_import_prefix,
                'prefix': self.pr_import_prefix_letter,
                'padding': self.pr_import_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.po_import_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.po_import_prefix,
                'prefix': self.po_import_prefix_letter,
                'padding': self.po_import_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.cash_purchase_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.cash_purchase_prefix,
                'prefix': self.cash_purchase_prefix_letter,
                'padding': self.cash_purchase_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.cash_purchase_return_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.purchase_prefix_name,
                'code': self.cash_purchase_return_prefix,
                'prefix': self.cash_purchase_return_prefix_letter,
                'padding': self.cash_purchase_return_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.material_requisition_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.inventory_prefix_name,
                'code': self.material_requisition_prefix,
                'prefix': self.material_requisition_prefix_letter,
                'padding': self.material_requisition_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.shop_requisition_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.inventory_prefix_name,
                'code': self.shop_requisition_prefix,
                'prefix': self.shop_requisition_prefix_letter,
                'padding': self.shop_requisition_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.stock_transfer_out_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.inventory_prefix_name,
                'code': self.stock_transfer_out_prefix,
                'prefix': self.stock_transfer_out_prefix_letter,
                'padding': self.stock_transfer_out_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.stock_transfer_in_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.inventory_prefix_name,
                'code': self.stock_transfer_in_prefix,
                'prefix': self.stock_transfer_in_prefix_letter,
                'padding': self.stock_transfer_in_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.shop_transfer_out_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.inventory_prefix_name,
                'code': self.shop_transfer_out_prefix,
                'prefix': self.shop_transfer_out_prefix_letter,
                'padding': self.shop_transfer_out_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.shop_transfer_in_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.inventory_prefix_name,
                'code': self.shop_transfer_in_prefix,
                'prefix': self.shop_transfer_in_prefix_letter,
                'padding': self.shop_transfer_in_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.direct_transfer_out_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.inventory_prefix_name,
                'code': self.direct_transfer_out_prefix,
                'prefix': self.direct_transfer_out_prefix_letter,
                'padding': self.direct_transfer_out_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.direct_transfer_in_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.inventory_prefix_name,
                'code': self.direct_transfer_in_prefix,
                'prefix': self.direct_transfer_in_prefix_letter,
                'padding': self.direct_transfer_in_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.damage_stock_out_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.inventory_prefix_name,
                'code': self.damage_stock_out_prefix,
                'prefix': self.damage_stock_out_prefix_letter,
                'padding': self.damage_stock_out_padding,
                'active': True,
            })
        if not self.env['ir.sequence'].sudo().search([('code', '=', self.damage_stock_in_prefix)]):
            prefix = self.env['ir.sequence'].sudo().create({
                'name': self.inventory_prefix_name,
                'code': self.damage_stock_in_prefix,
                'prefix': self.damage_stock_in_prefix_letter,
                'padding': self.damage_stock_in_padding,
                'active': True,
            })

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []

        if self._context.get('allowed_company_ids'):
            selected_company_ids = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
            if selected_company_ids:
                branches_ids = self.env['res.branch'].search([('company_id','in',selected_company_ids.ids)])
                args = [('id', 'in', branches_ids.ids)]
                return super(ResBranch, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                name_get_uid=name_get_uid)
            return super(ResBranch, self)._name_search(name=name, args=args, operator=operator, limit=limit,name_get_uid=name_get_uid)