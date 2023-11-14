from odoo import fields, models, api, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


# from odoo import amount_to_text


class RelatedPartyBills(models.Model):
    _name = 'related.party.bill'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Related Party Bill'
    _rec_name = 'partner_id'

    def _default_journal(self):
        return self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)

    def _default_currency(self):
        return self.env.user.company_id.currency_id

    def _default_company(self):
        return self.env.user.company_id

    name = fields.Char(string='Name', default='New')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    date = fields.Date(string='Date', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', default=_default_journal)
    state = fields.Selection([('draft', 'Draft'),
                              ('open', 'Open'),
                              ('partial', 'Partial'),
                              ('cancel', 'Cancelled'),
                              ('paid', 'Paid')], default='draft')
    bill_move_id = fields.Many2one('account.move', string='Bill Move')
    payment_move_id = fields.Many2one('account.move', string='Payment Move')
    line_ids = fields.One2many('related.party.bill.line', 'bill_id', string='Bill Lines')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=_default_company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=_default_currency)
    total_amount = fields.Monetary(string='Total amount', compute='_compute_total')
    ref = fields.Char(string='Reference', required=True)
    count_journal_entry = fields.Integer(compute='_compute_jv')
    related_party_name = fields.Char(string='Related party', )

    def _compute_jv(self):
        for rec in self:
            if rec.bill_move_id:
                rec.count_journal_entry = 1
            else:
                rec.count_journal_entry = 0

    @api.model
    def amount_currency_debit(self):
        if self.currency_id != self.env.user.company_id.currency_id:
            return self.total_amount

    @api.model
    def amount_currency_credit(self):
        total = 0
        for rec in self.line_ids:
            total += rec.subtotal
        return total * -1

    def action_confirm(self):
        l = []
        account_move_object = self.env['account.move']

        # Credit line
        credit_val = {
            'name': 'Related Party' + ' ' + str(self.ref),
            'account_id': self.partner_id.property_account_payable_id.id,
            'credit': self.total_amount,
            'partner_id': self.partner_id.id,
        }
        l.append((0, 0, credit_val))

        # Debit lines
        for rec in self.line_ids:
            debit_val = {
                'name': 'Related Party' + ' ' + str(rec.bill_id.ref),
                'account_id': self.partner_id.property_account_payable_id.id,
                'debit': rec.subtotal,
                'partner_id': rec.partner_id.id,
            }
            l.append((0, 0, debit_val))

        vals = {
            'journal_id': self.journal_id.id,
            'date': self.date,
            'ref': self.ref,
            # 'invoice_line_ids': l,
            "invoice_line_ids": [(0, 0, l)]
            }

        self.bill_move_id = account_move_object.create(vals)
        self.bill_move_id.action_post()
        self.state = 'open'

    # def action_confirm(self):
    #     l = []
    #     account_move_object = self.env['account.move']
    #     credit_val = {
    #         'move_id': self.bill_move_id.id,
    #         'name': 'Related Party' + ' ' + str(self.ref),
    #         'account_id': self.partner_id.property_account_payable_id.id,
    #         'credit': self.total_amount,
    #         # 'analytic_account_id': self.analytic_account.id or False,
    #         # 'currency_id': self.currency_id.id,
    #         'partner_id': self.partner_id.id,
    #         # 'amount_currency': self.amount_currency_debit() or False,
    #         # 'company_id': self.company_id.id,
    #
    #     }
    #     l.append((0, 0, credit_val))
    #     for rec in self.line_ids:
    #         debit_val = {
    #
    #             'move_id': rec.bill_id.bill_move_id.id,
    #             'name': 'Related Party' + ' ' + str(rec.bill_id.ref),
    #             'account_id': self.partner_id.property_account_payable_id.id,
    #             'debit': rec.subtotal,
    #             # 'currency_id': rec.bill_id.currency_id.id,
    #             'partner_id': rec.partner_id.id,
    #             # 'amount_currency': self.amount_currency_credit() or False,
    #             # 'analytic_account_id': ,
    #             # 'company_id': ,
    #
    #         }
    #         l.append((0, 0, debit_val))
    #     vals = {
    #         'journal_id': self.journal_id.id,
    #         'date': self.date,
    #         'ref': self.ref,
    #         # 'company_id': ,
    #         # 'line_ids': l,
    #         'invoice_line_ids':[(0, 0, l)],
    #     }
    #     self.bill_move_id = account_move_object.create(vals)
    #     self.bill_move_id.action_post()
    #     self.state = 'open'

    def action_cancel(self):
        if self.bill_move_id:
            self.bill_move_id.button_cancel()
            self.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'

    def _compute_total(self):
        total = 0
        for rec in self:
            for line in rec.line_ids:
                total += line.subtotal
            rec.total_amount = total

    @api.model
    def create(self, vals):
        code = 'related.party.code'
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code(code)
            vals['name'] = seq
        return super(RelatedPartyBills, self).create(vals)

    def action_move_view(self):
        if self.bill_move_id:
            tree_view = self.env.ref('account.view_move_tree')
            form_view = self.env.ref('account.view_move_form')
            return {
                'type': 'ir.actions.act_window',
                'name': 'View Journal Entry',
                'res_model': 'account.move',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
                'domain': [('id', '=', self.bill_move_id.id)],

            }


class RelatedPartyBillsLine(models.Model):
    _name = 'related.party.bill.line'

    name = fields.Char(string='Description', required=True)
    qty = fields.Float(string='Quantity', required=True)
    price = fields.Float(string='Unit Price', required=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal')
    bill_id = fields.Many2one('related.party.bill', string='Bill')
    partner_id = fields.Many2one('res.partner', string='Partner')
    account_id = fields.Many2one('account.account', required=True)

    @api.depends('qty', 'price')
    def _compute_subtotal(self):
        total = 0
        for rec in self:
            rec.subtotal = rec.qty * rec.price
