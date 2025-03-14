
from werkzeug import urls
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError

class CustomClearance(models.Model):
    _name = 'custom.clearance'
    _description = 'Custom Clearance'

    name = fields.Char('Name', compute='_compute_name')
    freight_id = fields.Many2one('freight.order', required=True)
    date = fields.Date('Date')
    agent_id = fields.Many2one('res.partner', 'Agent')
    loading_port_id = fields.Many2one('freight.port', string="Loading Port")
    discharging_port_id = fields.Many2one('freight.port',
                                          string="Discharging Port")
    line_ids = fields.One2many('custom.clearance.line', 'line_id')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('done', 'Done')], default='draft')
    # order_ids = fields.One2many('freight.order.line', 'clearance_id')
    import_main_id = fields.Many2one('import.main',string='Import Mainefest')
    number = fields.Char(string='AWB Number')
    invoice_count = fields.Integer(compute='compute_count')
    
    def compute_count(self):
        for rec in self:
            if rec.env['account.move'].search([('ref', '=', rec.name)]):
                rec.invoice_count = rec.env['account.move'].search_count([('ref', '=', rec.name)])
            else:
                rec.invoice_count = 0
                    
    @api.depends('freight_id')
    def _compute_name(self):
        """Compute the name of custom clearance"""
        for rec in self:
            if rec.freight_id:
                rec.name = 'CC - ' + str(rec.freight_id.name)
            else:
                rec.name = 'CC - '
    
    # 
    def create_invoice(self):
        """Create invoice"""
        lines = []
        if self.import_main_id.line_ids:
            for order in self.import_main_id.line_ids:
                if self.number and order.cargo_type_id:
                    if self.number = order.number:
                        time_days = self.datetime.datetime.now() - order.import_ma_id.entering_date
                        hours= time_days.days * 24
                        price_unit = order.cargo_type_id.price
                        value = (0, 0, {
                            'name': order.number,
                            'price_unit': price_unit,
                            'quantity': hours,
                        })
                        lines.append(value)
                    
                        invoice_line = {
                            'move_type': 'out_invoice',
                            'partner_id': order.consignee.id,
                            'invoice_user_id': self.env.user.id,
                            'invoice_origin': order.number,
                            'ref': self.name,
                            'invoice_line_ids': lines,
                        }
                        inv = self.env['account.move'].sudo().create(invoice_line)
                        result = {
                            'name': 'action.name',
                            'type': 'ir.actions.act_window',
                            'views': [[False, 'form']],
                            'target': 'current',
                            'res_id': inv.id,
                            'res_model': 'account.move',
                        }
                        self.state = 'done'
                        return result
                else:
                    raise ValidationError('Please write correct Number to proceed the invoice!!')


    # 
    
    @api.onchange('freight_id')
    def _onchange_freight_id(self):
        """Getting default values for loading and discharging port"""
        for rec in self:
            rec.date = rec.freight_id.order_date
            rec.loading_port_id = rec.freight_id.loading_port_id
            rec.discharging_port_id = rec.freight_id.discharging_port_id
            rec.agent_id = rec.freight_id.agent_id

    def action_confirm(self):
        """Send mail to inform agents to custom clearance is confirmed"""
        for rec in self:
            rec.name = 'CC' \
                       ' - ' + rec.freight_id.name
            rec.state = 'confirm'
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            Urls = urls.url_join(base_url, 'web#id=%(id)s&model=custom.clearance&view_type=form' % {'id': self.id})
            Urls_ = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.freight_id.id})

            mail_content = _('Hi %s,<br>'
                             'The Custom Clearance %s is confirmed'
                             '<div style = "text-align: center; '
                             'margin-top: 16px;"><a href = "%s"'
                             'style = "padding: 5px 10px; font-size: 12px; '
                             'line-height: 18px; color: #FFFFFF; '
                             'border-color:#875A7B;text-decoration: none; '
                             'display: inline-block; '
                             'margin-bottom: 0px; font-weight: 400;'
                             'text-align: center; vertical-align: middle; '
                             'cursor: pointer; white-space: nowrap; '
                             'background-image: none; '
                             'background-color: #875A7B; '
                             'border: 1px solid #875A7B; border-radius:3px;">'
                             'View %s</a></div>'
                             '<div style = "text-align: center; '
                             'margin-top: 16px;"><a href = "%s"'
                             'style = "padding: 5px 10px; font-size: 12px; '
                             'line-height: 18px; color: #FFFFFF; '
                             'border-color:#875A7B;text-decoration: none; '
                             'display: inline-block; '
                             'margin-bottom: 0px; font-weight: 400;'
                             'text-align: center; vertical-align: middle; '
                             'cursor: pointer; white-space: nowrap; '
                             'background-image: none; '
                             'background-color: #875A7B; '
                             'border: 1px solid #875A7B; border-radius:3px;">'
                             'View %s</a></div>'
                             ) % (rec.agent_id.name, rec.name, Urls,
                                  rec.name, Urls_, self.freight_id.name)
            main_content = {
                'subject': _('Custom Clerance For %s') % self.freight_id.name,
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': rec.agent_id.email,
            }
            mail_id = self.env['mail.mail'].create(main_content)
            mail_id.mail_message_id.body = mail_content
            mail_id.send()

    def action_revision(self):
        """Creating custom revision"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Received/Delivered',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'custom.clearance.revision.wizard',
            'context': {
                'default_custom_id': self.id
            }
        }

    def get_revision(self):
        """Getting details of custom revision"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Revision',
            'view_mode': 'tree,form',
            'res_model': 'custom.clearance.revision',
            'domain': [('clearance_id', '=', self.id)],
            'context': "{'create': False}"
        }


class CustomClearanceLine(models.Model):
    _name = 'custom.clearance.line'
    _description = 'Custom Clearance Line'

    
    shipper_id = fields.Many2one('freight.shipper', 'Shipper', required=True,
                                 help="Shipper's Details")
    consignee_id = fields.Many2one('freight.consignee', 'Consignee',
                                   help="Details of consignee")

    name = fields.Char('Document Name')
    document = fields.Binary(string="Documents", store=True, attachment=True)
    line_id = fields.Many2one('custom.clearance')
    

class CustomClearanceRevision(models.Model):
    _name = 'custom.clearance.revision'
    _description = 'Custom Clearance Revision'

    name = fields.Char('Name')

    name = fields.Char()
    reason = fields.Text()
    clearance_id = fields.Many2one('custom.clearance')
