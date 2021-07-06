# -*- coding: utf-8 -*-

from odoo import models,  fields, api




class ProductProduct(models.Model):
    _inherit = 'product.product'




    # @api.multi
    def stock_card_move_get(self):
        self.ensure_one()
        scp_obj = self.env['stock.card.product']
        scp_brw = scp_obj.create({'product_id': self._ids})
        print("see stock.card.product")
        return scp_brw.stock_card_move_get()
