# -*- coding: utf-8 -*-
{
    'name': "landed_cost_customizations",

    'summary': """Landed Costs Average customization
        """,

    'description': """
        Landed Costs Average customization
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'stock_landed_costs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/account_invoice_inherited.xml',
        'views/stock_landed_cost_inherited.xml',
        # 'views/templates.xml',
    ]
}
