from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'


class IrActionReport(models.Model):
    _inherit = 'ir.actions.report'


    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        if self._is_invoice_report(report_ref):
            invoices = self.env['account.move'].browse(res_ids)
            if any(m.state != 'posted' and m.company_id.print_only_posted_invoices for m in invoices):
                raise UserError(_("You can only print journal entries that are in 'Posted' state."))

        return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)