# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
from odoo.tools.misc import formatLang


class landed_cost_customizations(models.Model):
    _inherit = 'purchase.order'

    lc_number = fields.Char()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('name', operator, name), ('partner_ref', operator, name),('lc_number', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.depends('name', 'partner_ref', 'lc_number')
    def name_get(self):
        result = []
        for po in self:
            refrenced_string = po.lc_number or ''
            name = po.name
            if po.partner_ref:
                name += '/' + po.partner_ref
            if self.env.context.get('show_total_amount') and po.amount_total:
                name += ': ' + formatLang(self.env, po.amount_total, currency_obj=po.currency_id)
            refrenced_string += ' ' + name
            result.append((po.id, refrenced_string))
        return result
