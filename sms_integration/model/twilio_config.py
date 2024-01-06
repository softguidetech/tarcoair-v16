from odoo import models, fields

class TwilioConfig(models.Model):
    _name = 'twilio.config'
    _description = 'Twilio Configuration'

    account_sid = fields.Char(string='Twilio Account SID', required=True)
    auth_token = fields.Char(string='Twilio Auth Token', required=True)
