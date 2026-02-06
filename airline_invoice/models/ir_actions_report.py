# -*- coding: utf-8 -*-

from odoo import models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def get_valid_action_reports(self, model, record_ids):
        """Override to filter Airline Invoice report to only show for Airline Invoices"""
        result = super(IrActionsReport, self).get_valid_action_reports(model, record_ids)
        
        # If this is for account.move model, filter out Airline Invoice report for non-airline invoices
        if model == 'account.move':
            airline_report = self.env.ref('airline_invoice.action_report_airline_invoice', raise_if_not_found=False)
            if airline_report and airline_report.id in result:
                records = self.env[model].browse(record_ids)
                # Remove report from result if any record is not an airline invoice
                if records and not all(r.is_airline_invoice and r.move_type == 'out_invoice' for r in records):
                    result = [r_id for r_id in result if r_id != airline_report.id]
        
        return result

