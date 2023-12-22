from odoo import models, fields, api


class FleetExtension(models.Model):
    _inherit = 'fleet.vehicle'

    license_date = fields.Date('License date')
    insurance_date = fields.Date('Insurance date')
