from odoo import models,fields,api,_

class CheckInboundReport(models.AbstractModel):
    _name = 'check.inbound.report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('finance_vouchers.report_check_inbound')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.check.inbound,
            'docs': self,
        }
        return report_obj.render('finance_vouchers.report_check_inbound', docargs)