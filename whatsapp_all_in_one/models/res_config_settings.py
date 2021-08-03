# -*- coding: utf-8 -*-

import os
import shutil

from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def action_logout(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        dir_path = os.path.abspath(dir_path + '/../wizard')
        data_dir = '.user_data_uid_' + self._get_unique_user()
        try:
            self.env['whatsapp.msg'].sudo()._cron_kill_chromedriver()
            shutil.rmtree(dir_path + '/' + data_dir)
        except:
            pass

    def _get_unique_user(self):
        IPC = self.env['ir.config_parameter'].sudo()
        dbuuid = IPC.get_param('database.uuid')
        return dbuuid + '_' + str(self.env.uid)
