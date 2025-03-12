

from odoo import fields, models


class FreightShipper(models.Model):
    _name = 'freight.shipper'

    name = fields.Char('Name',required=True)

    