from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_gsale = fields.Boolean(string="G Sales")
    is_return = fields.Boolean(string="Return")
    is_discount = fields.Boolean(string="Discount")
    is_cogs = fields.Boolean(string="COGS")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gross_sales = fields.Float('Gross Sales')
    return_sales = fields.Float('Return Sales')
    discount_sales = fields.Float('Discount Sales')
    net_sales = fields.Float('Net Sales')
    cogs_sales = fields.Float('Cogs Sales')
    markup = fields.Float('Markup', group_operator="avg")
    margin = fields.Float('Margin', group_operator="avg")


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    markup = fields.Boolean()
