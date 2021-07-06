# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class mm_product_pricelist_tree_inherit(models.Model):
#     _name = 'mm_product_pricelist_tree_inherit.mm_product_pricelist_tree_inherit'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100