from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    sale_account_id = fields.Many2one('account.account',string='Sale Account')
    zenith_partner_id = fields.Many2one('res.partner',string='Ticket Customer')
    zenith_pos = fields.Char(string='Zenith Point of sale')

