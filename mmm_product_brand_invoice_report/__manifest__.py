# -*- coding: utf-8 -*-
{
    'name': "MMM Product Brand Invoice Report",
    'depends': ['base', 'account', 'product', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ]
}