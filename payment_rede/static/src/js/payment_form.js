odoo.define('payment_asaas.payment_form', function (require) {
    "use strict";

    var core = require('web.core');
    var PaymentForm = require('payment.payment_form');

    PaymentForm.include({

        jsLibs: [
            '/payment_asaas/static/src/lib/jquery.mask.min.js'
        ],

        events: _.extend({
            "change input[name='asaas-card-number']": 'onChangeCardNumber',
            "change input[name='asaas-card-cvc']": 'onChangeCardCVC',
            "change input[name='asaas-card-expiry']": 'onChangeCardExpiry',
        }, PaymentForm.prototype.events),

        start: function() {
            return this._super.apply(this, arguments).then( () => this.radioClickEvent(false));
        },

        bindCreditCardEvents: function() {
            let $number = this.$("input[name='asaas-card-number']")
            let $expiry = this.$("input[name='asaas-card-expiry']")
            let $cvc = this.$("input[name='asaas-card-cvc']")
            try{
                $number.mask("0000 0000 0000 0000");
                $expiry.mask("00/0000");
                $cvc.mask("000");
            } catch (e) {
                console.log(e);
            }
        },

        radioClickEvent: function (ev) {
            this._super.apply(this, arguments);
            this.bindCreditCardEvents();
        },

        // New event handlers

        onChangeCardNumber: function(ev) {
            let $element = $(ev.currentTarget)
            let is_valid = $.payment.validateCardNumber($element.val());
            if(!is_valid) $element.closest('div.form-group').addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
            else $element.closest('div.form-group').removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
        },

        onChangeCardCVC: function(ev) {
            let $element = $(ev.currentTarget)
            let is_valid = $.payment.validateCardCVC($element.val());
            if(!is_valid) $element.closest('div.form-group').addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
            else $element.closest('div.form-group').removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
        },

        onChangeCardExpiry: function(ev) {
            let $element = $(ev.currentTarget)
            let value = $element.val().split('/');
            if(value.length != 2) {
                var is_valid = false;
            } else {
                var is_valid = $.payment.validateCardExpiry(value[0], value[1]);
            }
            if(!is_valid) $element.closest('div.form-group').addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
            else $element.closest('div.form-group').removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
        }
    });

});