
{
    "name": "Global Discount",
    "summary": """Global Discount for Odoo 16""",
    "license": 'LGPL-3',
    "version": "16",
    'sequence': 2,
    "category": "Extra Sale",
    'website': 'www.zinfog.com',
    'author': 'Zinfog',
    "depends": [
        "base", "sale", "sale_management", "account"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/invoice.xml",
        "views/res_settings.xml",
    ],
    "qweb": [
    ],
    "images": [
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    
}