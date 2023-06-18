odoo.define('rowena_custom_login.address', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    var BrWebsiteSale = require('br_website_sale.address');

    BrWebsiteSale.include({

        events: _.extend({
            'change #input_parent_cnpj_cpf': 'onChangeParentCnpj',
        }, BrWebsiteSale.prototype.events),

        init: function(parent, args) {
            this._super.apply(this, arguments);
            var queryDict = {};
            window.location.search.substr(1).split("&").forEach(item => queryDict[item.split("=")[0]] = item.split("=")[1]);
            this.default_cpf = queryDict.cpf_cnpj;
        },

        start: function () {
            this._super.apply(this, arguments).then(() => {
                if(this.default_cpf) {
                    let $cpf_input = this.$el.find("#input_cnpj_cpf");
                    $cpf_input.val(this.default_cpf);
                    if(this.default_cpf.length > 11) {
                        let $company = this.$el.find('#radioCompany');
                        $company.prop('checked', true);
                        $company.trigger('change');
                        $cpf_input.mask('00.000.000/0000-00');
                    } else {
                        let $person = this.$el.find("#radioPerson");
                        $person.prop('checked', true);
                        $person.trigger('change');
                        $cpf_input.mask('000.000.000-00');
                    }
                    $cpf_input.trigger('input');
                }
                this.$el.find('#input_parent_cnpj_cpf').mask('00.000.000/0000-00');
                this.$el.find("#id_country").val(this.$el.find('#input_country_id').val());
                this.$el.find("#id_country").trigger('change');
            });
        },

        onChangeParentCnpj: function(ev) {
            let val = $("#input_parent_cnpj_cpf").val().replace(/\D/g, "");
            let $zip = this.$el.find(`input[name="zip"]`);
            let $street2 = this.$el.find(`input[name="street2"]`);
            let $number = this.$el.find(`input[name="l10n_br_number"]`);
            $zip.attr('disable', true);
            $street2.attr('disable', true);
            $number.attr('disable', true);
            ajax.jsonRpc('/get_company_info', 'call', { 'cnpj': val}).then( res =>{
                if(res.ok) {
                    $zip.val(res.zip);
                    $zip.trigger('change');
                    $street2.val(res.street2);
                    $number.val(res.l10n_br_number);
                }
                $zip.attr('disable', false);
                $street2.attr('disable', false);
                $number.attr('disable', false);
            });
        },

        onChangeRadioCompany: function (ev) {
            this._super.apply(this, arguments);
            let $target = $(ev.target);
            let is_person = ($target.val() == 'person' && $target.prop('checked')) || ($target.val() == 'company' && !$target.prop('checked'));
            if (is_person) {
                this.$el.find('.div-parent-cnpj').show();
                this.$el.find('.department-row').show();
            } else {
                this.$el.find('.div-parent-cnpj').hide();
                this.$el.find('.department-row').hide();
            }
        }
    });

});
