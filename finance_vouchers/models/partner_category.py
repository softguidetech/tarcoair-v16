from odoo import models, fields


class PartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_related_party = fields.Boolean(string="Is related Party")

