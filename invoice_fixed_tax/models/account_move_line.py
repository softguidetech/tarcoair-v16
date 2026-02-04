# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fixed_tax_amount = fields.Float(
        string='Fixed Tax Amount',
        digits='Product Price',
        default=0.0,
        help='Fixed tax amount for this invoice line. This will be shown as a separate journal item in the Journal Voucher. Only available if enabled in company settings.'
    )
    
    company_enable_fixed_tax = fields.Boolean(
        string='Company Fixed Tax Enabled',
        related='move_id.company_id.enable_fixed_tax',
        readonly=True,
        store=False
    )

    @api.constrains('fixed_tax_amount')
    def _check_fixed_tax_amount(self):
        """Validate that fixed tax amount is not negative"""
        for line in self:
            if line.fixed_tax_amount < 0:
                raise ValidationError(_('Fixed tax amount cannot be negative.'))
            # Check if fixed tax is enabled for the company
            if line.fixed_tax_amount and line.move_id and line.move_id.company_id:
                if not line.move_id.company_id.enable_fixed_tax:
                    raise ValidationError(_('Fixed tax amount is not enabled for this company. Please enable it in company settings.'))

