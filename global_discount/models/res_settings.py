from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    enable_discount = fields.Boolean(string="Activate Universal Discount")
    sales_discount_account = fields.Many2one('account.account', string="Sales Discount Account")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_discount = fields.Boolean(string="Activate Universal Discount", related='company_id.enable_discount', readonly=False)
    sales_discount_account = fields.Many2one('account.account', related='company_id.sales_discount_account', string="Sales Discount Account", readonly=False)