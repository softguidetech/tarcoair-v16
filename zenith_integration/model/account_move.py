from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    pnr_alpha = fields.Char(string='PNR Alpha')
    iata_agency_code = fields.Char(string='IATA Agency Code')
    pos = fields.Char(string='Point of Sale')
    customer_name = fields.Char(string='Customer Name')
    customer_zenith_id = fields.Char(string='Customer ID')
    transaction_name = fields.Char(string='Transaction Name')
    payment_type = fields.Char(string='Payment Type')
    balance_sales_currency = fields.Char(string='Balance Sales Currency')
    sale_agent = fields.Char(string='Sale Agent')
    ticket_number = fields.Char(string='Ticket Number')
    heading_st_payment = fields.Char(string='Heading Statement Payment')

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
