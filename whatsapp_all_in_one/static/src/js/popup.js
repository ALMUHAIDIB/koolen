odoo.define('whatsapp_all_in_one.popups', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var PopupWidget = require('point_of_sale.popups');
var rpc = require('web.rpc');
var _t  = require('web.core')._t;


var WhatsAppQRCodePopup = PopupWidget.extend({
    template: 'QRCodePopup',
    click_confirm: function() {
        var self = this;
        this.gui.close_popup();
        if (this.options.rec_id) {
            rpc.query({
                model: 'whatsapp.msg',
                method: 'action_send_msg',
                args: [[self.options.rec_id]],
                context: {'from_pos': true},
            }).then(function (res) {
                var type = self.options.type
                if (res && res.name && res.name === 'Scan WhatsApp QR Code') {
                    self.gui.show_popup("whatsapp_qr_popup", {
                       'title': _t("Scan WhatsApp QR Code"),
                       'body':  _t("You are not logged in to WhatsApp, Please Scan QR code and Login"),
                       'qr_img': res.qr_img,
                       'rec_id': self.options.rec_id,
                       'type': type,
                    });
                    self.$('.js_whatsapp_send').css('pointer-events', 'auto');
                } else if (res === true) {
                    self.gui.show_popup('confirm',{
                        'title': _t('Message Sent'),
                        'body': _t(type + " has been sent to customer's WhatsApp number"),
                    });
                    self.$('.js_whatsapp_send').css('pointer-events', 'auto');
                } else {
                    self.gui.show_popup("error", {
                       'title': _t("Error sending message"),
                       'body':  _t("Something went wrong while sending " + type + " to WhatsApp."),
                    });
                    self.$('.js_whatsapp_send').css('pointer-events', 'auto');
                }
            });
        }
    },
});
gui.define_popup({name:'whatsapp_qr_popup', widget: WhatsAppQRCodePopup});

return PopupWidget;
});
