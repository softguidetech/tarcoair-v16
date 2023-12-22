from odoo import models,fields,api,_

class CheckVoucherReport(models.AbstractModel):
    _name = 'check.voucher.report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('finance_vouchers.report_check')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.check.voucher,
            'docs': self,
        }
        return report_obj.render('finance_vouchers.report_check', docargs)