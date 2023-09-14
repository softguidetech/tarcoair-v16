# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FinancePrintCheckWizard(models.TransientModel):
    _name = "finance.print.check.wizard"
    _description = "Check wizard"

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('finance_vouchers.report_check_printing')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.check.printing,
            'docs': self,
        }
        return report_obj.render('finance_vouchers.report_check_printing', docargs)


