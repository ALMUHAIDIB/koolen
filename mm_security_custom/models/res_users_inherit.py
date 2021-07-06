from odoo import models, fields, api,_

class resusersInherit(models.Model):
    _inherit = 'res.users'



    x_team_id = fields.Many2one('crm.team', 'Sales Team')