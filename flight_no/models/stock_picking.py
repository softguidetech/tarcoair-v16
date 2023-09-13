from odoo import fields , models,api,tools,_
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError,UserError
# from odoo import amount_to_text


class StockPicking(models.Model):
     _inherit = 'stock.picking'


     root_id = fields.Many2one('root.name',string="Root")
     flight_no = fields.Char(string="Number")

class AccountMove(models.Model):
     _inherit = 'account.move'


     root_id = fields.Many2one('root.name',string="Root")
     flight_no = fields.Char(string="Number")
     username = fields.Char(string="Username")