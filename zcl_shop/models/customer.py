from odoo import models, api, _,fields


class ResPartnerInherits(models.Model):
    _inherit = "res.partner"
    _description = "customers"

    is_shop_customer = fields.Boolean(default=False, store=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Confirmed')], string='Status', default='draft', required=True)
    shop_id = fields.Integer(string='shop')
    incentive_amount = fields.Float(string="Incentive Amount")

    def action_confirm(self):
        self.state = 'done'


# SHOP WISE CUSTOMER VIEW ACTION
    @api.model
    def action_open_customers_window(self):
        domain = [
            ('is_company', '!=', True),
            ('customer_true', '=', True),
            ('is_shop_customer', '=', True),
            ('branch_id', 'in', self.env.user.branch_ids.ids),
        ]

        action = {
            'name': 'Customers',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'kanban,form',
            'view_ids': [
                (5, 0, 0),
                (0, 0, {'view_mode': 'kanban', 'view_id': self.env.ref('zcl_shop.zcl_res_partner_kanban_view').id}),
                (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('zcl_shop.view_zcl_partner_form').id}),
            ],
            'context': {'default_customer_true': True, 'default_is_shop_customer': True},
            'domain': domain,
        }


        return action



