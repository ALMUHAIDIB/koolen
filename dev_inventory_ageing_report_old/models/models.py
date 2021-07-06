from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_aging = fields.Boolean(string="Aging")

