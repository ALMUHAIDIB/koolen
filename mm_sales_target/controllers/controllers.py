# -*- coding: utf-8 -*-
from odoo import http

# class MmSalesTarget(http.Controller):
#     @http.route('/mm_sales_target/mm_sales_target/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mm_sales_target/mm_sales_target/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mm_sales_target.listing', {
#             'root': '/mm_sales_target/mm_sales_target',
#             'objects': http.request.env['mm_sales_target.mm_sales_target'].search([]),
#         })

#     @http.route('/mm_sales_target/mm_sales_target/objects/<model("mm_sales_target.mm_sales_target"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mm_sales_target.object', {
#             'object': obj
#         })