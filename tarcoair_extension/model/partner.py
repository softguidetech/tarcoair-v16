from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = "res.partner"

    @api.onchange('category_id')
    def _onchange_category_ids(self):
        debit_accounts = self.env['account.account']
        credit_accounts = self.env['account.account']

        if self.category_id:
            for category in self.category_id:
                debit_accounts |= category.debit_account_id
                credit_accounts |= category.credit_account_id
        self.property_account_receivable_id = debit_accounts and debit_accounts[0].id or False
        self.property_account_payable_id = credit_accounts and credit_accounts[0].id or False


