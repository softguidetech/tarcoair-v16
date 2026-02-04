# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    total_fixed_tax = fields.Monetary(
        string='Total Fixed Tax',
        compute='_compute_total_fixed_tax',
        currency_field='currency_id',
        store=False,
        help='Total fixed tax amount from all invoice lines'
    )
    
    @api.depends('invoice_line_ids.fixed_tax_amount', 'company_id.enable_fixed_tax', 'move_type')
    def _compute_total_fixed_tax(self):
        """Compute total fixed tax amount from invoice lines"""
        for move in self:
            if move.company_id.enable_fixed_tax and move.is_invoice(include_receipts=True):
                move.total_fixed_tax = sum(move.invoice_line_ids.filtered(
                    lambda l: not l.display_type
                ).mapped('fixed_tax_amount'))
            else:
                move.total_fixed_tax = 0.0

    def _create_fixed_tax_journal_items(self):
        """
        Create journal items for fixed tax amounts from invoice lines.
        This method is called when the invoice is posted.
        Fixed taxes are shown as separate journal items in the Journal Voucher.
        """
        self.ensure_one()
        
        # Check if fixed tax is enabled for the company
        if not self.company_id.enable_fixed_tax:
            return
        
        if not self.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'):
            return
        
        # Check if fixed tax journal items already exist
        existing_fixed_tax_items = self.line_ids.filtered(
            lambda l: l.name and ('Fixed Tax' in l.name or 'Fixed Tax Adjustment' in l.name)
        )
        if existing_fixed_tax_items:
            # Remove existing fixed tax items to recreate them
            existing_fixed_tax_items.unlink()
        
        # Get all invoice lines with fixed tax amounts
        lines_with_fixed_tax = self.invoice_line_ids.filtered(
            lambda l: l.fixed_tax_amount and l.fixed_tax_amount != 0.0 and not l.display_type
        )
        
        if not lines_with_fixed_tax:
            return
        
        # Get tax account from company settings
        company = self.company_id
        
        if not company.fixed_tax_account_id:
            _logger.warning('Fixed Tax Account is not configured in company settings for invoice %s. Skipping fixed tax journal items.', self.name)
            raise UserError(_('Fixed Tax Account is not configured in company settings. Please configure it in Company > Fixed Tax settings.'))
        
        tax_account = company.fixed_tax_account_id
        
        # Create journal items for fixed taxes
        journal_items = []
        total_fixed_tax = sum(lines_with_fixed_tax.mapped('fixed_tax_amount'))
        
        if total_fixed_tax == 0:
            return
        
        # Determine debit/credit based on move type
        # For customer invoices: tax increases total (debit receivable, credit tax)
        # For vendor bills: tax increases total (credit payable, debit tax)
        is_customer_invoice = self.move_type in ('out_invoice', 'out_refund')
        is_refund = self.move_type in ('out_refund', 'in_refund')
        
        # Get receivable/payable account from existing lines
        receivable_payable_line = self.line_ids.filtered(
            lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable') and not l.display_type
        )
        if not receivable_payable_line:
            _logger.warning('Cannot find receivable/payable account for fixed tax on invoice %s. Skipping fixed tax journal items.', self.name)
            return
        
        receivable_payable_account = receivable_payable_line[0].account_id
        
        # Calculate tax amounts based on move type
        # For customer invoices: tax increases receivable (debit receivable, credit tax)
        # For vendor bills: tax increases payable (credit payable, debit tax)
        if is_customer_invoice:
            if is_refund:
                # Customer refund: reduce receivable, so credit receivable and debit tax
                tax_debit = abs(total_fixed_tax)
                tax_credit = 0.0
                receivable_debit = 0.0
                receivable_credit = abs(total_fixed_tax)
            else:
                # Customer invoice: increase receivable, so debit receivable and credit tax
                tax_debit = 0.0
                tax_credit = abs(total_fixed_tax)
                receivable_debit = abs(total_fixed_tax)
                receivable_credit = 0.0
        else:
            # Vendor bill
            if is_refund:
                # Vendor refund: reduce payable, so debit payable and credit tax
                tax_debit = 0.0
                tax_credit = abs(total_fixed_tax)
                payable_debit = abs(total_fixed_tax)
                payable_credit = 0.0
            else:
                # Vendor bill: increase payable, so credit payable and debit tax
                tax_debit = abs(total_fixed_tax)
                tax_credit = 0.0
                payable_debit = 0.0
                payable_credit = abs(total_fixed_tax)
        
        # Calculate amount_currency for tax line
        if self.currency_id != self.company_id.currency_id:
            # For customer invoices, tax amount is negative in currency (credit side)
            # For vendor bills, tax amount is positive in currency (debit side)
            if is_customer_invoice:
                tax_amount_currency = -abs(total_fixed_tax) if not is_refund else abs(total_fixed_tax)
            else:
                tax_amount_currency = abs(total_fixed_tax) if not is_refund else -abs(total_fixed_tax)
        else:
            tax_amount_currency = 0.0
        
        # Create tax journal item (shows as separate line in JV)
        # The tax line will debit/credit the receivable/payable account and credit/debit the tax account
        # This ensures the move stays balanced
        tax_journal_item_vals = {
            'move_id': self.id,
            'name': _('Fixed Tax Amount'),
            'account_id': tax_account.id,
            'debit': tax_debit,
            'credit': tax_credit,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'date': self.date,
            'date_maturity': self.invoice_date_due or self.date,
            'display_type': 'tax',
            'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
            'amount_currency': tax_amount_currency,
        }
        
        journal_items.append(tax_journal_item_vals)
        
        # Create offsetting entry in receivable/payable account
        # This adjusts the receivable/payable to include the fixed tax amount
        offset_journal_item_vals = {
            'move_id': self.id,
            'name': _('Fixed Tax Adjustment'),
            'account_id': receivable_payable_account.id,
            'debit': receivable_debit if is_customer_invoice else payable_debit,
            'credit': receivable_credit if is_customer_invoice else payable_credit,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'date': self.date,
            'date_maturity': self.invoice_date_due or self.date,
            'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
            'amount_currency': -tax_amount_currency if self.currency_id != self.company_id.currency_id else 0.0,
        }
        
        journal_items.append(offset_journal_item_vals)
        
        # Create all journal items
        if journal_items:
            self.env['account.move.line'].with_context(check_move_validity=False).create(journal_items)
            _logger.info('Created %d journal items for fixed taxes on invoice %s', len(journal_items), self.name)

    def action_post(self):
        """Override to create fixed tax journal items before posting"""
        result = super(AccountMove, self).action_post()
        
        # Create journal items for fixed taxes after posting
        for move in self:
            if move.state == 'posted':
                move._create_fixed_tax_journal_items()
        
        return result

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        """Override to include fixed tax amounts in tax computation"""
        result = super(AccountMove, self)._recompute_tax_lines(recompute_tax_base_amount=recompute_tax_base_amount)
        
        # After recomputing taxes, ensure fixed tax journal items are created if invoice is posted
        for move in self:
            if move.state == 'posted':
                # Check if fixed tax journal items already exist
                existing_fixed_tax_items = move.line_ids.filtered(
                    lambda l: 'Fixed Tax' in (l.name or '')
                )
                if not existing_fixed_tax_items:
                    move._create_fixed_tax_journal_items()
        
        return result

