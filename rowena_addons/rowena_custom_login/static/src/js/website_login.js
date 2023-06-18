odoo.define('rowena_custom_login.login', function (require) {

    var publicWidget = require('web.public.widget');
    var QWeb  = require('web.core').qweb;
    var ajax = require('web.ajax');
    var session = require('web.session');

    publicWidget.registry.websiteCustomLogin = publicWidget.Widget.extend({
        selector: "ul#top_menu",
        xmlDependencies: [
            '/rowena_custom_login/static/src/xml/templates.xml',
        ],

        events: {
            'click a[href="/web/login"]': 'onClickLogin',
            'show_login_sidebar': 'onShowLoginSidebar',
        },

        init: function(parent, args){
            this.is_first_step = true;
            this._super.apply(this, arguments);
            this.redirect = this.getLocation();
        },

        start: function(){
            var self = this;
            return this._super.apply(this, arguments).then( () => {
                $("#wrap").append($(QWeb.render("rowena_custom_login.login_template", {'redirect': this.redirect})));
                $("input[name='csrf_token").val(odoo.csrf_token);
                self.bindEvents();
            });
        },

        bindEvents: function() {
            $("#close-custom-login").on('click', this.onCloseCustomLogin.bind(this));
            $(".js_btn_custom_template_advance").on('click', this.onClickAdvance.bind(this));
            $("input[name='cpf']").on('keypress', this.onKeyPressCpf.bind(this));
            $("input[name='password']").on('keypress', this.onKeyPressPassword.bind(this));

            $("#add_to_cart").on('click', this.onClickAddCart.bind(this));
            $("a[href='/shop/cart']").on('click', this.onClickShopCart.bind(this));
        },

        getLocation: function(hash=false) {
            if(hash) return window.location.pathname + window.location.hash;
            else return window.location.pathname;
        },

        // EVENT HANDLERS

        onShowLoginSidebar: function(ev, redirect=false) {
            if(!redirect) redirect = this.redirect;
            $("input[name='redirect']").val(redirect);
            $(".website_custom_login_container").addClass('active');
        },

        onClickLogin: function(ev) {
            ev.preventDefault();
            this.$el.trigger('show_login_sidebar');
        },

        onCloseCustomLogin: function(ev) {
            $(".website_custom_login_container").removeClass('active');
        },

        onKeyPressCpf: function(ev) {
            if (ev.which == 13) {
                this.onClickAdvance(ev);
            }
        },

        onKeyPressPassword: function(ev) {
            if (ev.which == 13) {
                $("#custom-login-form").trigger('submit');
            }
        },

        onClickAddCart: function(ev) {
            if(!session.user_id) {
                ev.stopPropagation();
                ev.preventDefault();
                this.$el.trigger('show_login_sidebar', [this.getLocation(true)]);
            }
        },

        onClickShopCart: function(ev) {
            if(!session.user_id) {
                ev.stopPropagation();
                ev.preventDefault();
                this.$el.trigger('show_login_sidebar', ['/shop/cart']);
            }
        },

        onClickAdvance: function(ev) {
            if(this.is_first_step) {
                ev.preventDefault();
                let val = $("input[name='cpf']").val().replace(/\D/g, "");
                if (val.length > 0) {
                    ajax.jsonRpc('/check_existing_cnpj_cpf', 'call', { 'cpf': val}).then( res =>{
                        if(res.login.length > 0) {
                            $("input[name='cpf']").prop('disabled', true);
                            $("input[name='login']").val(res.login);
                            $(".field-password").show();
                            $("input[name='password']").focus();
                            $('.js_btn_custom_template_advance').html('Entrar');
                            this.is_first_step = false;
                        } else {
                            window.location = `/web/signup?redirect=${this.getLocation(true)}&cpf_cnpj=${val}`;
                        }
                    });
                }
            } else {
                $("#custom-login-form").trigger('submit');
            }
        }
    });

});
