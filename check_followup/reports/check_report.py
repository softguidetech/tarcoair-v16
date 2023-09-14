from odoo import models,fields,api,_

class FleetCarCostReport(models.AbstractModel):
    _name = 'check_followup.check.report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('check_followup.report_check')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.check,
            'docs': self,
        }
        return report_obj.render('check_followup.report_check', docargs)