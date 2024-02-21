from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES, change_default=True, tracking=True, domain="['&', ('vendor_true', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    # internal_do_partner_id = fields.Many2one('res.partner', string='Vendor', domain="[('vendor_true', '=', True),('purchase_type', '=', 'internal_do')]")
    # project_do_partner_id = fields.Many2one('res.partner', string='Vendor', domain="[('vendor_true', '=', True),('purchase_type', '=', 'project_do')]")
    narration = fields.Text(string="Narration")
    delivery_terms = fields.Char('Delivery Terms')
    delivery_address = fields.Many2one('stock.location', string='Delivery Addr.', domain="[('usage', '=', 'internal')]", required=True)
    prq_no = fields.Char(string="PRQ No")
    cargo_details = fields.Char(string="Cargo Details")
    total_qty = fields.Float(string="Quantity")
    total_last_rate = fields.Float(string="Last Rate", digits=(16, 3))
    total_least_rate = fields.Float(string="Least Rate", digits=(16, 3))
    total_gross = fields.Float(string="Gross", digits=(16, 3))
    total_discount_amt = fields.Float(string="Discount Amt", digits=(16, 3))
    total_net_value = fields.Float(string="Net Value", digits=(16, 3))
    total_net = fields.Float(string="Net", digits=(16, 3))
    total_vat = fields.Float(string="VAT 5%", digits=(16, 3))
    shop_purchase = fields.Boolean(string="Shop Purchase")
    store_purchase = fields.Boolean(string="Store Purchase")
    shop_internal_do = fields.Boolean(string='Shop Internal DO')
    store_internal_do = fields.Boolean(string='Store Internal DO')
    shop_project_do = fields.Boolean(string='Shop Project DO')
    store_project_do = fields.Boolean(string='Store Project DO')
    grn_local_import = fields.Boolean(string='Grn local import')
    shop_grn_local_import = fields.Boolean(string='Grn local import')
    purchase_local = fields.Boolean(string='Purchase local')
    purchase_import = fields.Boolean(string='Purchase import')

    @api.onchange('partner_id')
    def _onchange_name(self):
        self.delivery_address = self.partner_id.contact_address

    # @api.onchange('internal_do_partner_id')
    # def _onchange_internal_do_partner(self):
    #     self.partner_id = self.internal_do_partner_id.id
    #
    # @api.onchange('project_do_partner_id')
    # def _onchange_project_do_partner(self):
    #     self.partner_id = self.project_do_partner_id.id

    @api.onchange('order_line')
    def _onchange_order_lines(self):
        sl_no = 1
        for line in self.order_line:
            line.serial_no = sl_no
            sl_no += 1
            if self.shop_internal_do:
                line.price_unit = line.product_id.traders_price
            if self.store_internal_do:
                line.price_unit = line.product_id.traders_price
            if self.shop_project_do:
                line.price_unit = line.product_id.project_price
            if self.store_project_do:
                line.price_unit = line.product_id.project_price
        total_qty_sum = 0
        total_last_rate_sum = 0
        total_least_rate_sum = 0
        total_gross_sum = 0
        total_discount_amt_sum = 0
        total_net_value_sum = 0
        for rec in self.order_line:
            total_qty_sum += rec.product_qty
            total_last_rate_sum += rec.last_rate
            total_least_rate_sum += rec.least_rate
            total_gross_sum += rec.gross
            total_discount_amt_sum += rec.discount_amt
            total_net_value_sum += rec.price_subtotal
        self.total_qty = total_qty_sum
        self.total_last_rate = total_last_rate_sum
        self.total_least_rate = total_least_rate_sum
        self.total_gross = total_gross_sum
        self.total_discount_amt = total_discount_amt_sum
        self.total_net_value = total_net_value_sum
        self.total_vat = total_net_value_sum * 0.05
        self.total_net = self.total_vat + self.total_net_value

    def action_po(self):
        res = self.button_confirm()
        if res:
            for rec in self.picking_ids:
                #picking type location changing
                recepit = self.env['stock.picking.type'].search([('id', '=', rec.picking_type_id.id)])
                recepit.update({
                    'default_location_dest_id': self.delivery_address.id
                })
                rec.location_dest_id = self.delivery_address.id
                for res in rec.move_ids_without_package:
                    res.location_dest_id = self.delivery_address.id
                    print(res.quantity_done, "i")
                    res.quantity_done = res.product_uom_qty
                    print(res.quantity_done, "K")
                rec.button_validate()

    def action_create_invoice(self):
        res = super(PurchaseOrder,self).action_create_invoice()
        if self.purchase_import:
            self.invoice_ids.purchase_import = True
        if self.purchase_local:
            self.invoice_ids.purchase_local = True
        return res

    def action_view_invoice(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        if not self.purchase_local and not self.purchase_import:
            if not invoices:
                # Invoice_ids may be filtered depending on the user. To ensure we get all
                # invoices related to the purchase order, we read them in sudo to fill the
                # cache.
                self.invalidate_model(['invoice_ids'])
                self.sudo()._read(['invoice_ids'])
                invoices = self.invoice_ids

            result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
            # choose the view_mode accordingly
            if len(invoices) > 1:
                result['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                res = self.env.ref('account.view_move_form', False)
                form_view = [(res and res.id or False, 'form')]
                if 'views' in result:
                    result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
                else:
                    result['views'] = form_view
                result['res_id'] = invoices.id
            else:
                result = {'type': 'ir.actions.act_window_close'}

            return result
    



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    serial_no = fields.Integer(string="SNo.")
    units = fields.Float(string="Units")
    last_rate = fields.Float(string="Last Rate")
    least_rate = fields.Float(string="Least Rate")
    gross = fields.Float(string="Gross")
    discount_amt = fields.Float(string="Discount Amt")


class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_import = fields.Boolean(string="Purchase Import")
    purchase_local = fields.Boolean(string="Purchase Local")
