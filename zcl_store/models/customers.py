from odoo import models, api, _, fields


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"
    _description = "customers"

    is_store_customer = fields.Boolean(default=False, store=True)
    # is_confirmed = fields.Boolean(default=False, store=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Confirmed')],
                             string='Status', default='draft', required=True)
    sale_account_id = fields.Many2one('account.account',string="Sale Account",
                                      domain="[('name', '=', 'Account Receivable')]")


    def action_confirm(self):
        self.state = 'done'

    # STORE WISE CUSTOMER VIEW ACTION
    @api.model
    def action_store_customers_window(self):
        domain = [
            ('is_company', '!=', True),
            ('customer_true', '=', True),
            ('is_store_customer', '=', True),
            ('branch_id', 'in', self.env.user.branch_ids.ids),
        ]

        action = {
            'name': 'Customers',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'kanban,form',
            'view_ids': [
                (5, 0, 0),
                (0, 0, {'view_mode': 'kanban', 'view_id': self.env.ref('zcl_store.customers_kanban_view').id}),
                (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('zcl_store.view_zcl_customer_form').id}),
            ],
            'context': {'default_customer_true': True, 'default_is_store_customer': True},
            'domain': domain,
        }

        return action


