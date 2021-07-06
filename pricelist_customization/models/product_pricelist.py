# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PriceListItemInherit(models.Model):
    _inherit = "product.pricelist.item"

    @api.depends('categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price',
                 'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        for item in self:

            if item.categ_id:
                item.name = _("Category: %s") % (item.categ_id.name)
            elif item.product_tmpl_id:
                # item.name = item.product_tmpl_id.name
                item.name = list(item.product_tmpl_id.name_get()[0])[-1]
            elif item.product_id:
                # item.name = item.product_id.display_name.replace('[%s]' % item.product_id.code, '')
                item.name = list(item.product_id.name_get()[0])[-1]
            else:
                item.name = _("All Products")

            if item.compute_price == 'fixed':
                item.price = ("%s %s") % (item.fixed_price, item.pricelist_id.currency_id.name)
            elif item.compute_price == 'percentage':
                item.price = _("%s %% discount") % (item.percent_price)
            else:
                item.price = _("%s %% discount and %s surcharge") % (item.price_discount, item.price_surcharge)

    @api.onchange('product_tmpl_id')
    def product_tmpl_id_onchange(self):
        if self.product_tmpl_id:
            if self.product_tmpl_id in self.pricelist_id.item_ids[:-2].mapped('product_tmpl_id'):
                raise ValidationError(_("Product {0} is already in the PriceList".format(list(self.product_tmpl_id.name_get()[0])[-1])))




