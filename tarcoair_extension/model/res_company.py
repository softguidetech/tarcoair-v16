from odoo import models, fields,api,_

class ResCompany(models.Model):
    _inherit = 'res.company'

    is_required_analytic = fields.Boolean(string='Is Required Analytic', default=False)

    @api.model
    def create(self, vals):
        context = self._context.copy()
        if not context.get('from_company'):
            context['from_company'] = True

            res = super(ResCompany, self).with_context(context).create(vals)

            if res.partner_id:
                res.partner_id.company_id = res.id
            return res
        else:
            return super(ResCompany, self).create(vals)


# @api.model
    # def create(self, vals):
    #     res = super(ResCompany, self).with_context(from_company=True).create(vals)
    #     if res.partner_id:
    #         res.partner_id.company_id = res.id
    #     return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_required_analytic = fields.Boolean(string='Is Required Analytic', related='company_id.is_required_analytic' , readonly=True)

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    is_required_analytic = fields.Boolean(string='Is Required Analytic', related='company_id.is_required_analytic', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Accounts')



