from odoo import models, fields, api, _


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    def return_invoices_with_domain(self):
        tree_view = self.env.ref('account.view_out_invoice_tree')
        form_view = self.env.ref('account.view_move_form')
        kanban_view = self.env.ref('account.view_account_move_kanban')
        # pivot = self.env.ref('account.view_invoice_pivot')
        action = {
            'name': _('Invoices'),
            'view_mode': 'tree,kanban,pivot, form',
            'res_model': 'account.move',
            'context': {'move_type': 'out_invoice', 'journal_type': 'sale'},
            'domain': [('move_type', '=', 'out_invoice')],
            'res_id': self.id,
            'view_id': False,
            'views': [
                (tree_view.id, 'tree'),
                (kanban_view.id, 'kanban'),
                # (pivot.id, 'pivot'),
                (form_view.id, 'form'),
            ],
            'type': 'ir.actions.act_window',
        }
        if self.env.user.has_group('sales_team.group_sale_salesman') and not self.env.user.has_group(
                'sales_team.group_sale_salesman_all_leads'):
            action['domain'] = [('move_type', '=', 'out_invoice'), ('user_id', '=', self.env.user.id)]
        elif self.env.user.has_group('sales_team.group_sale_salesman_all_leads') and not self.env.user.has_group(
                'sales_team.group_sale_manager'):
            action['domain'] = [('move_type', '=', 'out_invoice'), '|', ('user_id', '=', self.env.user.id),
                                ('team_id.users', 'in', self.env.user.id)]
        elif self.env.user.has_group('sales_team.group_sale_manager'):
            action['domain'] = [('move_type', '=', 'out_invoice')]
        return action

    def return_credit_with_domain(self):
        tree_view = self.env.ref('account.view_out_invoice_tree')
        form_view = self.env.ref('account.view_move_form')
        kanban_view = self.env.ref('account.view_account_move_kanban')
        # pivot = self.env.ref('account.view_invoice_pivot')
        action = {
            'name': _('Credit Notes'),
            'view_mode': 'tree,kanban,pivot, form',
            'res_model': 'account.move',
            'context': {'default_move_type': 'out_refund', 'move_type': 'out_refund', 'journal_type': 'sale'},
            'domain': [('move_type', '=', 'out_refund')],
            'res_id': self.id,
            'view_id': False,
            'views': [
                (tree_view.id, 'tree'),
                (kanban_view.id, 'kanban'),
                # (pivot.id, 'pivot'),
                (form_view.id, 'form'),
            ],
            'type': 'ir.actions.act_window',
        }
        if self.env.user.has_group('sales_team.group_sale_salesman') and not self.env.user.has_group(
                'sales_team.group_sale_salesman_all_leads'):
            action['domain'] = [('move_type', '=', 'out_refund'), ('user_id', '=', self.env.user.id)]
        elif self.env.user.has_group('sales_team.group_sale_salesman_all_leads') and not self.env.user.has_group(
                'sales_team.group_sale_manager'):
            action['domain'] = [('move_type', '=', 'out_refund'), '|', ('user_id', '=', self.env.user.id),
                                ('team_id.users', 'in', self.env.user.id)]
        elif self.env.user.has_group('sales_team.group_sale_manager'):
            action['domain'] = [('move_type', '=', 'out_refund')]
        return action
