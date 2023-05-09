odoo.define('sale_coordenado.controller', function (require) {

    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var QWeb = core.qweb;
    var ajax = require('web.ajax');

    publicWidget.registry.saleCoordenadoController = publicWidget.Widget.extend({
        selector: '.asaas_installment',

        xmlDependencies: [
            '/payment_asaas/static/src/xml/templates.xml',
        ],

        init: function(parent, args) {
            this._super(parent, args);
            this.show_installment = window.location.toString().includes("/shop/payment") && !window.location.toString().includes("/asaas");
        },

        willStart: function () {
            var self = this;
            var superDeferred = this._super();
            var info = ajax.jsonRpc('/shop/asaas_installment_info', 'call', {}).then( res => {
                if (res.max_parcels > 1) {
                    Object.assign(self, res);
                }
            })
            return $.when(superDeferred, info);
        },
        
        start: function () {
            if(this.show_installment && this.max_parcels > 1) {
                this.compute_parcels();
                this.show_installment_template();
            }
            return this._super();
        },

        onChangeInstallment: function(ev) {
            let val = parseInt($(ev.target).val())
            var self = this;
            ajax.jsonRpc('/shop/asaas_installment', 'call', {"installment_number": val}).then( res => {
                if (res.ok) {
                    self.current_parcels = res.current_parcels;
                    self.show_installment_template({"success": "Parcelamento atualizado com sucesso!"})
                } else {
                    self.show_installment_template({"error": res.message})
                }
            })
        },

        compute_parcels: function() {
            this.parcels_list = []
            for(var i=1; i <= this.max_parcels; i++) {
                this.parcels_list.push([i, (this.amount / i).toFixed(2)]);
            }
        },

        show_installment_template: function(message={}) {
            this.$el.html('');
            var $template = $(QWeb.render("payment_asaas.asaas_installment_template", {
                parcels: this.parcels_list,
                current_parcels: this.current_parcels,
                message: message
            }));
            $template.appendTo(this.$el);
            this.$el.find('#installment_select').change(_.bind(this.onChangeInstallment, this));
        }

    });
});