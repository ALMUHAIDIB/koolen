from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def _check_order_line(self):
        if self.order_line:
            for line in self.order_line:
                sale_line_obj = self.env['sale.order.line'].search(
                    [('order_id', '=', self.id), ('product_id', '=', line.product_id.id)])
                if len(sale_line_obj) > 1:
                    raise ValidationError(("This Product %s Already Exist") % line.product_id.display_name)









