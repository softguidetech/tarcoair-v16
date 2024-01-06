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
     analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

class AccountMoveLineInherit(models.Model):
     _inherit = 'account.move.line'

     analytic_account_id = fields.Many2one(related='move_id.analytic_account_id', string='Analytic Account')

     @api.onchange('analytic_account_id')
     def onchange_analytic_account_id(self):
          self.analytic_distribution = False
          if self.analytic_account_id:
               self.analytic_distribution = {self.analytic_account_id.id: 100}