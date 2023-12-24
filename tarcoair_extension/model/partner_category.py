from odoo import models, fields


class PartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    debit_account_id = fields.Many2one('account.account', string='Debit Account',
                                       domain="[('account_type', '=', 'asset_receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
                                       )
    credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                        domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
                                        )
