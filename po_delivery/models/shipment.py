from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SerialQtyShipment(models.Model):
    _name = 'serial.qty.shipment'

    po_id = fields.Many2one(comodel_name='purchase.order')
    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    serial = fields.Integer(string='Serial')
    qty = fields.Float(string='Quantity')

    @api.onchange('serial')
    def serial_constrain(self):
        if self.serial:
            if self.serial not in range(self.po_id.number_of_shipments + 1):
                raise ValidationError('The serial number must not be more than the number of shipments')

        else:
            raise ValidationError('Please enter Serial Number')
