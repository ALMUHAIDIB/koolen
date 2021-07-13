// odoo.define('avaya_voip/static/src/js/telephone_components.js', function(require){
//     "use strict";

//     const useStore = require('mail/static/src/component_hooks/use_store.js');

//     const { Component } = owl;
//     const {useRef} = owl.hooks;

//     class AvayaHistory extends Component {
//         /**
//          * @override
//          */
//         constructor(...args) {
//             super(...args);
//             /**
//              * global JS generated ID for this component. Useful to provide a
//              * custom class to autocomplete input, so that click in an autocomplete
//              * item is not considered as a click away from messaging menu in mobile.
//              */
//             this._componentRef = useRef('historylog');
//             this._onClickGlobal = this._onClickGlobal.bind(this);
//             useStore(props => {
//                 const historylog = this.env.model['avaya.call.history'].get()
//             })
//         }
//     }
// })