# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
from lxml import etree


class sale_order(models.Model):
    _inherit = 'sale.order'

    #
    # @api.multi
    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     res= super(sale_order,self).onchange_partner_id()
    #     for s_order in self:
    #         if s_order.partner_id:
    #             for line in s_order.order_line:
    #                 line.discount = s_order.partner_id.discount

    @api.onchange('parent_partner_id')
    def parent_partner_id_onchange(self):
        domain = super(sale_order, self).parent_partner_id_onchange()
        for s_order in self:
            if s_order.parent_partner_id:
                for line in s_order.order_line:
                    line.discount = s_order.parent_partner_id.discount
        if domain:
            return domain


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    # @api.onchange('product_id')
    # def product_id_change(self):
    #     res = super(sale_order_line, self).product_id_change()
    #     for sale_line in self:
    #         if sale_line.order_id and sale_line.order_id.partner_id:
    #             sale_line.discount = sale_line.order_id.partner_id.discount

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(sale_order_line, self).product_id_change()
        for sale_line in self:
            if sale_line.order_id and sale_line.order_id.parent_partner_id:
                sale_line.discount = sale_line.order_id.parent_partner_id.discount
