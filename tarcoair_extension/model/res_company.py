from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    is_required_analytic = fields.Boolean(string='Is Required Analytic')

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_required_analytic = fields.Boolean(string='Is Required Analytic', related='company_id.is_required_analytic')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Accounts')

class AccountAnalytic(models.Model):
    _inherit = 'account.analytic.account'

    is_required_analytic = fields.Boolean(string='Is Required Analytic', related='company_id.is_required_analytic')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Accounts')

