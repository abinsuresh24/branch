from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date, formatLang


class KsGlobalTaxInvoice(models.Model):
    _inherit = "account.move"

    ks_global_tax_rate = fields.Float(string='Universal Tax (%):', readonly=True,
                                      states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    ks_amount_global_tax = fields.Monetary(string="Universal Tax", readonly=True, track_visibility='always')
    ks_enable_tax = fields.Boolean(compute='ks_verify_tax')
    ks_sales_tax_account_id = fields.Integer(compute='ks_verify_tax')
    ks_purchase_tax_account_id = fields.Integer(compute='ks_verify_tax')

    @api.depends('company_id.ks_enable_tax')
    def ks_verify_tax(self):
        for rec in self:
            rec.ks_enable_tax = rec.company_id.ks_enable_tax
            rec.ks_sales_tax_account_id = rec.company_id.ks_sales_tax_account.id
            rec.ks_purchase_tax_account_id = rec.company_id.ks_purchase_tax_account.id


    def amount_button(self):
        for rec in self:
            rec.ks_calculate_tax()
        #     if 'ks_amount_discount' in rec:
        #         rec.ks_calculate_discount()

            # rec.ks_calculate_tax()
            rec.ks_update_universal_tax()
            sign = rec.move_type in ['in_refund', 'out_refund'] and -1 or 1
            # rec.amount_total_company_signed = rec.amount_total * sign
            # rec.amount_total_signed = rec.amount_total * sign
            rec._compute_amount()


    def ks_calculate_tax(self):
        for rec in self:
            print(rec.amount_total, "==================================")
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.ks_global_tax_rate != 0.0 and rec.move_type in type_list:
            # if rec.ks_global_tax_rate != 0.0:
                price_sub_total = sum(rec.invoice_line_ids.mapped('price_subtotal'))
                rec.ks_amount_global_tax = ((price_sub_total - rec.universal_total_display_discount_amount) * rec.ks_global_tax_rate) / 100
            else:
                rec.ks_amount_global_tax = 0.0

            rec.amount_total = rec.ks_amount_global_tax + rec.amount_total

            rec.amount_residual = rec.ks_amount_global_tax + rec.amount_residual


    def ks_update_universal_tax(self):
        for rec in self:
            already_exists = self.line_ids.filtered(
                lambda line: line.name and line.name.find('Universal Tax') == 0)
            terms_lines = self.line_ids.filtered(
                lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
            other_lines = self.line_ids.filtered(
                lambda line: line.account_id.account_type not in ('asset_receivable', 'liability_payable'))
            if already_exists:
                amount = rec.ks_amount_global_tax
                if rec.ks_sales_tax_account_id \
                        and (rec.move_type == "out_invoice"
                             or rec.move_type == "out_refund")\
                        and rec.ks_global_tax_rate > 0:
                    if rec.move_type == "out_invoice":
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            # 'debit': amount > 0.0 and amount or 0.0,
                            # 'credit': amount < 0.0 and -amount or 0.0,
                        })
                amount = rec.ks_amount_global_tax
                if rec.ks_purchase_tax_account_id \
                        and (rec.move_type == "in_invoice"
                             or rec.move_type == "in_refund")\
                        and rec.ks_global_tax_rate > 0:

                    # rec.ks_calculate_tax()
                    if rec.move_type == "in_invoice":
                        already_exists.update({

                        })
                    else:
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                total_balance = sum(other_lines.mapped('balance'))
                total_amount_currency = sum(other_lines.mapped('amount_currency'))
                terms_lines.update({
                    'amount_currency': -total_amount_currency,
                    # 'debit': total_balance < 0.0 and -total_balance or 0.0,
                    # 'credit': total_balance > 0.0 and total_balance or 0.0,
                })
            if not already_exists and rec.ks_global_tax_rate > 0:
                in_draft_mode = self != self._origin
                if not in_draft_mode:
                    rec.ks_calculate_tax()
                    rec._recompute_universal_tax_lines()

    @api.constrains('ks_global_tax_rate')
    def ks_check_tax_value(self):
        if self.ks_global_tax_rate > 100 or self.ks_global_tax_rate < 0:
            raise ValidationError('You cannot enter percentage value greater than 100 or less than 0.')

