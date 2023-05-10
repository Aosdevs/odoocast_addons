odoo.define('aspl_float_fuel_meter.widget', function(require) {
    "use strict";
    var core = require('web.core');
    var widget = require('web.basic_fields');
    var fieldRegistry = require('web.field_registry');
    var FieldFuel = widget.FieldFloat.extend({
        template : 'FieldFuel',
        _getValue : function() {
           return this.$('input').val();
          },
          _render : function() {

                      var $this = this
                        var value = this.value
                          var maxvalue = parseInt($this.$('input')[0].max)
                          var steps = parseInt($this.$('input')[0].step)
                          var $slider = this.$("#fuelgauge")
                          var fuelgauge = this.$("#fuelgauge").dynameter({
                                width: 200,
                                label:'fuel',
                                value: 0.0,
                                min: 0.0,
                                max: maxvalue,
                                unit:'ltr',
                              });

                        var show_value = this.value;
                        var $input = this.$el.find('input');
                        var $fuelgauge = this.$el.find('#fuelgauge');
                        $input.mousemove(function(e) {
                          if (e.buttons == 1) {
                             fuelgauge.changeValue(parseInt($input.val()))
                          }
                        });
                         $input.click(function(e) {
                             fuelgauge.changeValue(parseInt($input.val()))
                        });
                           $input.val(show_value);

                  if (this.mode === 'edit'){
                        this.$("#fuelgauge").dynameter({value:$this.value})
                  }
                  else{
                        this.$("#fuelgauge").dynameter({value:$this.value})
                        this.$('#fuel-gauge-control').hide();
                  }
                this.$('input').val($this.value)
          },
          _onInput: function(){
            this.$input = this.$('input');
            this._super();
            }
    });
    fieldRegistry.add('fuelgauge', FieldFuel);
    return {
       FieldFuel : FieldFuel
    };
});
