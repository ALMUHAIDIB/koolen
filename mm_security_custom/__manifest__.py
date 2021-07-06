# -*- coding: utf-8 -*-
{
    'name': "MM Security custom",

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','account_accountant','sale','sales_team'],

    # always loaded
    'data': [
        'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/server_actions_menus.xml',
        'views/account.xml',
        'views/sale_order_inherit.xml',
        'views/res_users_inherit.xml'

    ],
}