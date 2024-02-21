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
    "name"         : "Quotation",
    "summary"      : """ Quotation """,
    "category"     : "Zinfog",
    "version"      : "16.0.1.0.0",
    "author"       : "Zinfog Codelabs Pvt Ltd",
    "license"      : "LGPL-3",
    "website"      : "https://www.zinfog.com",
    "description"  : """ Quotation """,
    "depends"      : ['base', 'mail','zcl_contacts','stock', 'account', 'sale_management','zcl_products','zcl_shop','zcl_sale_inherited'],
    "data"         : ['security/ir.model.access.csv',
                      'data/sequence.xml',
                      'views/sale_quotation_view.xml',
                      'views/menu.xml',
                      ],
    "application"  : True,
    "installable"  : True,
    "auto_install" : False,
}
