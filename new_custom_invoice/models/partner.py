from odoo import models, fields, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    customer_product_sku = fields.One2many('sku.partner', 'partner_id', string='Products SKU')
    credit_period = fields.Integer(string='Credit Period')

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id,
                 "%s %s" % (rec.ref + '-' if rec.ref else " ", rec.name)
                 ))
        return result

    def get_name_ref(self):
        for record in self:
            return "{0}{1}".format(record.ref + '-' if record.ref else "", record.name)


class PartnerSku(models.Model):
    _name = 'sku.partner'

    partner_id = fields.Many2one('res.partner', string='Partner', invisible=True)
    name = fields.Many2one('product.product', string='Product', required=True)
    product_sku = fields.Char(string='SKU NO.')
