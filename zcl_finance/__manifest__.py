# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Sayooj T K
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

{
    "name": "Finance",
    "summary": """ Finance """,
    "category": "Zinfog",
    "version": "16.0.1.0.0",
    "author": "Zinfog Codelabs Pvt Ltd",
    "license": "LGPL-3",
    "website": "https://www.zinfog.com",
    "description": """ Finance """,
    "depends": ['base', 'contacts','zcl_invoice','account',],
    "data": ['security/security.xml',
             'security/ir.model.access.csv',
             'data/sequence.xml',
             'views/customers.xml',
             'views/finance_view.xml',
             'views/bank_receipt.xml',
             'views/account_move_view.xml',
             'views/products.xml',
             'wizard/customer_invoice_wizard_view.xml',
             'wizard/journal_info_wizard_view.xml',
             'views/menu.xml'
             ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
