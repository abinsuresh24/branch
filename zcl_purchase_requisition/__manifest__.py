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
    "name": "Purchase Requisition",
    "summary": """ Purchase Requisition """,
    "category": "Zinfog",
    "version": "16.0.1.0.0",
    "author": "Zinfog Codelabs Pvt Ltd",
    "license": "LGPL-3",
    "website": "https://www.zinfog.com",
    "description": """ Purchase Requisition """,
    "depends": ['base', 'mail', 'contacts', 'zcl_contacts','zcl_shop','zcl_store', 'zcl_purchase', 'purchase','product','zcl_products'],
    "data": ['security/ir.model.access.csv',
             'data/sequence.xml',
             'views/purchase_requisition.xml',
             'wizard/product_moves_wizard_view.xml',
             'views/menu.xml'
             ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
