from odoo import fields, models, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    invoice_track_id = fields.Many2one(comodel_name="invoice.track", string="Invoice Track", readonly=True)

    def action_post(self):
        res = super(AccountInvoiceInherit, self).action_post()
        if self.parent_partner_id and self.move_type == 'out_invoice':
            invoice_track = self.env['invoice.track'].create({
                'name': str(self.sequence_number) + " / " + self.parent_partner_id.name,
                'invoice_id': self.id,
                'invoice_date': datetime.now().date(),
                'customer_id': self.parent_partner_id.id,
                'branch_id': self.partner_id.id,
                'salesperson_id': self.user_id.id,
                'state': 'receive',
            }).sudo()
            self.invoice_track_id = invoice_track.id
            return res

    def button_cancel(self):
        res = super(AccountInvoiceInherit, self).button_cancel()
        if self.invoice_track_id.id != False:
            self.invoice_track_id.unlink()
            # self.invoice_track_id.state = "cancelled"
        return res
