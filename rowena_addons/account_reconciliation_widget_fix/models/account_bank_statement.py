from odoo import fields, models


class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    def _create_counterpart_and_new_aml(
        self, counterpart_moves, counterpart_aml_dicts, new_aml_dicts
    ):

        aml_obj = self.env["account.move.line"]

        # Delete previous move_lines
        self.move_id.line_ids.with_context(force_delete=True).unlink()

        # Create liquidity line
        liquidity_aml_dict = self._prepare_liquidity_move_line_vals()
        aml_obj.with_context(check_move_validity=False).create(liquidity_aml_dict)

        self.sequence = self.statement_id.line_ids.ids.index(self.id) + 1
        counterpart_moves = counterpart_moves | self.move_id

        # Complete dicts to create both counterpart move lines and write-offs
        to_create = counterpart_aml_dicts + new_aml_dicts
        date = self.date or fields.Date.today()
        for aml_dict in to_create:
            aml_dict["move_id"] = self.move_id.id
            aml_dict["partner_id"] = self.partner_id.id
            aml_dict["statement_line_id"] = self.id
            self._prepare_move_line_for_currency(aml_dict, date)

        # Create write-offs
        for aml_dict in new_aml_dicts:
            aml_obj.with_context(check_move_validity=False).create(aml_dict)

        # Create counterpart move lines and reconcile them
        aml_to_reconcile = []

        for aml_dict in counterpart_aml_dicts:
            if not aml_dict["move_line"].statement_line_id:
                aml_dict["move_line"].with_context(check_move_validity=False).write({"statement_line_id": self.id})
            if aml_dict["move_line"].partner_id.id:
                aml_dict["partner_id"] = aml_dict["move_line"].partner_id.id
            aml_dict["account_id"] = aml_dict["move_line"].account_id.id

            counterpart_move_line = aml_dict.pop("move_line")
            new_aml = aml_obj.with_context(check_move_validity=False).create(aml_dict)

            aml_to_reconcile.append((new_aml, counterpart_move_line))

        # Post to allow reconcile
        if self.move_id.state != "posted":
            self.move_id.with_context(
                skip_account_move_synchronization=True
            ).action_post()

        # Reconcile new lines with counterpart
        for new_aml, counterpart_move_line in aml_to_reconcile:
            (new_aml | counterpart_move_line).reconcile()

            self._check_invoice_state(counterpart_move_line.move_id)

        # Needs to be called manually as lines were created 1 by 1
        self.move_id.update_lines_tax_exigibility()
        # record the move name on the statement line to be able to retrieve
        # it in case of unreconciliation
        self.write({"move_name": self.move_id.name})

        return counterpart_moves
