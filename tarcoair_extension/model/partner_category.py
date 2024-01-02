from odoo import models, fields,api,_


class PartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    # def default_company(self):
    #     return self.env.company

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    debit_account_id = fields.Many2one('account.account',company_dependent=True, string='Debit Account',
                                       domain="[('account_type', '=', 'asset_receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
                                       )
    credit_account_id = fields.Many2one('account.account',company_dependent=True, string='Credit Account',
                                        domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
                                        )

