odoo.define('whatsapp_all_in_one.whatsapp_pos', function (require) {
'use strict';

var concurrency = require('web.concurrency');
var core = require('web.core');
var models = require('point_of_sale.models');
var Printer = require('point_of_sale.Printer').Printer;
var rpc = require('web.rpc');
var screens = require('point_of_sale.screens');
var session = require('web.session');
var Widget = require('web.Widget');


var ajax = require('web.ajax');
var _t = core._t;

var QWeb = core.qweb;

screens.ReceiptScreenWidget.include({
    show: function() {
        var self = this;
        this._super();
        var is_auto_send = this.pos.config.auto_whatsapp_invoice;
        var order = this.pos.get_order();
        if (order.is_to_invoice()) {
            this.$('.js_whatsapp_send').html("<i class='fa fa-whatsapp' /> Send Invoice")
        } else {
            this.$('.js_whatsapp_send').html("<i class='fa fa-whatsapp' /> Send Receipt")
        }
        if (is_auto_send) {
            var ordered = this.pos.push_order(order);
            ordered.then(function () {
                self.whatsapp_send();
            }).catch(function () {
                // self.gui.show_popup("error", {
                //    'title': _t("Error sending message"),
                //    'body':  _t("Connection to POS backend is not present! WhatsApp Message will not be sent."),
                // });
            });
        }
    },
    renderElement: function() {
        var self = this;
        this._super();
        this.$('.js_whatsapp_send').click(function(){
            $(this).css('pointer-events', 'none');
            self.lock_screen(true);
            self.whatsapp_send();
        });
    },
    whatsapp_send: function(){
        var self = this;
        var order = this.pos.get_order();
        var customer = order.get_client();
        var is_send_invoice = order.is_to_invoice();
        if (customer && customer.mobile) {
            var context = {
                'active_model': 'pos.order',
                'active_id': order.name,
            }
            var data = {
                widget: this,
                pos: order.pos,
                order: order,
                receipt: order.export_for_printing(),
                orderlines: order.get_orderlines(),
                paymentlines: order.get_paymentlines(),
            };

            var receipt = QWeb.render('OrderReceipt', data);
            var printer = new Printer();
            var prom = new Promise(function () {});

            var message = '';

            if (is_send_invoice) {
                message = _t('Dear *' + customer.name + '*,\nHere is your Invoice for the *' + order.name + '*');
                prom = new Promise((resolve, reject) => {resolve();});
            } else {
                message = _t('Dear *' + customer.name + '*,\nHere is your electronic ticket for the *' + order.name + '*');
                prom = new Promise((resolve, reject) => {
                    context['receipt_data'] = receipt;
                    resolve();
                });
            }
            var order_id = self.pos.db.add_order(order.export_as_JSON());
            var done =  new Promise(function (resolveDone, rejectDone) {
                var transfer;
                if (is_send_invoice) {
                    transfer = new Promise((resolve, reject) => {
                        resolve();
                    });
                } else {
                    var transfer = self.pos._flush_orders([self.pos.db.get_order(order_id)], {timeout:30000, to_invoice:is_send_invoice, for_whatsapp:true});
                }
                transfer.catch(function (error) {
                    rejectDone();
                });

                transfer.then(function(order_server_id){
                    rpc.query({
                        model: 'whatsapp.msg',
                        method: 'create',
                        args: [{
                            'partner_ids': [customer.id],
                            'message': message,
                        }],
                        context: context,
                    }).then(function(result) {
                        if (result) {
                            rpc.query({
                                model: 'whatsapp.msg',
                                method: 'action_send_msg',
                                args: [[result]],
                                context: {'from_pos': true},
                            }).then(function (res) {
                                var type = is_send_invoice ? "Invoice" : "Receipt";
                                if (res && res.name && res.name === 'Scan WhatsApp QR Code') {
                                    self.gui.show_popup("whatsapp_qr_popup", {
                                       'title': _t("Scan WhatsApp QR Code"),
                                       'body':  _t("You are not logged in to WhatsApp, Please Scan QR code and Login"),
                                       'qr_img': res.qr_img,
                                       'rec_id': result,
                                       'type': type,
                                    });
                                    self.$('.js_whatsapp_send').css('pointer-events', 'auto');
                                    self.lock_screen(false);
                                    resolveDone();
                                } else if (res === true) {
                                    self.gui.show_popup('confirm',{
                                        'title': _t('Message Sent'),
                                        'body': _t(type + " has been sent to customer's WhatsApp number"),
                                    });
                                    self.$('.js_whatsapp_send').css('pointer-events', 'auto');
                                    self.lock_screen(false);
                                    resolveDone()
                                } else {
                                    self.gui.show_popup("error", {
                                       'title': _t("Error sending message"),
                                       'body':  _t("Something went wrong while sending " + type + " to WhatsApp."),
                                    });
                                    self.$('.js_whatsapp_send').css('pointer-events', 'auto');
                                    self.lock_screen(false);
                                    rejectDone();
                                }
                            });
                        } else {
                            self.lock_screen(false);
                        }
                    }).catch(function () {
                        self.lock_screen(false);
                        order.set_to_email(false);
                        self.$('.js_whatsapp_send').css('pointer-events', 'auto');
                        rejectDone();
                        // self.gui.show_popup("error", {
                        //    'title': _t("Error sending message"),
                        //    'body':  _t("Connection to POS backend is not present! WhatsApp Message will not be sent."),
                        // });
                    });
                });
                return done;
            });
        }
    }
});

screens.PaymentScreenWidget.include({

    renderElement: function() {
        var self = this;
        this._super();
        this.$('input[name="whatsapp_select"]').on('change', function (evt) {
            if (evt.target.value == 'invoice') {
                self.$('.js_invoice').addClass('highlight');
            } else {
                self.$('.js_invoice').removeClass('highlight');
            }
        });
    },
    click_invoice: function() {
        this._super();
        var order = this.pos.get_order();
        if (order.is_to_invoice()) {
            this.$('input[name="whatsapp_select"][value="receipt"]').attr('checked', false);
            this.$('input[name="whatsapp_select"][value="invoice"]').attr('checked', 'checked');
        } else {
            this.$('input[name="whatsapp_select"][value="invoice"]').attr('checked', false);
            this.$('input[name="whatsapp_select"][value="receipt"]').attr('checked', 'checked');
        }
    },
});

});
