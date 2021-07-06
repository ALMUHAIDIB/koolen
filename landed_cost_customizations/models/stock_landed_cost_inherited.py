# -*- coding: utf-8 -*-

from odoo import models, fields, api


class stock_landed_cost_inherited(models.Model):
    _inherit = 'stock.landed.cost'

    purchase_order_id = fields.Many2one('purchase.order')

    @api.onchange('purchase_order_id')
    def _get_domain_for_pickings(self):
        relation_ids = self.purchase_order_id.picking_ids.ids
        return {'domain': {'picking_ids': [('id', 'in', relation_ids)]}}

    @api.onchange('picking_ids')
    def _get_domain_for_invoices(self):
        invoice_ids = self.env['account.move'].search([('purchase_order_id', '=', self.purchase_order_id.id)]).ids
        return {'domain': {'invoice_ids': [('id', 'in', invoice_ids)]}}
