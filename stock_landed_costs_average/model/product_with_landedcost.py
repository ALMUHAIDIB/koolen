# -*- coding: utf-8 -*-

from odoo import models, fields


class Product_with_landedcost(models.Model):
    _name = "product.product.withlandedcost"

    price_unit=fields.Float()
    product_id=fields.Many2one('product.product')
    # location_id=fields.Many2one('stock.location')

    _sql_constraints = [
        ('product_id_unique', 'unique(product_id)', 'product_id already available, need to update price_unit value')
    ]