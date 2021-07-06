# -*- coding: utf-8 -*-
{
    'name': "pricelist_customization",

    'summary': """
        product reference appear next to the product name pluse restriction to privent the product reception in the same pricelist """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}