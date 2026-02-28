from odoo import models, fields

class TransactionType(models.Model):
    _name = 'zenith.transaction.type'
    _description = 'Transaction Type'

    name = fields.Char(string='Name', required=True)