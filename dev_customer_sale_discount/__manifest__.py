# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

{
    'name': 'Customer based Discount On Sale',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Sales Management',
    'description':
        """ 
        Odoo app adds Customer  based discount on Sale
        
        odoo customer discount
        odoo customer based discount
        odoo sale discount
        odoo discount 
        odoo discount on sale 
        odoo customer discount on sale order 
 Customer based Discount On Sale
Odoo Customer based Discount On Sale
manage Customer based Discount On Sale
odoo manage Customer based Discount On Sale
odoo application add Customer based discount functionality on sale order screen
 odoo apps Define discount on customer screen which will redirect automatically on sale order line screen.
Manage customer discount on sale 
Odoo manage customer discount on sale 
Customer discount 
Manage customer discount 
Odoo manage customer discount 
Discount on sale 
Odoo Discount on sale 
Manage Discount on sale 
Odoo manage Discount on sale 
       
        
        
        
    """,
    'summary': 'Odoo app adds Customer based discount on Sale',
    'depends': ['base', 'sale', 'new_custom_invoice'],
    'data': [
        'views/res_customer_view.xml',

    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,

    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd',
    'support': 'devintelle@gmail.com',
    'price': 12.0,
    'currency': 'EUR',
    # 'live_test_url':'https://youtu.be/A5kEBboAh_k',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
