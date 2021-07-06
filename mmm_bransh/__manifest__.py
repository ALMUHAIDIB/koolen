# -*- coding: utf-8 -*-
{
    'name': "mmm_bransh",
    'author': "Centione",
    'website': "http://www.centione.com",

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_form_view.xml',
        'views/res_partner_tree_view.xml',
        'views/res_partner_kanban_view_inherit.xml',
        'views/sale_order_form_inherit.xml',
        'views/account_invoice_inherit.xml',
        'views/views.xml',
        'views/templates.xml',
    ]
}
