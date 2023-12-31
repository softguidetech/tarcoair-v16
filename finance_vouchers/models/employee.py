from odoo import fields , models,api,tools,_
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError
# from odoo import amount_to_text


class PartnerDirectoryInherit(models.Model):
    _inherit = 'res.partner'

    # custody_account_id = fields.Many2one('account.account',string='Custody Account')
    # is_employee = fields.Boolean(string='Is Employee',default=False)
    is_related_party = fields.Boolean(related='category_id.is_related_party', readonly=True, string="Is related Party")