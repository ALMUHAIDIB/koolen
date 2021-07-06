from odoo import models, fields, api, exceptions, _


class SalesTargetModel(models.Model):
    _name = 'sales.target'
    _rec_name = 'user_id'

    product_id = fields.Many2one('product.product', string='Product')
    team_id = fields.Many2one('crm.team', 'Sales Team')
    user_id = fields.Many2one('res.users', string='Sales Person')
    target = fields.Float(string='Target')
    achieved = fields.Float(string='Sold QTY', compute='compute_target_achieved', store=False)
    sold_value = fields.Float(string='Sold Value', compute='compute_sold_value_achieved', store=False)
    sold_value_stored = fields.Float(string='Sold Value')
    achieved_stored = fields.Float(string='Sold QTY')
    achieved_percent = fields.Float(string='Acheived %', compute='compute_target_percent', store=False)
    achieved_percent_stored = fields.Float(string='Acheived %')
    color = fields.Integer('Color Index', default=0)
    # update = fields.Boolean(string='updated')
    month = fields.Selection([
        ('1', 'Jan'), ('2', 'Feb'),
        ('3', 'Mar'), ('4', 'April'),
        ('5', 'May'), ('6', 'Jun'),
        ('7', 'Jul'), ('8', 'Aug'),
        ('9', 'Sep'), ('10', 'Oct'),
        ('11', 'Nov'), ('12', 'Dec'),
    ], string='Month')

    categ_id = fields.Many2one('product.category', string='Product Category', related='product_id.categ_id', store=True)
    onhand = fields.Float(string='On Hand', related='product_id.qty_available', store=True)
    assigned_target = fields.Float(string='Assigned Target', compute='compute_assigned_target')
    value_target = fields.Float(string='Value Target', compute='compute_value_target')
    value_target_store = fields.Float(string='Value Target')

    @api.onchange('product_id', 'target')
    def compute_value_target(self):
        for rec in self:
            if rec.product_id and rec.target:
                pricelist_item_obj = self.env['product.pricelist.item'].search(
                    [('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id),
                     ('pricelist_id.name', '=', 'WHOLE SALE')], limit=1)
                if pricelist_item_obj:
                    rec.value_target = rec.target * pricelist_item_obj.fixed_price
                else:
                    rec.value_target = 0

    @api.onchange('team_id')
    def onchange_team_domain(self):
        for rec in self:
            if rec.team_id:
                return {
                    'domain': {'user_id': [('id', 'in', rec.team_id.member_ids.ids)]}
                }
            else:
                return {
                    'domain': {'user_id': []}
                }

    @api.onchange('product_id', 'month')
    def compute_assigned_target(self):
        for rec in self:
            assigned_target = 0
            if rec.product_id and rec.month:
                sales_target_obj = self.search([('product_id', '=', rec.product_id.id)])
                for line in sales_target_obj:
                    assigned_target += line.target
                rec.assigned_target = assigned_target

    @api.constrains('product_id', 'user_id', 'month')
    def unique_attendance_code(self):
        if self.product_id and self.user_id and self.month and self.search(
                [('product_id', '=', self.product_id.id), ('user_id', '=', self.user_id.id), ('month', '=', self.month),
                 ('id', '!=', self.id)]):
            raise exceptions.ValidationError(_('This Target Already Exist !'))

    @api.onchange('categ_id')
    def categ_products_of_sale_domains(self):
        for rec in self:
            if rec.categ_id:
                products = self.env['product.product'].search([('categ_id', '=', rec.categ_id.id)])
                return {
                    'domain': {'product_id': [('id', 'in', products.ids)]}
                }
            else:
                return {
                    'domain': {'product_id': []}
                }

    @api.onchange('user_id', 'product_id', 'month')
    def compute_target_achieved(self):
        for rec in self:
            filtered_invoice = []
            filtered_return_invoice = []
            achieved_value = 0
            returned_value = 0
            if rec.user_id and rec.product_id and rec.month:
                invoice_lines_obj = self.env['account.move.line'].search(
                    [('salesman_id', '=', rec.user_id.id), ('state', 'in', ('open', 'in_payment', 'paid')),
                     ('price_subtotal', '>', 0), ('product_id', '=', rec.product_id.id)])
                for line in invoice_lines_obj:
                    if line.create_date.month == int(rec.month):
                        filtered_invoice.append(line)
                for filter_line in filtered_invoice:
                    achieved_value += filter_line.quantity
                invoice_lines_return_obj = self.env['account.move.line'].search(
                    [('salesman_id', '=', rec.user_id.id), ('state', 'in', ('open', 'in_payment', 'paid')),
                     ('price_subtotal', '<', 0),
                     ('product_id', '=', rec.product_id.id)])
                for return_line in invoice_lines_return_obj:
                    if return_line.create_date.month == int(rec.month):
                        filtered_return_invoice.append(return_line)
                for filter_return_line in filtered_return_invoice:
                    returned_value += filter_return_line.quantity
                rec.achieved = achieved_value - returned_value

    @api.onchange('user_id', 'product_id', 'month')
    def compute_sold_value_achieved(self):
        for rec in self:
            filtered_invoice = []
            filtered_return_invoice = []
            sold_value = 0
            returned_value = 0
            if rec.user_id and rec.product_id and rec.month:
                invoice_lines_obj = self.env['account.move.line'].search(
                    [('salesman_id', '=', rec.user_id.id), ('price_subtotal', '>', 0),
                     ('state', 'in', ('open', 'in_payment', 'paid')),
                     ('product_id', '=', rec.product_id.id)])
                for line in invoice_lines_obj:
                    if line.create_date.month == int(rec.month):
                        filtered_invoice.append(line)
                for filter_line in filtered_invoice:
                    sold_value += filter_line.price_subtotal
                invoice_lines_returned_obj = self.env['account.move.line'].search(
                    [('salesman_id', '=', rec.user_id.id), ('price_subtotal', '<', 0),
                     ('state', 'in', ('open', 'in_payment', 'paid')),
                     ('product_id', '=', rec.product_id.id)])
                for return_line in invoice_lines_returned_obj:
                    if return_line.create_date.month == int(rec.month):
                        filtered_return_invoice.append(return_line)
                for filter_return_line in filtered_return_invoice:
                    returned_value += filter_return_line.price_subtotal
                rec.sold_value = sold_value - returned_value

    @api.onchange('achieved', 'target')
    def compute_target_percent(self):
        for rec in self:
            if rec.achieved and rec.target:
                rec.achieved_percent = (rec.achieved / rec.target) * 100
            else:
                rec.achieved_percent = 0

    @api.onchange('achieved')
    def on_change_archived(self):
        for rec in self:
            rec.achieved_stored = rec.achieved

    @api.onchange('value_target')
    def on_change_value_target(self):
        for rec in self:
            rec.value_target_store = rec.value_target

    @api.onchange('achieved_percent')
    def on_change_archived_percent(self):
        for rec in self:
            rec.achieved_percent_stored = rec.achieved_percent

    @api.onchange('sold_value')
    def on_change_sold_value(self):
        for rec in self:
            rec.sold_value_stored = rec.sold_value

    def update(self):
        self = self.sudo()
        for rec in self.search([]):
            rec.on_change_archived()
            rec.on_change_archived_percent()
            rec.on_change_sold_value()
            rec.on_change_value_target()
