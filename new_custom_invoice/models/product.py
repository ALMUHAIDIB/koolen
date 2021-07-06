from odoo import fields, models, api


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    ar_name = fields.Char(string='Arabic Name')
