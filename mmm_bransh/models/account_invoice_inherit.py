# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    bransh_ids = fields.Many2one('res.partner', string="Branch")
