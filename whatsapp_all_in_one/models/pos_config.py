# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class POSOrder(models.Model):
    _inherit = 'pos.config'

    auto_whatsapp_invoice = fields.Boolean(string='Automatic Receipt/Invoice via WhatsApp', help="Send POS Receipt/Invoice Automatically to Customer's WhatsApp Number")
    default_option = fields.Selection([('invoice', 'Invoice'), ('receipt', 'Receipt')], string='WhatsApp Default Option', default='receipt')

    @api.onchange('default_option', 'module_account')
    def _onchange_default_option(self):
        if self.default_option == 'invoice' and not self.module_account:
            raise UserError(_("You can't set invoice as default option, becuase invoicing option is not enabled."))