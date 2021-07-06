# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    parent_partner_id = fields.Many2one(comodel_name='res.partner', string='Customer',
                                        domain=[('is_company', '=', True)])

    @api.onchange('parent_partner_id')
    def parent_partner_id_onchange(self):
        if self.parent_partner_id:
            return {'domain': {'partner_id': [('id', 'in', self.parent_partner_id.child_ids.ids)]}}
        else:
            return {'domain': {'partner_id': [('id', 'in', [])]}}

    # def action_invoice_create(self, grouped=False, final=False):
    #     """
    #     Create the invoice associated to the SO.
    #     :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
    #                     (partner_invoice_id, currency)
    #     :param final: if True, refunds will be generated if necessary
    #     :returns: list of created invoices
    #     """
    #     inv_obj = self.env['account.invoice']
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     invoices = {}
    #     references = {}
    #     invoices_origin = {}
    #     invoices_name = {}
    #
    #     for order in self:
    #         group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
    #
    #         # We only want to create sections that have at least one invoiceable line
    #         pending_section = None
    #
    #         for line in order.order_line:
    #             if line.display_type == 'line_section':
    #                 pending_section = line
    #                 continue
    #             if float_is_zero(line.qty_to_invoice, precision_digits=precision):
    #                 continue
    #             if group_key not in invoices:
    #                 inv_data = order._prepare_invoice()
    #                 invoice = inv_obj.create(inv_data)
    #                 references[invoice] = order
    #                 invoices[group_key] = invoice
    #                 invoices_origin[group_key] = [invoice.origin]
    #                 invoices_name[group_key] = [invoice.name]
    #             elif group_key in invoices:
    #                 if order.name not in invoices_origin[group_key]:
    #                     invoices_origin[group_key].append(order.name)
    #                 if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
    #                     invoices_name[group_key].append(order.client_order_ref)
    #
    #             if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
    #                 if pending_section:
    #                     pending_section.invoice_line_create(invoices[group_key].id, pending_section.qty_to_invoice)
    #                     pending_section = None
    #                 line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
    #
    #         if references.get(invoices.get(group_key)):
    #             if order not in references[invoices[group_key]]:
    #                 references[invoices[group_key]] |= order
    #
    #     for group_key in invoices:
    #         invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
    #                                    'origin': ', '.join(invoices_origin[group_key])})
    #         sale_orders = references[invoices[group_key]]
    #         if len(sale_orders) == 1:
    #             invoices[group_key].reference = sale_orders.reference
    #
    #     if not invoices:
    #         raise UserError(_(
    #             'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))
    #
    #     for invoice in invoices.values():
    #         invoice.compute_taxes()
    #         if not invoice.invoice_line_ids:
    #             raise UserError(_(
    #                 'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))
    #         # If invoice is negative, do a refund invoice instead
    #         if invoice.amount_total < 0:
    #             invoice.type = 'out_refund'
    #             for line in invoice.invoice_line_ids:
    #                 line.quantity = -line.quantity
    #         # Use additional field helper function (for account extensions)
    #         for line in invoice.invoice_line_ids:
    #             line._set_additional_fields(invoice)
    #         # Necessary to force computation of taxes. In account_invoice, they are triggered
    #         # by onchanges, which are not triggered when doing a create.
    #         invoice.compute_taxes()
    #         # Idem for partner
    #         so_payment_term_id = invoice.payment_term_id.id
    #         invoice._onchange_partner_id()
    #         # To keep the payment terms set on the SO
    #         invoice.payment_term_id = so_payment_term_id
    #         invoice.message_post_with_view('mail.message_origin_link',
    #                                        values={'self': invoice, 'origin': references[invoice]},
    #                                        subtype_id=self.env.ref('mail.mt_note').id)
    #     return [inv.id for inv in invoices.values()]

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderInherit, self)._prepare_invoice()
        invoice_vals['parent_partner_id'] = self.parent_partner_id.id
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id')
    def compute_partner_sku(self):
        for record in self:
            if record.order_id.parent_partner_id and record.product_id:
                partner_id = record.order_id.parent_partner_id
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

    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'partner_sku': self.partner_sku,
            'barcode': self.barcode,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res
