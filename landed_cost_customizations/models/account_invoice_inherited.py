# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_invoice_inherited(models.Model):
    _inherit = 'account.move'

    is_landed_cost = fields.Boolean()
    purchase_order_id = fields.Many2one('purchase.order')
    picking_ids = fields.Many2many('stock.picking')

    @api.onchange('purchase_order_id')
    def _get_domain_for_pickings(self):
        relation_ids = self.purchase_order_id.picking_ids.ids
        return {'domain': {'picking_ids': [('id', 'in', relation_ids)]}}
