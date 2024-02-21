{
    'name': 'Invoices',
    'version': '16.0.1.0.0',
    'summary': 'Manage customer invoices and process payments',
    'description': 'A module to handle draft invoices of customers and process payments.',
    'author': "Zinfog codelabs",
    'depends': ['base', 'account', 'zcl_contacts', 'sale_management', 'zcl_direct_order','zcl_shop', 'zcl_direct_order'],
    'data': [
        'security/ir.model.access.csv',
        'views/invoice.xml',
        'views/cash_memo_invoice.xml',
        'views/cash_sale_invoice.xml',
        'views/return_invoice.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
