# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Manjima V
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models, api, _
from odoo.tests import Form


class JournalInfoWizard(models.TransientModel):
    _name = "journal.information.wizard"
    _description = "Journal Information Wizard"

    total_debit = fields.Char(string='Total Debit', readonly=True)
    total_credit = fields.Char(string='Total Credit', readonly=True)
    journal_name = fields.Char(string='Journal Entry', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    is_unreconcile = fields.Boolean()

    def journal_unreconciled(self):
        self.is_unreconcile = True
        active_id = self.env.context.get('active_id')
        account_move = self.env['account.move'].browse(active_id).exists()
        if self.is_unreconcile:
            account_move.is_hide_info = True
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
