# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartnerMarkupWizard(models.TransientModel):
    _name = 'partner.markup.wizard'

    partner_ids = fields.Many2many(comodel_name="res.partner", string="Partner", required=False, )

    date_from = fields.Date(string="From", required=True, default=fields.Date.context_today)
    date_to = fields.Date(string="To ", required=True)

    def generate_move_line(self):
        for rec in self:
            partners = []
            if rec.partner_ids:
                for partner in rec.partner_ids:
                    gross_sales = 0
                    return_sales = 0
                    discount_sales = 0
                    cogs_sales = 0
                    account_move_line = self.env['account.move.line'].search([('partner_id', 'in', partner.ids),
                                                                              ('journal_id.markup', '=', True),
                                                                              ('date', '<=', rec.date_from),
                                                                              ('date', '>=', rec.date_to), ])
                    print('account_move_line >> ', account_move_line)
                    if account_move_line:
                        print('in if')
                        partners.append(partner.id)

                        for line in account_move_line:
                            if line.account_id.is_gsale:
                                gross_sales += line.balance

                            if line.account_id.is_return:
                                return_sales += line.balance

                            if line.account_id.is_discount:
                                discount_sales += line.balance

                            if line.account_id.is_cogs:
                                cogs_sales += line.balance

                        partner.gross_sales = gross_sales
                        partner.return_sales = return_sales
                        partner.discount_sales = discount_sales
                        partner.cogs_sales = cogs_sales

                        net_sales = gross_sales - return_sales - discount_sales
                        partner.net_sales = net_sales
                        if cogs_sales != 0:
                            markup = (net_sales - cogs_sales) / cogs_sales
                        else:
                            markup = 0
                        if net_sales != 0:
                            margin = (net_sales - cogs_sales) / net_sales
                        else:
                            margin = 0
                        partner.markup = markup
                        partner.margin = margin
                    else:
                        print('in else')
                        partner.markup = 0
                        partner.margin = 0
                        partner.gross_sales = 0
                        partner.return_sales = 0
                        partner.discount_sales = 0
                        partner.net_sales = 0
                        partner.cogs_sales = 0

            else:
                my_partners_obj = []
                res_partner = self.env['res.partner'].search([('journal_item_count', '>', 0)])
                res_partner1 = self.env['res.partner'].search_count([('journal_item_count', '>', 0)])
                print('res_partner1 >> ', res_partner1)
                for partner in res_partner:
                    print('Iam in')
                    gross_sales = 0
                    return_sales = 0
                    discount_sales = 0
                    cogs_sales = 0
                    account_move_line = self.env['account.move.line'].search([('partner_id', '=', partner.id),
                                                                              ('journal_id.markup', '=', True),
                                                                              ('date', '<=', rec.date_from),
                                                                              ('date', '>=', rec.date_to), ])
                    print('account_move_line >> ', account_move_line)
                    if account_move_line:
                        partners.append(partner.id)

                        for line in account_move_line:
                            if line.account_id.is_gsale:
                                gross_sales += line.balance

                            if line.account_id.is_return:
                                return_sales += line.balance

                            if line.account_id.is_discount:
                                discount_sales += line.balance

                            if line.account_id.is_cogs:
                                cogs_sales += line.balance

                        partner.gross_sales = gross_sales
                        partner.return_sales = return_sales
                        partner.discount_sales = discount_sales
                        partner.cogs_sales = cogs_sales

                        net_sales = gross_sales - return_sales - discount_sales
                        partner.net_sales = net_sales
                        if cogs_sales != 0:
                            markup = (net_sales - cogs_sales) / cogs_sales
                        else:
                            markup = 0
                        if net_sales != 0:
                            margin = (net_sales - cogs_sales) / net_sales
                        else:
                            margin = 0
                        partner.markup = markup
                        partner.margin = margin

            tree_view = self.env.ref('mmm_partner_markup_report.view_partner_tree')
            pivot = self.env.ref('mmm_partner_markup_report.view_partner_pivot')
            return {
                'name': _('Partner Markup'),
                'view_type': 'tree',
                'view_mode': 'tree,form,pivot',
                'res_model': 'res.partner',
                'view_id': False,
                'views': [(tree_view.id, 'tree'),
                          (pivot.id, 'pivot'), ],
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', partners)], }
