from odoo import models,fields, api,_
from odoo.exceptions import ValidationError
import os
from twilio.rest import Client

class AccountMove(models.Model):
    _inherit = 'account.move'

    mobile = fields.Char('Mobile')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.mobile = False
        if self.partner_id and self.partner_id.mobile:
            self.mobile = self.partner_id.mobile

    @api.constrains('mobile')
    def _check_mobile(self):
        if not self.mobile:
            raise ValidationError(_('Mobile number needed!!'))

    def action_post(self):
        res = super(AccountMove,self).action_post()
        for rec in self:
            config  = self.env['ir.config_parameter']
            tarcoair_sms_template_id = config.sudo().get_param('sms_integration.tarcoair_sms_template_id') or False
            account_sid = config.sudo().get_param('sms_integration.account_sid') or False
            auth_token = config.sudo().get_param('sms_integration.auth_token') or False
            sms_host_number = config.sudo().get_param('sms_integration.sms_host_number') or False
            if account_sid and auth_token and sms_host_number:
                if tarcoair_sms_template_id:
                    tarcoair_sms_template = self.env['tarcoair.sms.template'].sudo().browse(int(tarcoair_sms_template_id))
                    template = tarcoair_sms_template.template
                    # account_sid = 'AC168e43587af4fe9d71819cc1cb0110ff'
                    # auth_token = 'bfe62a97948947b91cbda59e02183b7c'
                    client = Client(account_sid, auth_token)
                    message = client.messages \
                        .create(
                        body= template,
                        from_= sms_host_number,
                        to= rec.mobile
                    )
                else:
                    raise ValidationError(_('Please configure Invoice SMS Template!!'))
            else:
                raise ValidationError(_('Please configure Twilio Account SID , Twilio Auth Token and SMS Host Mobile!!'))

        return res

