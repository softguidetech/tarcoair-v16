from odoo import models, fields, api, _
from odoo.exceptions import AccessError



class ResPartner(models.Model):
    _inherit = "res.partner"

    # @api.model
    # def default_get(self, fields):
    #     res = super(ResPartner, self).default_get(fields)
    #     print(res,"666666666666666666666666666666")
    #     print(res['type'],"77777777777777777777777777777")
    #     if res['type'] != 'contact':
    #         res.update({'company_id': self.env.user.company_id.id,})
    #
    #     return res

    @api.model
    def create(self, vals):
        user = self.env.user
        if user.has_group('tarcoair_extension.group_partner_creation'):
            if not self._context.get('from_company'):
                vals['company_id'] = user.company_id.id
            return super(ResPartner, self).create(vals)
        else:
            raise AccessError(_("You do not have permission to create partners. Please contact your administrator."))

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


