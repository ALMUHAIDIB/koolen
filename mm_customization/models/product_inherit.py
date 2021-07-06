from odoo import models, fields, api


class ProductInherit(models.Model):
    _inherit = 'product.template'

    box_size = fields.Integer(string='Box Size')
