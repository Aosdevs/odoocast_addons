from odoo import models, fields
from odoo.tools import float_is_zero


class ProductTemplate(models.Model):
    _inherit = "product.template"

    parent_code = fields.Char(string="Código Pai")
    website_default_quantity = fields.Float(
        string="Quantidade no Site",
        help="Quantidade padrão do produto ao ser adicionado no carrinho através do e-Commerce",
        default=1,
    )

    # Disable combination if product standard price is 0
    def _is_combination_possible(
        self, combination, parent_combination=None, ignore_no_variant=False
    ):
        self.ensure_one()
        variant = self._get_variant_for_combination(combination)
        if float_is_zero(
            variant.standard_price,
            precision_rounding=self.env.company.currency_id.rounding,
        ):
            return False
        return super(ProductTemplate, self)._is_combination_possible(
            combination, parent_combination, ignore_no_variant
        )
