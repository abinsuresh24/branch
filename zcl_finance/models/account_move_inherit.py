from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    _rec_name = 'document_no'

    is_finance_journal = fields.Boolean()
    narration = fields.Char(string="Narration")
    document_no = fields.Char(string="Document No", readonly=True)
    show_info_button = fields.Boolean(default=False)
    is_hide_info = fields.Boolean()

    @api.model
    def create(self, vals_list):
        """Declaring function for creating unique sequence number
        for each journal entry"""
        if vals_list.get('document_no', 'New') == 'New':
            vals_list['document_no'] = self.env['ir.sequence'].next_by_code(
                'journal.entry.sequence') or 'New'
        result = super().create(vals_list)
        return result

    def action_reconcile(self):
        self.show_info_button = True
        if self.show_info_button:
            self.is_hide_info = False

    def action_reconciled_view(self):

        return {
            'name': 'Journal Info Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'journal.information.wizard',
            'view_mode': 'form',
            # 'view_id': self.env.ref('zcl_finance.journal_information_wizard_form').id,
            'target': 'new',
            'context': {'default_journal_name': self.document_no,
                        'default_date': self.date,
                        'default_total_debit': sum(line.debit for line in self.line_ids),
                        'default_total_credit': sum(line.debit for line in self.line_ids)}
        }


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    serial_no = fields.Integer(string="Sno", compute='_get_line_numbers')
    branch_id = fields.Many2one('res.branch', string="Branch", readonly=False)
    description = fields.Char(string="Description")
    reference = fields.Char(string="Reference")
    remark = fields.Char(string="Remark")

    @api.depends('move_id.line_ids')
    def _get_line_numbers(self):
        for line in self:
            number = 0
            line.serial_no = number
            for l in line.move_id.line_ids:
                number += 1
                l.serial_no = number
