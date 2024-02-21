# -*- coding: utf-8 -*-
###################################################################################

# Author       :  sayooj t k
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

{
    "name": "Product",
    "summary": """ Product """,
    "category": "Zinfog",
    "version": "16.0.1.0.0",
    "author": "Zinfog Codelabs Pvt Ltd",
    "license": "LGPL-3",
    "website": "https://www.zinfog.com",
    "description": """ Product """,
    "depends": ['base', 'product'],
    "data": [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/menu.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
