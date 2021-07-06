from odoo import models, fields, api


class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    is_company = fields.Boolean(string='IS Company', default=False)

    @api.onchange('company_type')
    def onchange_company_type(self):
        if self.company_type == 'company':
            self.is_company == True
        else:
            self.is_company == False

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id,
                 "%s %s" % (rec.ref + '-' if rec.ref else " ", rec.name)
                 ))
        return result
