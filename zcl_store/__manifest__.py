# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Anoop Jayaprakash
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

{
    "name"         : "Store",
    "summary"      : """ Store """,
    "category"     : "Zinfog",
    "version"      : "16.0.1.0.0",
    "author"       : "Zinfog Codelabs Pvt Ltd",
    "license"      : "LGPL-3",
    "website"      : "https://www.zinfog.com",
    "description"  : """ Store """,
    "depends"      : ['base', 'product', 'stock', 'contacts','zcl_stock_inherited','branch'],
    "data"         : ['data/store_sequence.xml',
                      'data/store_data.xml',
                      'views/shop_products.xml',
                      'views/store_stock.xml',
                      'views/shop_stock.xml',
                      'views/customers.xml',
                      'views/store.xml',
                      'views/menu.xml'],
    "application"  : True,
    "installable"  : True,
    "auto_install" : False,
}
