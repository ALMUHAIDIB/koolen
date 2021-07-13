from odoo import models, fields, api, _

class AvayaHistory(models.Model):
    _name = "avaya.call.history"
    _description = "Avaya Call History"

    name = fields.Char(string="Number")
    partner_id = fields.Many2one("res.partner", string="Contacts")
    state = fields.Selection(string="Status", selection=[
        ('missed', 'Missed'),
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ])
    agent_id = fields.Many2one("res.partner", string="Agent", default=lambda self: self.env.user.partner_id)
    caller_id = fields.Char(string="CallerID")
    agent_domain = fields.Char(string="Agent Filter", compute="_temp", search="_get_history")

    def _temp(self):
        pass

    def _get_history(self, operator, value):
        agentId = self.env.user[0].partner_id.id
        return [('agent_id', '=', agentId)]

    @api.model
    def create(self, vals):
        vals['caller_id'] = vals['caller_id'].split('@')[0] if '@' in vals['caller_id'] else vals['caller_id']
        vals['partner_id'] = self.env['res.partner'].sudo().search([('mobile', '=', vals['name'])]).id
        return super(AvayaHistory, self).create(vals)
    
    # def write(self, vals):
    #     print(self)
    #     print(vals)
    #     return super(AvayaHistory, self).write(vals)


