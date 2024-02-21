from odoo import api, fields, models, _


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            user = self.env.user
            if not vals.get('name') or vals['name'] == _('New'):
                if vals.get('shop_true') == True or vals.get('store_true') == True:
                    if user.branch_id.purchase_requisition_prefix:
                        do_prefix = self.env['ir.sequence'].search(
                            [('code', '=', user.branch_id.purchase_requisition_prefix)])
                        if do_prefix:
                            vals['name'] = self.env['ir.sequence'].next_by_code(
                                do_prefix.code) or _('New')
                else:
                    print("d")
        return super().create(vals_list)


class MaterialRequisition(models.Model):
    _inherit = 'material.request'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            user = self.env.user
            if not vals.get('name') or vals['name'] == _('New'):
                if vals.get('shop_true') == True or vals.get('store_true') == True:
                    if user.branch_id.material_requisition_prefix:
                        do_prefix = self.env['ir.sequence'].search(
                            [('code', '=', user.branch_id.material_requisition_prefix)])
                        if do_prefix:
                            vals['name'] = self.env['ir.sequence'].next_by_code(
                                do_prefix.code) or _('New')
                else:
                    print("d")
        return super().create(vals_list)