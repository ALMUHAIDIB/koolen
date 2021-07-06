# -*- coding: utf-8 -*-

from odoo import models,  fields, api




class ProductTemplate(models.Model):
    _inherit = 'product.template'

    custom_product_variant_id = fields.Many2one('product.product', 'Product',
                                                compute='_compute_custom_product_variant_id', store='True')

    @api.depends('product_variant_ids')
    def _compute_custom_product_variant_id(self):
        for p in self:
            p.custom_product_variant_id = p.product_variant_ids[:1].id

