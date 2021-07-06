# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    @api.depends('invoice_origin')
    def compute_sale_picking_ids(self):
        for record in self:
            if record.invoice_origin:
                sale_order = record.env['sale.order'].search([('name', '=', record.invoice_origin)])
                record.sale_picking_ids = [(6, 0, sale_order.picking_ids.ids)]
            else:
                record.sale_picking_ids = []

    @api.depends('invoice_line_ids', 'amount_untaxed')
    def get_discount_amount(self):
        for rec in self:
            rec.discount_amount = sum([x.quantity * x.price_unit * x.discount / 100 for x in rec.invoice_line_ids])
            rec.total_discount = rec.discount_amount + rec.amount_untaxed

    partner_limit_days = fields.Integer(related='parent_partner_id.credit_period', string='Customer Limit Days',
                                        readonly=True)

    sale_picking_ids = fields.Many2many(comodel_name='stock.picking', readonly=True, compute='compute_sale_picking_ids')

    parent_partner_id = fields.Many2one(comodel_name='res.partner', string='Customer')

    total_discount = fields.Monetary(string='Total Amount', compute="get_discount_amount")
    discount_amount = fields.Monetary(string='Discount Amount', compute="get_discount_amount")

    @api.onchange('parent_partner_id')
    def parent_partner_id_onchange(self):
        if self.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
            if self.parent_partner_id:
                return {'domain': {'partner_id': [('id', 'in', self.parent_partner_id.child_ids.ids)]}}
            else:
                return {'domain': {'partner_id': [('id', 'in', [])]}}

    def amount_to_text(self, amount):
        return self.currency_id.amount_to_text(amount)

    def sale_picking_to_text(self, sale_picking):
        sale_picking_text = ''
        for picking in sale_picking:
            sale_picking_text = sale_picking_text + picking.name + '  '
        return sale_picking_text


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    @api.depends('product_id')
    def compute_partner_sku(self):
        for record in self:
            if record.move_id.parent_partner_id and record.product_id:
                partner_id = record.move_id.parent_partner_id
                if partner_id.customer_product_sku:
                    for product in partner_id.customer_product_sku:
                        if record.product_id.id == product.name.id:
                            record.partner_sku = product.product_sku
                        else:
                            record.partner_sku = ''
                else:
                    record.partner_sku = ''
                record.barcode = record.product_id.barcode
            else:
                record.partner_sku = ''
                record.barcode = ''

    partner_sku = fields.Char(string='Customer SKU', readonly=True, compute='compute_partner_sku')
    barcode = fields.Char(string='Barcode', compute='compute_partner_sku')
