

from odoo import fields, models


class FreightConsignee(models.Model):
    _name = 'freight.consignee'

    name = fields.Char('Name',required=True)
    