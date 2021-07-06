# -*- coding: utf-8 -*-
{
    'name': "new_custom_invoice",

    'summary': """
        new custom invoice template for customer invoices""",

    'author': "Centione",
    'website': "http://www.centione.com",

    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'stock', 'product', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/partner.xml',
        'views/account_invoice.xml',
        'views/product.xml',
        'views/views.xml',
        'views/stock.xml',
        'views/sale.xml',
        'views/report_payment_receipt.xml',
    ],
}