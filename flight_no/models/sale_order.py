from odoo import fields , models,api,tools,_
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError,UserError
# from odoo import amount_to_text


class SaleOrder(models.Model):
     _inherit = 'sale.order'

     def action_confirm(self):
          res = super(SaleOrder, self).action_confirm()

          for rec in self:
               if rec.picking_ids:
                    for pick_rec in rec.picking_ids:
                         pick_rec.write({
                              'root_id': rec.root_id.id,
                              'flight_no': rec.flight_no,
                         })

          return res


     # def action_confirm(self):
     #
     #      res = super(SaleOrder, self).action_confirm()
     #
     #      for rec in self:
     #
     #           for pick_rec in rec.picking_ids:
     #
     #                pick_rec.write({'root_id': rec.root_id.id
     #           })
     #           pick_rec.write({'flight_no': rec.flight_no
     #
     #                           })
     #
     #      return res



     root_id=fields.Many2one('root.name',string='Root')

     flight_no = fields.Char(string='Number')
     username = fields.Char(string="Username")

     # def action_confirm(self):
     #
     #      if self._get_forbidden_state_confirm() & set(self.mapped('state')):
     #           raise UserError(_(
     #                'It is not allowed to confirm an order in the following states: %s'
     #           ) % (', '.join(self._get_forbidden_state_confirm())))
     #
     #      for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
     #           order.message_subscribe([order.partner_id.id])
     #      self.write({
     #           'state': 'sale',
     #           'date_order': fields.Datetime.now()
     #      })
     #
     #      # Context key 'default_name' is sometimes propagated up to here.
     #      # We don't need it and it creates issues in the creation of linked records.
     #      # context = self._context.copy()
     #      # context.pop('default_name', None)
     #      self._action_confirm()
     #      self._create_invoices()
     #      # self.with_context(context)._action_confirm()
     #
     #      if self.env.user.has_group('sale.group_auto_done_setting'):
     #           self.action_done()
     #      return True


class RootName(models.Model):
     _name = 'root.name'
     name=fields.Char('Root')