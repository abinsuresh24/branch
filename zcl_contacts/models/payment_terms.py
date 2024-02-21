# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Anagha VP
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models


class PaymentTerms(models.Model):
    _name = 'payments.terms'
    _description = "Payment Terms"
    # _rec_name = "Payment Terms"

    name = fields.Char(string="Name")