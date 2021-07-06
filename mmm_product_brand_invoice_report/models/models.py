# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductBrand(models.Model):
    _name = 'product.brand'

    name = fields.Char(required=True, string='Name')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(comodel_name="product.brand", string="Product Brand", required=False, )


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    # brand = fields.Char(string='Product Brand')
    product_brand_id = fields.Many2one(comodel_name="product.brand", string="Brand List", readonly=True)

    _depends = {
        'product.template': ['product_brand_id'],
    }

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", template.product_brand_id as product_brand_id"

