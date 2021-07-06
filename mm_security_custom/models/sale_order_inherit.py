from odoo import models, fields, api


class saleorderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    is_has_group_price = fields.Boolean(default=lambda self: self.check_user_has_group_default(),
                                        compute='check_user_has_group')

    def check_user_has_group(self):
        for rec in self:
            rec.is_has_group_price = self.env.user.has_group('mm_security_custom.group_price')

    def check_user_has_group_default(self):
        return self.env.user.has_group('mm_security_custom.group_price')


class saleorderInherit(models.Model):
    _inherit = 'sale.order'

    is_has_group_sale_person = fields.Boolean(default=lambda self: self.check_user_has_group_default(),
                                              compute='check_user_has_group')

    team_id = fields.Many2one('crm.team', 'Sales Team', related='user_id.x_team_id', store=True, change_default=True,
                              default=False)

    def check_user_has_group(self):
        for rec in self:
            rec.is_has_group_sale_person = self.env.user.has_group('mm_security_custom.group_sale_person_edit')

    def check_user_has_group_default(self):
        return self.env.user.has_group('mm_security_custom.group_sale_person_edit')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'payment_term_id': False,
                'fiscal_position_id': False,
            })
            return

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'user_id': self.partner_id.user_id.id or self.partner_id.commercial_partner_id.user_id.id or self.env.uid
        }
        if self.env['ir.config_parameter'].sudo().get_param(
                'sale.use_sale_note') and self.env.user.company_id.sale_note:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.user.company_id.sale_note

        # if self.partner_id.team_id:
        #     values['team_id'] = self.partner_id.team_id.id
        self.update(values)


class saleteamInherit(models.Model):
    _inherit = 'crm.team'

    users = fields.Many2many('res.users', compute='compute_users', store=True)

    @api.depends('member_ids')
    def compute_users(self):
        for rec in self:
            rec.users = self.env['res.users'].search([('sale_team_id', '=', rec.id)])
