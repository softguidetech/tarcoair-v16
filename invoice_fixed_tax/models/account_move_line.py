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
    
    @api.onchange('fixed_tax_amount')
    def _onchange_fixed_tax_amount(self):
        """Trigger UI recomputation.

        In Odoo 16 we must not call move._recompute_tax_lines() (it doesn't exist).
        Totals are recomputed automatically via @_compute_totals dependencies.
        """
        for line in self:
            if line.move_id and not line.move_id.company_id.enable_fixed_tax:
                line.fixed_tax_amount = 0.0
    
    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'fixed_tax_amount', 'move_id.company_id.enable_fixed_tax')
    def _compute_totals(self):
        """Override to include fixed tax amount in tax calculation"""
        super(AccountMoveLine, self)._compute_totals()
        
        for line in self:
            if (line.fixed_tax_amount and 
                line.move_id and 
                line.move_id.company_id.enable_fixed_tax and
                line.display_type in ('product', 'cogs')):
                # Add fixed tax amount to price_total (which includes tax)
                # This ensures the VAT amount (price_total - price_subtotal) includes the fixed tax
                if line.price_total is not False and line.price_total is not None:
                    # price_total already includes regular taxes, add fixed tax
                    line.price_total = line.price_total + line.fixed_tax_amount
                elif line.price_subtotal is not False and line.price_subtotal is not None:
                    # If no taxes, add fixed tax to subtotal to get total
                    line.price_total = line.price_subtotal + line.fixed_tax_amount

