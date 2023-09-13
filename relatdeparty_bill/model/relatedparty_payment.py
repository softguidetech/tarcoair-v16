from odoo import fields , models,api,tools,_
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError
# from odoo import amount_to_text


class PaymentAccount(models.Model):
    _inherit = 'account.payment'

    is_contract = fields.Selection([('normal','Normal Payment'),
                                    ('contract','Contract Installment')],string='Is it Contract?')


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_contract = fields.Selection([('normal', 'Normal Payment'),
                                    ('contract', 'Contract Installment')], string='Is it Contract?')

