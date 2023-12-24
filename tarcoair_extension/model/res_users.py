from odoo import models, fields, api

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    users_ids = fields.Many2many('res.users', string='Users', default=lambda self: self._default_users())


    @api.model
    def _default_users(self):
        return [(6, 0, [self.env.user.id])]


class ResUsers(models.Model):
    _inherit = 'res.users'

    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic Accounts')


