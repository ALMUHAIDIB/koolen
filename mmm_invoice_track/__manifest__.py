# -*- coding: utf-8 -*-
{
    'name': "mmm_invoice_track",
    'author': "Centione",
    'website': "http://www.centione.com",

    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/invoice_track.xml',
        'views/car_model.xml',
        'views/account_invoice.xml',
    ]
}
