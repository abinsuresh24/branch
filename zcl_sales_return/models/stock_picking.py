from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import date, datetime
from odoo.exceptions import UserError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    return_bool = fields.Boolean(string="Return Receipts")

    @api.onchange('return_bool')
    def _onchange_return_bool(self):
        if self.return_bool:
            returns = self.env['stock.picking.type'].search([('return_bool', '=', True)])
            if len(returns) >= 1:
                raise UserError(_("Its Already One Form Is True"))