#
    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        ks_res = super(KsGlobalTaxInvoice, self)._prepare_refund(invoice, date_invoice=None, date=None,
                                                                 description=None, journal_id=None)
        ks_res['ks_global_tax_rate'] = self.ks_global_tax_rate
        ks_res['ks_amount_global_tax'] = self.ks_amount_global_tax
        return ks_res

    # @api.onchange('ks_global_tax_rate', 'line_ids','ks_amount_global_tax')
    def _recompute_universal_tax_lines(self):
        for rec in self:

            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.ks_global_tax_rate > 0 and rec.move_type in type_list:
                if rec.is_invoice(include_receipts=True):
                    in_draft_mode = self != self._origin
                    ks_name = "Universal Tax"
                    ks_name = ks_name + \
                              " @" + str(self.ks_global_tax_rate) + "%"
                    # ks_name = ks_name + " for " + \
                    #           ("Invoice No: " + str(self.ids)
                    #            if self._origin.id
                    #            else (self.display_name))
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
                    already_exists = self.line_ids.filtered(
                                    lambda line: line.name and line.name.find('Universal Tax') == 0)
                    if already_exists:
                        amount = self.ks_amount_global_tax
                        if self.ks_sales_tax_account_id \
                                and (self.move_type == "out_invoice"
                                     or self.move_type == "out_refund"):
                            already_exists.update({
                                'name': ks_name,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                            })
                        if self.ks_purchase_tax_account_id\
                                and (self.move_type == "in_invoice"
                                     or self.move_type == "in_refund"):
                            already_exists.update({
                                'name': ks_name,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                            })
                    else:
                        new_tax_line = self.env['account.move.line']
                        create_method = in_draft_mode and \
                                        self.env['account.move.line'].new or\
                                        self.env['account.move.line'].create

                        if self.ks_sales_tax_account_id \
                                and (self.move_type == "out_invoice"
                                     or self.move_type == "out_refund"):
                            amount = self.ks_amount_global_tax
                            dict = {
                                    'move_name': self.name,
                                    'name': ks_name,
                                    # 'name': ks_name,
                                    # 'sequence':True,
                                    'price_unit': self.ks_amount_global_tax,
                                    'quantity': 1,
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                    'account_id': self.ks_purchase_tax_account_id,
                                    'move_id': self._origin,
                                    'date': self.date,
                                    'display_type':('tax'),
                            #
                            #         ('product', 'Product'),
                            #     ('cogs', 'Cost of Goods Sold'),
                            # ('tax', 'Tax'),
                            # ('rounding', "Rounding"),
                            # ('payment_term', 'Payment Term'),
                            # ('line_section', 'Section'),
                            # ('line_note', 'Note'),
                            # ('epd', 'Early Payment Discount')
                                    # 'exclude_from_invoice_tab': True,
                                    'partner_id': terms_lines.partner_id.id,
                                    'company_id': terms_lines.company_id.id,
                                    'company_currency_id': terms_lines.company_currency_id.id,
                                    }
                            if self.move_type == "out_invoice":
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            if in_draft_mode:
                                self.line_ids += create_method(dict)
                                # Updation of Invoice Line Id
                                duplicate_id = self.invoice_line_ids.filtered(
                                    lambda line: line.name and line.name.find('Universal Tax') == 0)
                                self.invoice_line_ids = self.invoice_line_ids - duplicate_id
                            else:
                                dict.update({
                                    # 'price_unit': 0.0,
                                    # 'debit': 0.0,
                                    # 'credit': 0.0,
                                })
                                self.line_ids = [(0, 0, dict)]
                                if self.line_ids[0].tax_ids.amount !=False:
                                    pass
                                else:
                                    self.line_ids[-1].tax_ids = False
                                # self.line_ids[-1].account_id.display_name=False
                                # self.line_ids[1].account_id.display_name == False
                                # self.line_ids[-1].tax_ids.amount == 0
                                # self.line_ids[1].tax_ids.display_name == False
                                # self.line_ids[1].account_type == False

                                # self.line_ids.account_id.display_name ==False
                                # self.line_ids[1].account_id.code == False
                                # self.line_ids[1].quantity = False

                        if self.ks_purchase_tax_account_id\
                                and (self.move_type == "in_invoice"
                                     or self.move_type == "in_refund"):
                            # self.ks_calculate_tax()
                            amount = self.ks_amount_global_tax
                            dict = {
                                    'move_name': self.name,
                                    'name': ks_name,
                                    'price_unit': self.ks_amount_global_tax,
                                    'quantity': 1,
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                    'account_id': self.ks_sales_tax_account_id,
                                    'move_id': self.id,
                                    'date': self.date,
                                    'sequence': True,
                                    'display_type': ('tax'),
                                    # 'exclude_from_invoice_tab': True,
                                    'partner_id': terms_lines.partner_id.id,
                                    'company_id': terms_lines.company_id.id,
                                    'company_currency_id': terms_lines.company_currency_id.id,
                                    }

                            if self.move_type == "in_invoice":
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            if in_draft_mode:
                                self.line_ids += create_method(dict)
                                # Updation of Invoice Line Id
                                duplicate_id = self.invoice_line_ids.filtered(
                                    lambda line: line.name and line.name.find('Universal Tax') == 0)
                                self.invoice_line_ids = self.invoice_line_ids - duplicate_id
                            else:
                                dict.update({
                                    # 'price_unit': 0.0,
                                    # 'debit': 0.0,
                                    # 'credit': 0.0,
                                })
                                self.line_ids = [(0, 0, dict)]
                                # self.line_ids = [(0, 0, dict)]
                                if self.line_ids[0].tax_ids.amount != False:
                                    pass
                                else:
                                    self.line_ids[-1].tax_ids = False
                                # self.line_ids[-1].tax_ids = False
                                # # self.line_ids[1].account_id.display_name == False
                                # self.line_ids.tax_ids.amount == 0
                                # self.line_ids.tax_ids.display_name == False
                                # # self.line_ids[1].account_type == False
                                # self.line_ids[1].tax_ids = False
                                # self.line_ids.account_id.display_name == False
                                # self.line_ids[1].account_id.code == False

                    if in_draft_mode:
                        # Update the payement account amount
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type not in ('asset_receivable', 'liability_payable'))
                        total_balance = sum(other_lines.mapped('balance'))
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        terms_lines.update({
                                    'amount_currency': -total_amount_currency,
                                    'debit': total_balance < 0.0 and -total_balance or 0.0,
                                    'credit': total_balance > 0.0 and total_balance or 0.0,
                                })
                    else:
                        amount = self.ks_amount_global_tax
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type not in ('asset_receivable', 'liability_payable'))
                        already_exists = self.line_ids.filtered(
                            lambda line: line.name and line.name.find('Universal Tax') == 0)
                        total_balance = sum(other_lines.mapped('balance'))
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        dict1 = {
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                        }
                        dict2 = {
                                'debit': total_balance < 0.0 and -total_balance or 0.0,
                                'credit': total_balance > 0.0 and total_balance or 0.0,
                                }
                        if terms_lines:
                            self.line_ids = [(1, already_exists.id, dict1), (1, terms_lines[0].id, dict2)]
                        print()

            elif self.ks_global_tax_rate <= 0:
                already_exists = self.line_ids.filtered(
                    lambda line: line.name and line.name.find('Universal Tax') == 0)
                if already_exists:
                    self.line_ids -= already_exists
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
                    other_lines = self.line_ids.filtered(
                        lambda line: line.account_id.account_type not in ('asset_receivable', 'liability_payable'))
                    total_balance = sum(other_lines.mapped('balance'))
                    total_amount_currency = sum(other_lines.mapped('amount_currency'))
                    terms_lines.update({
                        'amount_currency': -total_amount_currency,
                        'debit': total_balance < 0.0 and -total_balance or 0.0,
                        'credit': total_balance > 0.0 and total_balance or 0.0,
                    })


    def _get_unbalanced_moves(self, container):
        return



    # def _compute_tax_totals(self):
    #     res = super(KsGlobalTaxInvoice, self)._compute_tax_totals()
    #     self.tax_totals['formatted_amount_total'] = formatLang(self.env, self.amount_total,currency_obj=self.currency_id)
    #     self.tax_totals['amount_total'] = self.amount_total
    #     self.tax_totals['ks_tax_amount'] = formatLang(self.env, self.ks_amount_global_tax, currency_obj=self.currency_id)

    def _compute_tax_totals(self):
        res = super(KsGlobalTaxInvoice, self)._compute_tax_totals()
        if self.tax_totals == True:
            self.tax_totals['formatted_amount_total'] = formatLang(self.env, self.amount_total,
                                                                   currency_obj=self.currency_id)
            self.tax_totals['amount_total'] = self.amount_total
            self.tax_totals['ks_tax_amount'] = formatLang(self.env, self.ks_amount_global_tax,
                                                          currency_obj=self.currency_id)
