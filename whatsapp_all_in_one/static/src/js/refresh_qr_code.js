odoo.define('whatsapp_all_in_one.refresh_qr_code', function (require) {
"use strict";

var FormRenderer = require('web.FormRenderer');
var rpc = require('web.rpc');


FormRenderer.include({

     _render: function () {
        this.qr_timer = 0;
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            if (self.$el.hasClass('qr_code_form')) {
                var res_id = self.state.context && self.state.context.wiz_id;
                if (res_id) {
                    self.qr_timer = setInterval(function() {
                        try {
                            rpc.query({
                                model: 'whatsapp.msg',
                                method: 'get_qr_img',
                                args: [[res_id]],
                            }).then(function (res) {
                                if (res) {
                                    self.$el.find('img.qr_img').attr('src', res)
                                }
                            });
                        } catch(err) {
                            console.error(err);
                        }
                    }, 9000);
                }
                self.$el.find('button.send_btn').on('click', function() {
                    clearInterval(self.qr_timer);
                });
                self.$el.find('button.close_btn').on('click', function() {
                    clearInterval(self.qr_timer);
                });

            }
        });
    },
});

});
