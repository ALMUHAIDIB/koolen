# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class InvoiceTrack(models.Model):
    _name = "invoice.track"
    state = fields.Selection([
        ('draft', 'Draft'),
        ('receive', 'Printed Invoice'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered To Customer'),
        ('warehouse_receipt', 'Warehouse Receipt'),
        ('account_receipt', 'Accounting Receipt'),
        ('cancelled', 'Cancelled'),
    ], string='Status', index=True, readonly=True, default='draft')

    name = fields.Char(string="name", required=False, )
    invoice_id = fields.Many2one(comodel_name="account.move", string="Invoice")
    amount_total = fields.Monetary(related="invoice_id.amount_total", string='Total', store=True, readonly=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency')
    invoice_date = fields.Date(string="Invoice Date", required=False, )
    customer_id = fields.Many2one(comodel_name="res.partner", string="Customer", )
    customer_address = fields.Char(related="customer_id.street", string="Customer Address")
    branch_id = fields.Many2one(comodel_name="res.partner", string="Branch", )
    branch_address = fields.Char(related="branch_id.street", string="Branch Address")
    salesperson_id = fields.Many2one(comodel_name="res.users", string="Salesperson", )
    driver_name = fields.Char(string="Driver Name")
    car_id = fields.Many2one(comodel_name="car.model", string="Car")
    data_receive = fields.Date(string="Date Receive Invoice", required=False, )
    note_receive = fields.Text(string="Note Receive Invoice", required=False, )
    data_shipped = fields.Date(string="Date shipped", required=False, )
    note_shipped = fields.Text(string="Note shipped", required=False, )
    data_delivered = fields.Date(string="Date Delivered To Customer", required=False, )
    note_delivered = fields.Text(string="Note Delivered To Customer", required=False, )
    data_warehouse_receipt = fields.Date(string="Date Warehouse Receive", required=False, )
    note_warehouse_receipt = fields.Text(string="Note Warehouse Receive", required=False, )
    data_account_receipt = fields.Date(string="Date Accounting Receive", required=False, )
    note_account_receipt = fields.Text(string="Note Accounting Receive", required=False, )

    def convert_to_shipped(self):
        self.state = "shipped"

    def convert_to_delivered(self):
        if self.driver_name == '':
            raise ValidationError("please Enter Driver Name")
        if not self.car_id.id:
            raise ValidationError("please Select Car")
        self.state = "delivered"

    def convert_to_warehouse_receipt(self):
        self.state = "warehouse_receipt"

    def convert_to_account_receipt(self):
        self.state = "account_receipt"

    def convert_to_closed(self):
        self.state = "cancelled"

    def convert_to_receive(self):
        self.state = "receive"

    def back_to_draft(self):
        self.state = "draft"

    def convert_to_cancelled(self):
        self.state = "cancelled"
