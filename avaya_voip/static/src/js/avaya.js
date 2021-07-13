odoo.define("avaya_voip.Avaya", function(require){
	"use strict";

	const Class = require("web.Class");
	const mixins = require("web.mixins");
	const ServicesMixin = require("web.ServicesMixin");
	
	const core = require('web.core');

	const avy = new AWL.client();

	const CALL_STATE = {
		NO_CALL: 0,
		INCOMING_CALL: 1,
		OUTGOING_CALL: 2,
		REJECTING_CALL: 3,
		CANCELING_CALL: 4,
		MISSED_CALL: 5,
	};

	let state = undefined;


 
	const CallListener = Class.extend(mixins.EventDispatcherMixin, ServicesMixin, {
		/**
		* @constructor
		*/
		init(parent){
			mixins.EventDispatcherMixin.init.call(this);
			this.setParent(parent);
			this.callState = CALL_STATE.NO_CALL;
			console.log(this);

		},

		incomingCall(rec){
			core.bus.trigger('incomingCall', rec);

		},

		registrationSuccess(){
			core.bus.trigger('registration_success');
		},
		
		callTerminate(callId, reason){
			core.bus.trigger('callTerminate', callId, reason, this.callState);
		},
		callAccepted(rec){
			core.bus.trigger('callAccepted', rec);
		},
		callDisconnected(callId, reason){
			core.bus.trigger('callDisconnected', callId, reason);
		},
		callRinging(){

		}, 

	});


	const Avaya = Class.extend(mixins.EventDispatcherMixin, ServicesMixin, {
		/**
		* @constructor
		*/
		init(parent){
			mixins.EventDispatcherMixin.init.call(this);
			this.setParent(parent);
			this._callState = undefined;
			this._rpc({
				model: "avaya.config",
				method: "get_avaya_config",
				args: [],
				kwargs: {},
			}).then(result => this._initConfig(result));
			// this._initConfig({id: 1});
		},
		/**
		* @private
		* @param{Object}
		*/
		_initConfig(result) {
			//avy.enableLogging();
			let stunServer = result.stun_server == false ? "" : result.stun_server;
			let stunPort = result.stun_port == false ? "" : result.stun_port;
			let turnServer = result.turn_server == false ? "" : result.turn_server;
			let turnPort = result.turn_port == false ? "" : result.turn_port;
			let turnUser = result.turn_user == false ? "" : result.turn_user;
			let turnPass = result.turn_pass == false ? "" : result.turn_pass;

			let cfg = {
				serviceType: "phone",
				enableVideo: false,
				Gateway: {ip: result.avaya_ip, port: "9443"},
				AppData: {applicationID: "", applicationUA: "sdktestclient-3.0.0", appInstanceID: avy.generateAppInstanceID()},
				disableResiliency: false,
			};
            if(result.allow_stun == "True"){
                cfg.Stunserver = {
                    ip: stunServer,
                    port: stunPort
                };
            }
            if(result.allow_turn == "True"){
                cfg.Turnserver = {
                    ip: turnServer,
                    port: turnPort,
                    user: turnUser,
                    pwd: turnPass
                };
            }

			let OnCallListener = new this._onCallListener(this);

			if( avy.setConfiguration(cfg, this._onConfigChanged, this._onRegistrationStateChanged, OnCallListener, this._onAuthTokenRenewd) === "AWL_MSG_SETCONFIG_SUCCESS"){
				console.log("\n SETCONFIG SUCCESS");

			}

			avy.logIn(result.login, result.password, "true");
		},

		answerCall(callID){
			avy.answerCall(callID);
		},

		rejectCall(callID){
			avy.rejectCall(callID);
		},
		_makeCall(number){
			return avy.makeCall(number);
		},
		makeCall(number){
			return avy.makeCall(number);
		},
		onTransferCall(number, callId){
			avy.transferCall(number, callId, 'unAttended');
		},
		dropCall(callID){
			avy.dropCall(callID);
		},
		cancelCall(callID){
			avy.cancelCall(callID);
		},
		doMute(callID){
			avy.doMute(callID);
		},
		doUnMute(callID){
			avy.doUnMute(callID);
		},
		doHold(callID){
			avy.doHold(callID);
		},
		doUnHold(callID){
			avy.doUnHold(callID);
		},
		_deviceList(device){
			console.log(device);
			let d = [];
			device.forEach(function(value){
				d.push(value[0]);
			});
			let no_device = "";
			console.log(d);
			[['audioinput', 'No Mic'], ['audiooutput', 'No Sound']].forEach(function(value){
				if(!d.includes(value[0])){
					no_device += value[1] + "\n";
				}
			});
			console.log(no_device);
			if(no_device != ""){
				alert(no_device);
			}
			
		},
        deviceList(){
			avy.getDeviceList(this._deviceList);
        },
		_onCallListener: function(){
			let onCallListener = new CallListener(this);
			console.log(this);
			let _onNewIncomingCall = function(callId, callObj, autoAnswer){

				callObj._callState = CALL_STATE.INCOMING_CALL;
				onCallListener.incomingCall(callObj);	
				console.log('incoming call');
				console.log(callId);
				console.log(callObj);
				console.log(autoAnswer);
				// onCallListener.createLog(this, callId, callObj.getFarEndNumber(), "").bind(this);
				
			}
			let _onCallStateChange = function(callId, callObj, event){
				let self = this;
				switch (callObj.getCallState()){
					case "AWL_MSG_CALL_IDLE":
						console.log(callId);
						console.log(callObj);
						console.log(event);
						break;
					case "AWL_MSG_CALL_CONNECTED":
						console.log('AWL_MSG_CALL_CONNECTED');
						callObj._callState = CALL_STATE.NO_CALL;
						onCallListener.callAccepted(callObj);
						break;
					case "AWL_MSG_CALL_RINGING":
						console.log('AWL_MSG_CALL_RINGING');
						console.log(callObj);
						console.log(event);
						onCallListener.callRinging();
						break;
					case "AWL_MSG_CALL_DISCONNECTED":
						console.log('AWL_MSG_CALL_DISCONNECTED');
						onCallListener.callDisconnected(callId, "Missed Call");
						break;
					case "AWL_MSG_CALL_FAILED":
						console.log("AWL_MSG_CALL_FAILED");
						break;
					case "AWL_MSG_CALL_INCOMING":
						console.log('AWL_MSG_CALL_INCOMING');
						onCallListener.callState = CALL_STATE.INCOMING_CALL;
						break;
					case "AWL_MSG_CALL_HELD":
						console.log('AWL_MSG_CALL_HELD');
					case "AWL_MSG_CALL_FAREND_UPDATE":
						console.log(callId);
						console.log(callObj);
						console.log("AWL_MSG_CALL_FAREND_UPDATE");
						break;
					default:
						break;
				}
			}
			let _onCallTerminate = function(callId, reason){
				console.log(callId);
				onCallListener.callTerminate(callId, reason);
			}
			let _onLoopBackNotification = function(notification){
				console.log('loopback');
				console.log(notification);
			}

			return {
				onNewIncomingCall: _onNewIncomingCall,
				onCallTerminate: _onCallTerminate,
				onCallStateChange: _onCallStateChange,
				onLoopBackNotification: _onLoopBackNotification,
			}
		},
		_onConfigChanged: function(res){
			console.log('\n onConfigChange:: result = ' + res.result);
			console.log('\n onConfigChange:: reason = ' + res.reason);
		},
		_onRegistrationStateChanged: function(res){
		    console.log('\n onRegistrationStateChange :: RESULT = ' + res.result);
			console.log('\n onRegistrationStateChange :: reason = ' + res.reason);
			if(res.result == "AWL_MSG_LOGIN_SUCCESS"){
				let reg = new CallListener(this);
				reg.registrationSuccess();
			}
		},
		_onAuthTokenRenewd: function(res){
			if(res.result === "AWL_MSG_TOKEN_RENEW_SUCCESS"){
				console.log("\n _onAuthTokenRenewd:: Token is successfully renewed");
			}else{
				console.log("\n _onAuthTokenRenewd:: Token renewal failed. reason: " + res.reason);
			}
		}
	});

	return Avaya
	
});
