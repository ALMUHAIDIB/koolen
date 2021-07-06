# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CarModel(models.Model):
    _name = "car.model"

    name = fields.Char(string="Car Number")
    car_type = fields.Char(string="Car Type")
