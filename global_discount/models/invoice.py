from odoo import api, fields, models, _
from odoo.tools import (
    date_utils,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    frozendict,
    get_lang,
    is_html_empty,
    sql
)
from contextlib import ExitStack, contextmanager
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning

# class AccountMoveLine(models.Model):
#     _name = "account.move.line"

    # display_type = fields.Selection(selection_add=[('global_discount', 'Global Discount')])
    # display_type = fields.Selection(
    #     selection=[
    #         ('product', 'Product'),
    #         ('cogs', 'Cost of Goods Sold'),
    #         ('tax', 'Tax'),
    #         ('rounding', "Rounding"),
    #         ('payment_term', 'Payment Term'),
    #         ('line_section', 'Section'),
    #         ('line_note', 'Note'),
    #         ('epd', 'Early Payment Discount'),
    #         ('global_discount','Global Discount')
    #     ],
    #     compute='_compute_display_type', store=True, readonly=False, precompute=True,
    #     required=True,)


class Invoice(models.Model):
    _inherit = "account.move"

    universal_discount_enable = fields.Boolean(string='Universal Discount')
    universal_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
                                               string='Universal Discount Type',
                                               default='percent')
    universal_discount_rate = fields.Float(string='Universal Discount', store=True,
                                           track_visibility='always')
    universal_discount_amount = fields.Monetary(string='Universal Discount',
                                                store=True,
                                                track_visibility='always')
    universal_total_display_discount_amount = fields.Monetary(string='Universal Discount', store=True)
    is_sale_order = fields.Boolean(default=True)
    discount_apply = fields.Boolean()

    def discount_apply_amount(self):
        for move in self:
            total_untaxed, total_untaxed_currency = 0.0, 0.0
            total_tax, total_tax_currency = 0.0, 0.0
            total_residual, total_residual_currency = 0.0, 0.0
            total, total_currency = 0.0, 0.0

            for line in move.line_ids:
                if move.is_invoice(True):
                    # === Invoices ===
                    if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type in ('product', 'rounding'):
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type == 'payment_term':
                        # Residual amount
                        if move.universal_discount_enable:
                            total_residual = move._compute_universal_total_display_discount_amount()
                            total_residual_currency = move._compute_universal_total_display_discount_amount()
                        else:
                            total_residual += line.amount_residual
                            total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            sign = move.direction_sign
            move.amount_untaxed = sign * total_untaxed_currency
            move.amount_tax = sign * total_tax_currency
            move.amount_total = sign * total_currency
            move.amount_tax_signed = -total_tax

            if move.universal_discount_enable:
                move.amount_untaxed_signed = move._compute_universal_total_display_discount_amount()
                move.amount_total_signed = abs(
                    total + move.universal_total_display_discount_amount) if move.move_type == 'entry' else -(
                        total + move.universal_total_display_discount_amount)
                move.amount_total_in_currency_signed = abs(
                    total + move.universal_total_display_discount_amount) if move.move_type == 'entry' else -(
                        total + move.universal_total_display_discount_amount)
                move.amount_residual = abs(total + move.universal_total_display_discount_amount)
                move.amount_residual_signed = abs(total + move.universal_total_display_discount_amount)
            else:
                move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
                move.amount_untaxed_signed = -total_untaxed
                move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(
                        sign * move.amount_total)
                move.amount_residual = -sign * total_residual_currency
                move.amount_residual_signed = total_residual

    def amount_tax_totals(self):
        for move in self:
            if move.is_invoice(include_receipts=True):
                base_lines = move.invoice_line_ids.filtered(lambda line: line.display_type == 'product')
                base_line_values_list = [line._convert_to_tax_base_line_dict() for line in base_lines]
                sign = move.direction_sign
                if move.id:
                    base_line_values_list += [
                        {
                            **line._convert_to_tax_base_line_dict(),
                            'handle_price_include': False,
                            'quantity': 1.0,
                            'price_unit': sign * line.amount_currency,
                        }
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'epd')
                    ]

                kwargs = {
                    'base_lines': base_line_values_list,
                    'currency': move.currency_id or move.journal_id.currency_id or move.company_id.currency_id,
                }

                if move.id:
                    kwargs['tax_lines'] = [
                        line._convert_to_tax_line_dict()
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'tax')
                    ]
                else:
                    epd_aggregated_values = {}
                    for base_line in base_lines:
                        if not base_line.epd_needed:
                            continue
                        for grouping_dict, values in base_line.epd_needed.items():
                            epd_values = epd_aggregated_values.setdefault(grouping_dict, {'price_subtotal': 0.0})
                            epd_values['price_subtotal'] += values['price_subtotal']

                    for grouping_dict, values in epd_aggregated_values.items():
                        taxes = None
                        if grouping_dict.get('tax_ids'):
                            taxes = self.env['account.tax'].browse(grouping_dict['tax_ids'][0][2])

                        kwargs['base_lines'].append(self.env['account.tax']._convert_to_tax_base_line_dict(
                            None,
                            partner=move.partner_id,
                            currency=move.currency_id,
                            taxes=taxes,
                            price_unit=values['price_subtotal'],
                            quantity=1.0,
                            account=self.env['account.account'].browse(grouping_dict['account_id']),
                            analytic_distribution=values.get('analytic_distribution'),
                            price_subtotal=values['price_subtotal'],
                            is_refund=move.move_type in ('out_refund', 'in_refund'),
                            handle_price_include=False,
                        ))

                total_tax_calculation = self.env['account.tax']._prepare_tax_totals(**kwargs)

                if self.universal_discount_enable:
                    total_amount_calculated = self._compute_universal_total_display_discount_amount()
                    total_tax_calculation['amount_untaxed'] = total_amount_calculated
                    move.tax_totals = total_tax_calculation
                else:
                    move.tax_totals = total_tax_calculation

                if move.invoice_cash_rounding_id:
                    rounding_amount = move.invoice_cash_rounding_id.compute_difference(move.currency_id,
                                                                                       move.tax_totals['amount_total'])
                    totals = move.tax_totals
                    totals['display_rounding'] = True
                    if rounding_amount:
                        if move.invoice_cash_rounding_id.strategy == 'add_invoice_line':
                            totals['rounding_amount'] = rounding_amount
                            totals['formatted_rounding_amount'] = formatLang(self.env, totals['rounding_amount'],
                                                                             currency_obj=move.currency_id)
                            totals['amount_total_rounded'] = totals['amount_total'] + rounding_amount
                            totals['formatted_amount_total_rounded'] = formatLang(self.env,
                                                                                  totals['amount_total_rounded'],
                                                                                  currency_obj=move.currency_id)
                        elif move.invoice_cash_rounding_id.strategy == 'biggest_tax':
                            if totals['subtotals_order']:
                                max_tax_group = max((
                                    tax_group
                                    for tax_groups in totals['groups_by_subtotal'].values()
                                    for tax_group in tax_groups
                                ), key=lambda tax_group: tax_group['tax_group_amount'])
                                max_tax_group['tax_group_amount'] += rounding_amount
                                max_tax_group['formatted_tax_group_amount'] = formatLang(self.env, max_tax_group[
                                    'tax_group_amount'], currency_obj=move.currency_id)
                                totals['amount_total'] += rounding_amount
                                totals['formatted_amount_total'] = formatLang(self.env, totals['amount_total'],
                                                                              currency_obj=move.currency_id)
            else:
                move.tax_totals = None

    def _compute_universal_total_display_discount_amount(self):
        total_amount = float(sum(self.invoice_line_ids.mapped('price_subtotal')))
        if self.universal_discount_type == "amount":
            self.universal_total_display_discount_amount = self.universal_discount_amount if 0 < self.universal_discount_amount <= total_amount else 0
        elif self.universal_discount_type == "percent":
            self.universal_total_display_discount_amount = (
                                                                   total_amount * self.universal_discount_rate) / 100 if 0 < self.universal_discount_rate <= 100 else 0
        else:
            self.universal_total_display_discount_amount = 0
        return total_amount - self.universal_total_display_discount_amount

    def apply_discount_items(self):
        for rec in self:
            sales_discount_account = rec.company_id.sales_discount_account.id
            if not sales_discount_account:
                raise UserError(_("Choose A Discount Account"))
            rec.discount_apply_amount()
            rec.amount_tax_totals()
            total_line = self.env['account.move.line'].search([('move_id','=', rec.id),('display_type','=','payment_term')])
            already_exsist = self.env['account.move.line'].search([('move_id','=', rec.id),('name','=','Discount'), ('display_type','=','epd')])
            if rec.move_type == 'out_invoice':
                amount = total_line.debit - rec.universal_discount_amount
                if not already_exsist:
                    vals = {
                        'name': 'Discount',
                        'move_id': rec.id,
                        'account_id': int(sales_discount_account),
                        'debit': rec.universal_total_display_discount_amount,
                        'credit': 0,
                        'display_type': 'epd',
                    }
                    new_line = self.env['account.move.line'].create(vals)
                else:
                    already_exsist.write({'debit': rec.universal_total_display_discount_amount})
                # new_line.write({'debit': rec.universal_discount_amount})
                rec.discount_apply_amount()


    @contextmanager
    def _check_balanced(self, container):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
            yield
            if disabled:
                return

        unbalanced_moves = self._get_unbalanced_moves(container)
        if unbalanced_moves and not self.move_type == 'out_invoice':
            error_msg = _("An error has occurred.")
            for move_id, sum_debit, sum_credit in unbalanced_moves:
                move = self.browse(move_id)
                error_msg += _(
                    "\n\n"
                    "The move (%s) is not balanced.\n"
                    "The total of debits equals %s and the total of credits equals %s.\n"
                    "You might want to specify a default account on journal \"%s\" to automatically balance each move.",
                    move.display_name,
                    format_amount(self.env, sum_debit, move.company_id.currency_id),
                    format_amount(self.env, sum_credit, move.company_id.currency_id),
                    move.journal_id.name)
            raise UserError(error_msg)
        elif unbalanced_moves and self.discount_apply:
            error_msg = _("An error has occurred.")
            for move_id, sum_debit, sum_credit in unbalanced_moves:
                move = self.browse(move_id)
                error_msg += _(
                    "\n\n"
                    "The move (%s) is not balanced.\n"
                    "The total of debits equals %s and the total of credits equals %s.\n"
                    "You might want to specify a default account on journal \"%s\" to automatically balance each move.",
                    move.display_name,
                    format_amount(self.env, sum_debit, move.company_id.currency_id),
                    format_amount(self.env, sum_credit, move.company_id.currency_id),
                    move.journal_id.name)
            raise UserError(error_msg)

    def action_post(self):
        self.discount_apply = True
        if self.universal_discount_rate:
            self.apply_discount_items()
        if self.ks_global_tax_rate:
            self.amount_button()
        return super().action_post()