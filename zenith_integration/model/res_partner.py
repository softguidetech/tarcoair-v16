from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    client_id = fields.Char('Client ID')

    _sql_constraints = [
            ('client_id', 'unique(client_id)',
             'Client ID must be unique!')
        ]
