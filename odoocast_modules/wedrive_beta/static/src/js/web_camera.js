<odoo>
    <data>

        <!-- views/vehicle_model_form.xml -->
        <record model="ir.ui.view" id="view_vehicle_model_form">
            <field name="name">vehicle.model.form</field>
            <field name="model">vehicle.model</field>
            <field name="arch" type="xml">
                <form string="Vehicle">
                    <sheet>
                        <div class="oe_title">
                            <label for="plate" class="oe_edit_only" />
                            <h1>
                                <field name="plate" class="oe_inline oe_editable" />
                            </h1>
                        </div>
                        <group>
                            <field name="marca" />
                            <field name="modelo" />
                            <field name="ano" />
                            <field name="cor" />
                            <field name="chassi" />
                            <field name="municipio" />
                            <field name="uf" />
                            <field name="segmento" />
                            <field name="anoModelo" />
                            <field name="subsegmento" />
                            <field name="combustivel" />
                            <field name="cilindradas" /> 
                        </group>
                    </sheet>
                </form>
            </field>
        </record>

        <!-- views/vehicle_ocr_api_view.xml -->

        <!-- Definição da ação para abrir a visualização do modelo -->
        <record model="ir.actions.act_window" id="action_vehicle">
            <field name="name">Veículos</field>
            <field name="res_model">vehicle.model</field>
            <field name="view_mode">tree,form</field>
        </record>

        <!-- Definição do menu principal -->
        <menuitem id="menu_vehicle_main" name="Wedrive" action="action_vehicle" sequence="10" />

    </data>
</odoo>
