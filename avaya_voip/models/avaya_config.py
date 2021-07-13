from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied
from odoo.http import request

from odoo.addons.base.models import res_users
res_users.USER_PRIVATE_FIELDS.append('avaya_password')


class AvayaConfiguration(models.Model):
    _name = "avaya.config"
    _description = "Avaya Configuration"

    @api.model
    def get_avaya_config(self):
        if not self.env.user.has_group('base.group_user'):
            raise AccessDenied()

        get_param = self.env['ir.config_parameter'].sudo().get_param
        return {
            'avaya_ip': get_param('avaya_voip.avaya_ip', default="localhost"),
            'stun_server': get_param('avaya_voip.stun_server'),
            'stun_port':get_param('avaya_voip.stun_port'),
            'turn_server': get_param('avaya_voip.turn_server'),
            'turn_port':get_param('avaya_voip.turn_port'),
            'turn_user':get_param('avaya_voip.turn_user'),
            'turn_pass':get_param('avaya_voip.turn_pass'),
            'allow_stun': get_param('avaya_voip.allow_stun'),
            'allow_turn': get_param('avaya_voip.allow_turn'),
            'login': self.env.user[0].avaya_login,
            'password': self.env.user[0].avaya_password,
            'debug': self.user_has_groups('base.group_no_one')
        }


class AvayaResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    avaya_ip = fields.Char("AVAYA Server IP", help="The IP address of your AVAYA Server", default="localhost", config_parameter="avaya_voip.avaya_ip")
    avaya_stun_server = fields.Char(string="Stun Server", config_parameter="avaya_voip.stun_server")
    stun_port = fields.Char(string="Port", config_parameter="avaya_voip.stun_port")
    avaya_turn_server = fields.Char(string="Turn Server", config_parameter="avaya_voip.turn_server")
    turn_port = fields.Char(string="Port", config_parameter="avaya_voip.turn_port")
    turn_user = fields.Char(string="User", config_parameter="avaya_voip.turn_user")
    turn_pass = fields.Char(string="Password",  config_parameter="avaya_voip.turn_pass")
    allow_stun = fields.Boolean(string="Allow Stun", default=False, config_parameter="avaya_voip.allow_stun")
    allow_turn = fields.Boolean(string="Allow Turn", default=False, config_parameter="avaya_voip.allow_turn")


class ResUsers(models.Model):
    _inherit = 'res.users'

    def __init__(self, pool, cr):
        init_res = super(ResUsers, self).__init__(pool, cr)
        avaya_fields = [
            'avaya_login',
            'avaya_password',
            'avaya_allow',
        ]

        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(avaya_fields)

        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(avaya_fields)
        return init_res

    avaya_login = fields.Char("AVAYA Login / Browser's Extension", groups="base.group_user")
    avaya_password = fields.Char("AVAYA Password", groups="base.group_user")
    avaya_allow = fields.Boolean(default=False, string="Enable VOIP", groups="base.group_user")

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super(IrHttp, self).session_info()
        result['avaya_allow'] = self.env.user[0].avaya_allow
        return result
