# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OperationType(models.Model):
    _inherit = 'stock.picking.type'

    salesperson = fields.Boolean(string="Salesperson")


class Picking(models.Model):
    _inherit = 'stock.picking'

    user_id = fields.Many2one(comodel_name="res.users", string="Salesperson")
    salesperson = fields.Boolean(string="Salesperson", related='picking_type_id.salesperson')


class JournalItemInherit(models.Model):
    _inherit = 'account.move.line'

    branch = fields.Char(string='Branch', compute='get_branch', store=True)
    user_id = fields.Many2one('res.users', compute='compute_user', store=True)
    branch_user_id = fields.Many2one('res.users', related='move_id.partner_id.user_id', string='Branch Salesperson')
    invoice_user_id = fields.Many2one('res.users', related='move_id.user_id', string='Invoice Salesperson')
    mmm_user_id = fields.Many2one('res.users', string='MMM Salesperson', compute='get_mmm_salesperson', store=True)

    @api.depends('move_id')
    def get_mmm_salesperson(self):
        print('hi')
        for rec in self:
            if rec.move_id:
                rec.mmm_user_id = rec.move_id.user_id.id
            elif rec.move_id.stock_move_id.picking_id.sale_id:
                rec.mmm_user_id = rec.move_id.stock_move_id.picking_id.sale_id.user_id.id
            elif rec.move_id.stock_move_id.picking_id.user_id:
                rec.mmm_user_id = rec.move_id.stock_move_id.picking_id.user_id.id
            else:
                rec.mmm_user_id = False

    @api.depends('payment_id', 'move_id')
    def get_branch(self):
        print('hi')
        for rec in self:
            if rec.payment_id:
                rec.branch = rec.payment_id.partner_id.name
            elif rec.move_id:
                rec.branch = rec.move_id.partner_id.name

    @api.depends('payment_id', 'move_id')
    def compute_user(self):
        for rec in self:
            if rec.payment_id:
                rec.user_id = rec.payment_id.sales_person
            elif rec.move_id:
                rec.user_id = rec.move_id.user_id
            else:
                rec.user_id = False


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    sales_person = fields.Many2one('res.users',related='partner_id.user_id',store=True)