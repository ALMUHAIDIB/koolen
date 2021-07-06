from odoo import fields, models, api


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    serial_number = fields.Char(string='Serial Number')
