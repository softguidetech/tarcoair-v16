from odoo import models, fields, api


class ZenithSyncWizard(models.TransientModel):
    _name = 'zenith.sync.wizard'
    _description = 'Zenith Sync Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    transaction_type_id = fields.Many2one('zenith.transaction.type', string='Transaction Type', required=True)
    location_id = fields.Many2one('hr.work.location', string='Location', required=True)
    classification_id = fields.Many2one('zenith.transaction.classification', string='Transaction Classification', required=True)

    def button_sync(self):
        return {'type': 'ir.actions.act_window_close'}
