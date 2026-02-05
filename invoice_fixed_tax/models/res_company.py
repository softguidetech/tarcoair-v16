# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    enable_fixed_tax = fields.Boolean(
        string='Enable Fixed Amount Tax',
        default=False,
        help='If enabled, invoice lines will have a fixed tax amount field that creates separate journal items in the Journal Voucher.'
    )
    
    fixed_tax_account_id = fields.Many2one(
        'account.account',
        string='Fixed Tax Account',
       
        help='Account to be used for fixed tax journal items. This account will appear in Journal Voucher for fixed tax amounts.'
    )
    
    @api.constrains('enable_fixed_tax', 'fixed_tax_account_id')
    def _check_fixed_tax_account(self):
        """Validate that tax account is set when fixed tax is enabled"""
        for company in self:
            if company.enable_fixed_tax and not company.fixed_tax_account_id:
                raise ValidationError('Fixed Tax Account must be set when Fixed Amount Tax is enabled.')

