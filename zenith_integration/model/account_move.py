from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_show_zenith_sync_wizard(self):
        view_id = self.env.ref('zenith_integration.view_zenith_sync_wizard_form').id
        return {
            'name': 'Zenith Sync Wizard',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'zenith.sync.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
