from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tarcoair_sms_template_id = fields.Many2one('tarcoair.sms.template', string='SMS Template', config_parameter='sms_integration.tarcoair_sms_template_id')
    account_sid = fields.Char(string='Twilio Account SID', config_parameter='sms_integration.account_sid')
    auth_token = fields.Char(string='Twilio Auth Token', config_parameter='sms_integration.auth_token')
    auth_token = fields.Char(string='Twilio Auth Token', config_parameter='sms_integration.auth_token')
    sms_host_number = fields.Char(string='SMS Host Mobile', config_parameter='sms_integration.sms_host_number')
