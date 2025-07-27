from odoo import api, fields, models

class ResUser(models.Model):
    _inherit = 'res.users'

    allowed_customer_ids = fields.Many2many(
        'res.partner',
        string='Allowed Customers',
        help='Customers that this user is allowed to access.',
    )



class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        restricted_customer = self.env.user.has_group('rgb_restrict_customer.group_rgb_restrict_customer')
        if restricted_customer:
            args = [('id', 'in', self.env.user.allowed_customer_ids.ids)] + list(args)
        return super(ResPartner, self)._search(args, offset, limit, order, count, access_rights_uid)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        restricted_customer = self.env.user.has_group('rgb_restrict_customer.group_rgb_restrict_customer')
        if restricted_customer:
            args += [('partner_id', 'in', self.env.user.allowed_customer_ids.ids)]
        return super(AccountMove, self)._search(args, offset, limit, order, count, access_rights_uid)

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        restricted_customer = self.env.user.has_group('rgb_restrict_customer.group_rgb_restrict_customer')
        if restricted_customer:
            args += [('partner_id', 'in', self.env.user.allowed_customer_ids.ids)]
        return super(AccountPaymentTerm, self)._search(args, offset, limit, order, count, access_rights_uid)