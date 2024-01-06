from odoo import models, fields

class SmsTemplate(models.Model):
    _name = 'tarcoair.sms.template'
    _description = 'SMS Templates'

    name = fields.Char(string='Template Name', required=True)
    template = fields.Text(string='SMS Template', required=True)
