odoo.define('avaya_voip.cstm_dialing_panel', function(require){ 
    "use strict"; 
    
    const SystrayMenu = require('web.SystrayMenu');
    const core = require('web.core');
    const session = require('web.session');
    const config = require('web.config');
    const Widget = require('web.Widget');
    const Avaya = require('avaya_voip.Avaya');
    const basic_fields = require('web.basic_fields');
    const Dialog = require('web.Dialog');
    const rpc = require('web.rpc');
    var CrashManager = require('web.CrashManager').CrashManager;

    const _t = core._t;
    const Qweb = core.qweb;
	if(session.avaya_allow === false){
		return;
	}

    if(config.device.isMobile){
        return; 
    }

    var Phone = basic_fields.FieldPhone;
    Phone.include({
        events: _.extend({}, Phone.prototype.events, {
            'click': '_onClick',
        }),
        init() {
            this._super(...arguments);
        },
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * Called when the phone number is clicked.
         *
         * @private
         * @param {MouseEvent} e
         */
        _onClick: function (e) {
            e.preventDefault();
            if(e.currentTarget.localName == "a"){
                let registered = core.bus.trigger('registered');
                if (registered){
                    var phoneNumber = this.value;
                    this.do_notify(_t('Start Calling'), _t('Calling ') + ' ' + phoneNumber);
                    core.bus.trigger('make_call', phoneNumber);
                }
            }
        },
    });

    let VoipConnector = Widget.extend({
        name: 'VoipConnector',
        template: 'avaya_voip.VoipConnector',
        events: {
            'click .call': '_onCall',
            'click .btnHangup': '_hangup',
            'click .btnCancel': '_onCancel',
            'click .btnMute': '_onMute',
            'click .btnUnMute': '_onUnMute',
            'click .btnForward': '_onTransferCall',
            'click .btnHold': '_onHold',
            'click .btnUnHold': '_onUnHold',
            'keyup .dial': function(ev){
                if(ev.keyCode === 13){
                    this._dialNumber = $('.dial').val();
                    if(this._dialNumber){

                        this._onCall(this._dialNumber);
                    }
                }
            },
        },
        custom_events: {
            'sip_accepted': '_sip_accepted',
            'on_accept_call': '_on_accept_call',
            'rejected_by': '_sip_rejected',
            'sip_cancel_outgoing': '_sip_cancel_outgoing',
            'sip_bye': '_sip_bye',
            'changeStatus': '_onProgress', 
            'sip_error_resolved': '_sip_error_resolved',
            'cancel_call': '_onCancel',
            'make_call': '_onCall',
            'open_form': '_redirectAnswerOpenForm',
            'registration_success': '_registration_success',
        },
        init: function(){
            this._super.apply(this, arguments);
            this.audio_incoming = undefined;
            this.audio_ring = undefined;
            this.callObj = undefined;
            this._callState = 0;
            this.dialog = undefined;

            core.bus.on('registration_success', this, this._registration_success);
            core.bus.on('incomingCall', this, this._incomingCall);
            core.bus.on('callTerminate', this, this._callTerminate);
            core.bus.on('callAccepted', this, this._callAccepted);
            core.bus.on('callDisconnected', this, this._callDisconnected);
			core.bus.on('make_call', this, this._onCall);
        },
        start: function(){

            this.$connector = this.$('.conn').prevObject;
            this._avaya = new Avaya(this);
            this._attach_audio_element();
            this._crash_manager();
            return this._super.apply(this, arguments);
        },
        _deviceList: function(device){
            console.log('device');
            console.log(device);
        },
        _crash_manager: function(){
            let self = this;
            CrashManager.include({
                show_error: function(error){
                    if(self.callObj.getCallState() === "AWL_MSG_CALL_IDLE"){
                        console.log(self.callObj.getCallState());
                    }else{
                        this._super(error);
                    }
                },
            })
        },
        _attach_audio_element: function(){
            this.audio_incoming = document.createElement("audio");
            this.audio_incoming.loop = 'true';
            this.audio_incoming.src = window.location.origin + "/avaya_voip/static/src/sounds/incomingcall.mp3";
            $('html').append(this.audio_incoming);
            
            this.audio_ring = document.createElement("audio");
            this.audio_ring.loop = 'true';
            this.audio_ring.src = window.location.origin + "/avaya_voip/static/src/sounds/ringbacktone.mp3";
            $('html').append(this.audio_ring);
        },

        _check_records: async function(callerNumber){
            this.contacts = undefined;
            let name = await rpc.query({
                model: 'res.partner',
                method: 'search_read',
                domain: [
                    '|',
                    ['phone', 'ilike', callerNumber],
                    ['mobile', 'ilike', callerNumber],
                ],
                fields: ['id', 'name'],
                limit: 1,
            });
            if (name.length > 0){
                this.contacts = name;
                return name[0].name;
            }

            return callerNumber;
        },
        _update_logs: async function(callId, reason){
            let call_state = undefined;
            if(reason == "Call Rejected" && this._callState == 1 || reason == "Missed Call" && this._callState == 1){
                call_state = 'missed'
                return await this._rpc({
                    model: 'avaya.call.history',
                    method: 'search_read',
                    fields: ['id'],
                    domain: [['caller_id', '=', callId], ['state', '=', 'incoming']]
                }).then((result) => {
                    if(result.length != 0){
                        this._rpc({
                            model: 'avaya.call.history',
                            method: 'write',
                            args: [[result[0].id], {
                                'state': call_state
                            }]
                        })
                    }
                })
            }
        },
        _create_log: async function(callObj){
            let call_state = undefined;
            if (this._callState == 1){
                call_state = 'incoming';
            }else if(this._callState == 2){
                call_state = 'outgoing';
            }
            let records = await this._rpc({
				model: 'avaya.call.history',
				method: 'create',
				args: [{
                    'name': callObj.getFarEndNumber(),
                    'caller_id': callObj.getCallId(),
                    'state': call_state,
                }],
			});

			return records
        },
        _incomingCall: async function(rec){
            this.callObj = rec;
            let self = this;
            let caller = await this._check_records(this.callObj.getFarEndNumber());
            this._callState = rec._callState;
            return await this._create_log(rec).then((result) => {
                console.log(result);
                console.log(self.callObj);
                console.log(self.audio_incoming);
                self.audio_incoming.play();
                self.dialog =  new Dialog(this, {
                    title: 'Incoming Call',
                    size: 'medium',
                    $content: Qweb.render('ContentDialog', {incoming: 'Incoming Call from ' + caller}),
                    buttons: [{
                        text: 'Answer',
                        classes: 'btn-primary',
                        close: true,
                        click: function(){
                            self._avaya.answerCall(self.callObj.getCallId());
                            self.audio_incoming.pause();
                            self._redirectAnswerOpenForm();
                        }
                    },
                    {
                        text: 'Reject',
                        close: true,
                        click: () => {
                            self._avaya.rejectCall(self.callObj.getCallId());
                            self.audio_incoming.pause();
                        }
                    }]
                }).open();
            });
        },
        _callTerminate: function(callId, reason, call_state){
            this.audio_incoming.pause();
            return this._update_logs(callId, reason, call_state);
        },
        _callDisconnected: function(callId, reason){
            this.onReset();
            if(this.dialog != undefined){
                this.dialog.close();
                this.dialog = undefined;
                this.do_notify(_("MISSED"), "You missed a call!");
            }
            return this._update_logs(callId, reason);
        },
        _redirectAnswerOpenForm: function(){
            const contacts = this.contacts;
            const number = this.callObj.getFarEndNumber();
            this.dialog = undefined;

            let rec_partner = {};
            if (contacts != undefined && contacts.length > 0) {
                rec_partner = {
                    res_id: contacts[0].id,
                    name: contacts[0].name,
                    number: number
                }
            } else {
                rec_partner = {
                    res_id: false,
                    number: number
                }
            }

            this._clickToPartner(rec_partner);

        },
        _onCall: function(number){
            let self = this;

            let promise = new Promise((resolve, reject) => {
                let callObj = this._avaya.makeCall(number);
                resolve(callObj);
            })

            promise.then((result) => {
                self.callObj = result;
                self._callState = 2;
                self._create_log(self.callObj);
            })
            
            this.onDialog(this._dialog_for_call(number));
            this.audio_ring.play();
        },
        _registration_success: function(){
            let self = this;
			let devices = this._avaya.deviceList();
            if(self.$connector.hasClass('conn')){
                self._backToDial(self.$connector);
            }
        },
        _callAccepted: function(rec){
            this.callObj = rec;
            this._callState = rec._callState;
            this.onDialog(this._dialog_for_ongoing());
            this.audio_ring.pause();
        },
        _hangup: function(e){
            e.preventDefault();
            this._avaya.dropCall(this.callObj.getCallId());
            this.onReset();
        },
        onReset: function(){
            let self = this;
            let oncall = self.$connector;
            if(oncall.hasClass('nav-item dropdown')){
                oncall.empty();
                self._backToDial(oncall);
            }
        },
        _onMute:function(e){
            e.preventDefault();
            e.currentTarget.classList.toggle('hidden');
            this.$('.drp-menu').find('.btnUnMute').toggleClass('hidden');

            this._avaya.doMute(this.callObj.getCallId());
        },
        _onUnMute: function(e){
            e.preventDefault();
            e.currentTarget.classList.toggle('hidden');
            this.$('.drp-menu').find('.btnMute').toggleClass('hidden');
            this._avaya.doUnMute(this.callObj.getCallId());
        },
        _onHold: function(e){
            e.preventDefault();
            e.currentTarget.classList.toggle('disabled');
            this.$('.drp-menu').find('.btnUnHold').toggleClass('disabled');
            this._avaya.doHold(this.callObj.getCallId());
        },
        _onUnHold: function(e){
            e.preventDefault();
            e.currentTarget.classList.toggle('disabled');
            this.$('.drp-menu').find('.btnHold').toggleClass('disabled');
            this._avaya.doUnHold(this.callObj.getCallId());
        },
        _backToDial: function(selector){
			selector.empty();
            selector.removeClass('conn').addClass('t_dial');
            selector.append(Qweb.render('avaya_voip.VoipDial'), {widget: this});
        },
        onDialog: function(dialog){
            let self = this;
            let dialvoip = self.$connector;
            if(dialvoip.hasClass('t_dial')){
                dialvoip.addClass('nav-item dropdown').removeClass('t_dial');
                dialvoip.empty();
            }else if(dialvoip.hasClass('nav-item dropdown')){
                dialvoip.empty();
            }
            dialvoip.append(Qweb.render('avaya_voip.VoipDropdown', dialog));
        },
        _onCancel: function(e){
            e.preventDefault();
            this._avaya.cancelCall(this.callObj.getCallId());
   
            this.onReset();
            this.audio_ring.pause();
        },
        _onTransferCall: function(e){
            e.preventDefault();
            let number = this.$('.drp-menu').find('#txt_transfer').val();
            if(number !== ""){
                this._avaya.onTransferCall(number, this.callObj.getCallId());
            }
        },
        _dialog_for_ongoing: function(){
            return {
                details: "ONGOING CALL",
                btnHangup: "btnHangup btn btn-secondary",
                btnMute: "btnMute btn btn-secondary",
                btnUnMute: "btnUnMute hidden btn btn-secondary",
                btnHold: "btnHold btn btn-secondary",
                btnUnHold: "btnUnHold btn btn-secondary disabled",
                btnCancel: "btnCancel btn btn-secondary disabled",
                btnForward: "btnForward btn btn-secondary",
                enableOncall: "false",
                enableCall: "true",
                hideInput: "",
                widget: this,
            }
        },
        _dialog_for_call: function(number){
            return {
                details: "CALLING " + number,
                btnHangup: "btnHangup btn btn-secondary disabled",
                btnMute: "btnMute btn btn-secondary disabled",
                btnUnMute: "btnUnMute hidden btn btn-secondary disabled",
                btnHold: "btnHold btn btn-secondary disabled",
                btnUnHold: "btnUnHold btn btn-secondary disabled",
                btnCancel: "btnCancel btn btn-secondary",
                btnForward: "btnForward btn btn-secondary disabled",
                enableOncall: "true",
                enableCall: "false",
                hideInput: "display: none;",
                widget: this,
            }
        },
        _clickToPartner: function(records){
            if(records.res_id){
                this.do_action({
                    res_id: records.res_id,
                    res_model: "res.partner",
                    target: 'main',
                    type: 'ir.actions.act_window',
                    views: [[false, 'form']]
                });

            } else {
                this.do_action({
                    context: {
                        default_mobile: records.number, 
                    },
                    res_model: 'res.partner',
                    target: 'main',
                    type: 'ir.actions.act_window',
                    views: [[false, 'form']]
                });
            }

        }

    })
    SystrayMenu.Items.push(VoipConnector);
    return VoipConnector;
});
