# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abdul Hakeem
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

{
    "name": "Cash Memo",
    "summary": """ Cash Memo """,
    "category": "Zinfog",
    "version": "16.0.1.0.0",
    "author": "Zinfog Codelabs Pvt Ltd",
    "license": "LGPL-3",
    "website": "https://www.zinfog.com",
    "description": """ Cash Memo """,
    "depends": ['base', 'mail', 'sales_team', 'account_payment', 'utm', 'sale_management', 'zcl_quotations', 'zcl_contacts', 'zcl_sale_inherited','zcl_shop','zcl_invoice'],
    "data": [
        "views/cash_memo.xml",
        "views/menu.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
