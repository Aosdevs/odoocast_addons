from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    asaas_installment = fields.Integer(string="Installment", default=1)

    def get_asaas_split_values(self, transaction_id):
        order_line_ids = (
            self.mapped("order_line").filtered(lambda x: not x.is_delivery)
            if "is_delivery" in self._fields
            else self
        )
        agent_lines = self.env["sale.order.line.agent"].search(
            [("object_id", "in", order_line_ids.ids)]
        )
        split = []
        for agent_line in agent_lines:
            wallet_id = agent_line.agent_id.with_context(
                order_id=self.id
            ).get_wallet_id()
            if wallet_id:
                split.append(
                    {
                        "walletId": wallet_id,
                        "fixedValue": agent_line.amount,
                    },
                )
        return {"split": split}
