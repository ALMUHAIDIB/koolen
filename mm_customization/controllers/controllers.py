# -*- coding: utf-8 -*-
from odoo import http

# class MmCustomization(http.Controller):
#     @http.route('/mm_customization/mm_customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mm_customization/mm_customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mm_customization.listing', {
#             'root': '/mm_customization/mm_customization',
#             'objects': http.request.env['mm_customization.mm_customization'].search([]),
#         })

#     @http.route('/mm_customization/mm_customization/objects/<model("mm_customization.mm_customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mm_customization.object', {
#             'object': obj
#         })