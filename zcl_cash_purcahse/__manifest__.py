# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abin suresh
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

{
    "name": "Cash Purchase",
    "summary": """ Cash Purchase """,
    "category": "Zinfog",
    "version": "16.0.1.0.0",
    "author": "Zinfog Codelabs Pvt Ltd",
    "license": "LGPL-3",
    "website": "https://www.zinfog.com",
    "description": """ Cash Purchase """,
    "depends": ['base', 'zcl_store', 'product', 'zcl_shop', 'account', 'purchase'],
    "data": [
        'views/purchase_order_view.xml',
        # 'views/internal_do_view.xml',
        'views/grn_local_import.xml',
        'views/purchase_local_import.xml',
        'views/menus.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
