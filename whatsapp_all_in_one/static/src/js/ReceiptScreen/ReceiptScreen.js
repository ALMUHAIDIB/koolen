odoo.define('whatsapp_all_in_one.ReceiptScreen', function(require) {
    'use strict';

    const { useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const { useContext } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const OrderManagementScreen = require('point_of_sale.OrderManagementScreen');
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const contexts = require('point_of_sale.PosContext');

    const WhatsAppPosResReceiptScreen = ReceiptScreen =>
        class extends ReceiptScreen {
            constructor() {
                super(...arguments);
                this.orderReceiptWhatsApp = useRef('order-receipt');
            }
            /**
             * @override
             */
            async sendToWhatsApp() {
                var order = this.currentOrder;
                var self = this;
                var customer = this.currentOrder.changed.client;
                var message = this.env._t('Dear *' + customer.name + '*,\nHere is your electronic ticket for the *' + order.name + '*');
                var newContext = {
                    'receipt_data': this.orderReceiptWhatsApp.el.outerHTML,
                    'active_model': 'pos.order',
                    'active_id': order.name,
                };
                var context = _.extend(this.env.session.user_context || {}, newContext);

                await this.rpc({
                    model: 'whatsapp.msg',
                    method: 'create',
                    args: [{
                        'partner_ids': [customer.id],
                        'message': message,
                    }],
                    kwargs: { context: newContext },
                }).then(function(result) {
                    if (result) {
                        self.rpc({
                            model: 'whatsapp.msg',
                            method: 'action_send_msg',
                            args: [[result]],
                            kwargs: { context: {'from_pos': true} },
                        }).then(function (res) {
                            debugger;
                            // var type = is_send_invoice ? "Invoice" : "Receipt";
                            // if (res && res.name && res.name === 'Scan WhatsApp QR Code') {
                            //     self.gui.show_popup("whatsapp_qr_popup", {
                            //        'title': _t("Scan WhatsApp QR Code"),
                            //        'body':  _t("You are not logged in to WhatsApp, Please Scan QR code and Login"),
                            //        'qr_img': res.qr_img,
                            //        'rec_id': result,
                            //        'type': type,
                            //     });
                            //     self.$('.js_whatsapp_send').css('pointer-events', 'auto');
                            //     self.lock_screen(false);
                            //     resolveDone();
                            // } else if (res === true) {
                            //     self.gui.show_popup('confirm',{
                            //         'title': _t('Message Sent'),
                            //         'body': _t(type + " has been sent to customer's WhatsApp number"),
                            //     });
                            //     self.$('.js_whatsapp_send').css('pointer-events', 'auto');
                            //     self.lock_screen(false);
                            //     resolveDone()
                            // } else {
                            //     self.gui.show_popup("error", {
                            //        'title': _t("Error sending message"),
                            //        'body':  _t("Something went wrong while sending " + type + " to WhatsApp."),
                            //     });
                            //     self.$('.js_whatsapp_send').css('pointer-events', 'auto');
                            //     self.lock_screen(false);
                            //     rejectDone();
                            // }
                        });
                    }
                });
            }
        };

    Registries.Component.extend(ReceiptScreen, WhatsAppPosResReceiptScreen);

    return ReceiptScreen;
});
