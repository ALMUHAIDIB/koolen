from odoo import models, fields, api


class AccountInvoiceLineInherit(models.Model):
    _inherit = 'account.move.line'

    salesman_id = fields.Many2one(related='move_id.invoice_user_id', store=True, string='Salesperson')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], related='move_id.state', string='Status', store=True, default='draft', copy=False)
