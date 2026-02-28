from odoo import models, fields

class TransactionClassification(models.Model):
    _name = 'zenith.transaction.classification'
    _description = 'Transaction Classification'

    name = fields.Char(string='Name', required=True)