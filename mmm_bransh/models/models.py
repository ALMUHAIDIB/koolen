# -*- coding: utf-8 -*-
#
# from odoo import models, fields, api
#
# class sale_order_inherit(models.Model):
#     _inherit = 'sale.order'
#
#
#     partner_id = fields.Many2one('res.partner', string='Customer', readonly=True,
#                              states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True,
#                              change_default=True, index=True,domain=[('company_type','=','company')], track_visibility='always', track_sequence=1,
#                              help="You can find a customer by its Name, TIN, Email or Internal Reference.")