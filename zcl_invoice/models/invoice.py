from odoo import models, fields, api


class Invoice(models.Model):
    _name = 'customer.invoice'
    _description = 'Customer Invoices'
    _rec_name = "invoice_no"

    invoice_no = fields.Char(string="Invoice No", default="New")
    date = fields.Datetime(string="Date", default=fields.Date.today())
    partner_id = fields.Many2one('res.partner', string='Customer', domain="[('customer_true', '=', True)]")
    account_id = fields.Many2one('account.account', string='Sale Account')
    branch_id = fields.Many2one('res.branch', string="Branch", default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_id, store=True)
    salesman_id = fields.Many2one('res.partner', string="Salesman", domain="[('sales_man_true', '=', True)]")
    narration = fields.Html(string="Narration")
    dln_no = fields.Char(string="DLN No")
    gsm_no = fields.Char(string="GSM No")
    available_balance = fields.Float(string="Available Balance", digits=(16, 3))
    customer_invoice_ids = fields.One2many('invoice.lines', 'invoice_lines_id', string='Customer', store=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('cancel', 'Cancelled')], default='draft')
    sub_total = fields.Float(string="Sub Total", digits=(16, 3))

    @api.onchange('sub_total')
    def compute_total_net(self):
        # Update the value of total_net when sub_total changes
        self.total_net = self.sub_total


    @api.onchange('partner_id')
    def _onchange_partner_ids(self):
        if self.partner_id:
            rec = self.env['sale.order'].sudo().search([('partner_id.id', '=', self.partner_id.id)])
            if rec:
                self.customer_invoice_ids = [(5, 0, 0)]
                for res in rec:
                    if len(res.invoice_ids.ids) == 0:
                        self.customer_invoice_ids = [fields.Command.create({'order_id': res.id,'amount_total': res.total_net})]


    def customer_selected_invoice(self):
        lst = []
        invoice_lines_to_delete = [rec.id for rec in self.customer_invoice_ids if not rec.check_box]
        self.customer_invoice_ids.filtered(lambda rec: rec.id in invoice_lines_to_delete).unlink()
        for rec in self.customer_invoice_ids:
            lst.append(rec.order_id.id)
        invoice = self.env['sale.order'].browse(lst).exists()._create_invoices(final=True)
        invoice.action_post()
        self.invoice_no = invoice.name
        self.state = 'confirm'

    def invoice_confirm(self):
        lst = []
        for rec in self.customer_invoice_ids:
            lst.append(rec.order_id.id)
        invoice = self.env['sale.order'].browse(lst).exists()._create_invoices(final=True)
        invoice.action_post()
        self.invoice_no = invoice.name
        self.state = 'confirm'


class CustomerInvoiceLines(models.Model):
    _name = 'invoice.lines'

    check_box = fields.Boolean(string="    ")
    invoice_lines_id = fields.Many2one('customer.invoice')
    order_id = fields.Many2one('sale.order')
    partner_id = fields.Many2one('res.partner', string='Customer', related='order_id.partner_id')
    sales_man_id = fields.Many2one('res.partner', string='Sales Man', related='order_id.salesman_id')
    date_order = fields.Datetime(string='Current Date', related='order_id.create_date')
    amount_total = fields.Float(string='Total', digits=(16, 3))

    # @api.depends('order_id')
    # def _onchange_amount_total(self):
    #     self.amount_total = self.order_id.total_net
    #     print(self.amount_total)
    #
