# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    enable_fixed_tax = fields.Boolean(
        string='Enable Fixed Amount Tax',
        default=False,
        help='If enabled, invoice lines will have a fixed tax amount field that creates separate journal items in the Journal Voucher.'
    )

