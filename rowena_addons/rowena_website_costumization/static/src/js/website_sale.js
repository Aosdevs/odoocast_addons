odoo.define('rowena_website_customization.website_sale', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.WebsiteSale.include({
        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then( () => {
                let product_id = parseInt(self.$el.find('.product_id').val());
                let $quantity = self.$el.find("input[name='add_qty']");
                ajax.jsonRpc('/rowena_product_info', 'call', { product_id }).then( result => {
                    if(result.ok) {
                        $quantity.val(result.website_default_quantity);
                    } else {
                        $quantity.val(1);
                    }
                    $quantity.trigger('change');
                    self.$el.find('.oe_cart .js_quantity').trigger('change');
                });
            });
        },
        _onChangeCombination: function (ev, $parent, combination) {
            this._super.apply(this, arguments);
            let product_id = parseInt($parent.find('.product_id').val());
            ajax.jsonRpc('/rowena_product_info', 'call', { product_id }).then( result => {
                if(result.ok) {
                    $("#display_default_code").text(result.default_code);
                } else {
                    $("#display_default_code").text("-");
                }
            });
        }
    });
});
