from odoo import models, api, _
from odoo.exceptions import AccessError

class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def create(self, vals):
        user = self.env.user
        if user.has_group('tarcoair_extension.group_account_creation'):
            return super(AccountAccount, self).create(vals)
        else:
            raise AccessError(_("You do not have permission to create accounts. Please contact your administrator."))
