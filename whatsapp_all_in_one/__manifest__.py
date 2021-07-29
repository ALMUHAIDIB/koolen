# -*- coding: utf-8 -*-
{
    'name': 'All In One WhatsApp Odoo Integration',
    'version': '14.0.1.0.0',
    'category': 'Tools',
    'author': 'Ascents Entrepreneurs',
    'license': 'OPL-1',
    'summary': 'All in One WhatsApp Integration with Odoo',
    'description': """
This module can be used to send messages to WhatsApp
----------------------------------------------------
Send Messages via WhatsApp
WhatsApp All in One Module
""",
    'depends': ['base', 'base_setup', 'contacts', 'account', 'sale_management', 'purchase', 'delivery', 'website_sale', 'point_of_sale'],
    'data': [
        'data/whatsapp_cron.xml',
        'security/ir.model.access.csv',
        'wizard/send_wp_msg_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_inovice_form_wa_inherited.xml',
        'views/account_payment_form_wa_inherited.xml',
        'views/pos_config_views.xml',
        'views/purchase_order_form_wa_inherited.xml',
        'views/sale_order_form_wa_inherited.xml',
        'views/stock_picking_form_wa_inherited.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/mobile_widget.xml',
        'static/src/xml/pos_whatsapp.xml',
    ],
    'external_dependencies': {'python': ['phonenumbers', 'selenium']},
    'images': ['static/description/main_screenshot.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
    'currency': 'EUR',
    'price': 30,
}
