# -*- coding: utf-8 -*-
{
    'name': "Po Delivery",

    'summary': """
        custom shipment division method for the purchase orders""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'purchase_stock', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase.xml',
        'views/stock.xml',
    ],
}