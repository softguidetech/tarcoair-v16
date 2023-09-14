from odoo import fields , models,api,tools,_
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError,UserError
# from odoo import amount_to_text


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    check_followup = fields.Boolean(string='تفاصيل الشيك',copy=False)
    electronic_trans = fields.Boolean(string='تحويل الكتروني', copy=False)
    # cash_unit = fields.Boolean(string='فئات العملة', copy=False)
    # unit_500=fields.Float(string='500 X')
    # unit_tl_500 = fields.Float(compute='_compute_units', readonly=True,string='total 500')
    # unit_200 = fields.Float(string='200 X')
    # unit_tl_200 = fields.Float(compute='_compute_units', readonly=True,string='total 200')
    # unit_100 = fields.Float(string='100 X')
    # unit_tl_100 = fields.Float(compute='_compute_units', readonly=True,string='total 100')
    # unit_50 = fields.Float(string='50 X')
    # unit_tl_50 = fields.Float(compute='_compute_units', readonly=True,string='total 50')
    # unit_20 = fields.Float(string='20 X')
    # unit_tl_20 = fields.Float(compute='_compute_units', readonly=True,string='total 20')
    # unit_10 = fields.Float(string='10 X')
    # unit_tl_10 = fields.Float(compute='_compute_units', readonly=True,string='total 10')
    # unit_other= fields.Float(string='Other X')
    # total_units = fields.Float(compute='_compute_units', readonly=True, string='Total')
    # unit_tl_other = fields.Float(compute='_compute_units', readonly=True,string='total Other')
    # total_other_value = fields.Float(string='Other Amount')
    bank_type = fields.Selection(related='journal_id.type')
    check_date = fields.Date(string='Check Date',copy=False)
    cheque_number = fields.Char(string='Check Number',copy=False)
    check_count = fields.Integer(compute='_compute_check')
    num2wo = fields.Char(string="المبلغ كتابة",compute='_onchange_amount',store=True)

    #@api.one
    def _compute_check(self):
        payment_count = self.env['check.followup'].sudo().search_count([('payment_id','=',self.id)])
        self.check_count = payment_count

    @api.depends('amount', 'currency_id')
    def _onchange_amount(self):
        for rec in self:
          rec.num2wo = str(rec.currency_id.amount_to_text(rec.amount)) + ' '+  'فقط لا غير'

    # @api.depends('total_units','unit_500','unit_200','unit_100','unit_50','unit_20','unit_10','unit_other','total_other_value','unit_tl_10')
    # def _compute_units(self):
    #     for obj in self:
    #      total_500 = obj.unit_500 * 500
    #      total_200 = obj.unit_200 * 200
    #      total_100 = obj.unit_100 * 100
    #      total_50 = obj.unit_50 * 50
    #      total_20 = obj.unit_20 * 20
    #      total_10 = obj.unit_10 * 10
    #      total_other = obj.unit_other * obj.total_other_value
    #      obj.unit_tl_500=total_500
    #      obj.unit_tl_200 = total_200
    #      obj.unit_tl_100 = total_100
    #      obj.unit_tl_50 = total_50
    #      obj.unit_tl_20 = total_20
    #      obj.unit_tl_10 = total_10
    #      obj.unit_tl_other = total_other
    #      obj.total_units = total_500 + total_200 + total_100 + total_50 + total_20 + total_10 + total_other
    # @api.one
    def action_check_view(self):
        if self.payment_type == 'inbound':
            tree_view_in = self.env.ref('check_followup.view_tree_check_followup_in')
            form_view_in = self.env.ref('check_followup.view_form_check_followup_in')
            return {
                'type': 'ir.actions.act_window',
                'name': 'View Customer Checks',
                'res_model': 'check.followup',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view_in.id, 'tree'), (form_view_in.id, 'form')],
                'domain': [('payment_id', '=', self.id)],

            }
        if self.payment_type == 'outbound':
            tree_view_out = self.env.ref('check_followup.view_tree_check_followup_out')
            form_view_out = self.env.ref('check_followup.view_form_check_followup_out')
            return {
                'type': 'ir.actions.act_window',
                'name': 'View Vendor Checks',
                'res_model': 'check.followup',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view_out.id, 'tree'), (form_view_out.id, 'form')],
                'domain': [('payment_id', '=', self.id)],

            }

    @api.model
    def get_currency(self):
        if self.currency_id != self.env.user.company_id.currency_id:
            return self.currency_id.id

    @api.model
    def amount_currency_credit(self):
        if self.currency_id != self.env.user.company_id.currency_id:
            return self.amount * -1

    @api.model
    def amount_currency_debit(self):
        if self.currency_id != self.env.user.company_id.currency_id:
            return self.amount

    @api.model
    def get_amount(self):
        if self.currency_id != self.env.user.company_id.currency_id:
            return self.amount / self.currency_id.rate
        if self.currency_id == self.env.user.company_id.currency_id:
            return self.amount


    def post(self):
        # if self.state != 'draft':
        #     raise UserError(_("Only a draft payment can be posted."))
        #
        # if any(inv.state != 'open' for inv in self.invoice_ids):
        #     raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
        #
        #     # keep the name in case of a payment reset to draft
        # if not self.name:
        #     # Use the right sequence to set the name
        #     if self.payment_type == 'transfer':
        #         sequence_code = 'account.payment.transfer'
        #     else:
        #         if self.partner_type == 'customer':
        #             if self.payment_type == 'inbound':
        #                 sequence_code = 'account.payment.customer.invoice'
        #             if self.payment_type == 'outbound':
        #                 sequence_code = 'account.payment.customer.refund'
        #         if self.partner_type == 'supplier':
        #             if self.payment_type == 'inbound':
        #                 sequence_code = 'account.payment.supplier.refund'
        #             if self.payment_type == 'outbound':
        #                 sequence_code = 'account.payment.supplier.invoice'
        #     self.name = self.env['ir.sequence'].with_context(ir_sequence_date=self.payment_date).next_by_code(sequence_code)
        #     if not self.name and self.payment_type != 'transfer':
        #         raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

        # rec = super(AccountPaymentInherit,self).post()
        super(AccountPaymentInherit,self).post()
        move_id = self.env['account.move.line'].search([('payment_id','=',self.id)],limit=1)

        # if self.cash_unit == True and self.total_units != self.amount:
        #     raise ValidationError(_('اجمالي المبلغ لا يساوي اجمالي فئات العملة'))
        if self.check_followup == True and self.journal_id.type == 'bank':
            if not self.journal_id.out_account and not self.journal_id.in_account:
                raise ValidationError(_('Please Insert Outstanding/ Under Collection Accounts in JOURNAL !!'))
            if self.journal_id.out_account and self.journal_id.in_account:
                if self.payment_type == 'inbound':


                    move_id.sudo().write({'ref': self.name})
                    ###########CreateCheck###############
                    check_obj = self.env['check.followup']
                    check_val = {
                        'check_date': self.check_date,
                        'cheque_number':self.cheque_number,
                        'source_document': self.name,
                        'memo': self.communication,
                        'beneficiary': self.company_id.name,
                        'currency_id': self.currency_id.id,
                        'amount': self.amount,
                        'state': 'under_collection',
                        'check_type': 'in',
                        'partner_id': self.partner_id.id,
                        # 'check_move_id': a.id,
                        'bank_id': self.journal_id.id,
                        'payment_id': self.id,
                    }
                    check_id = check_obj.sudo().create(check_val)
                    ###########LOG#############################
                    log_obj = self.env['check.log']
                    log_obj.create({'move_description': 'Check is Under Collection ',
                            'move_id': move_id.move_id.id,
                            'move_date': datetime.today(),
                            'check_id': check_id.id,
                            })
                if self.payment_type == 'outbound':
                    move_id.sudo().write({'ref': self.name})
                    ###########CreateCheck###############
                    check_obj = self.env['check.followup']
                    check_val = {
                        'check_date': self.check_date,
                        'cheque_number':self.cheque_number,
                        'source_document': self.name,
                        'memo': self.communication,
                        'beneficiary': self.partner_id.name,
                        'currency_id': self.currency_id.id,
                        'amount': self.amount,
                        'state': 'out_standing',
                        'check_type': 'out',
                        'partner_id': self.partner_id.id,
                        # 'check_move_id': a.id,
                        'bank_id': self.journal_id.id,
                        'payment_id': self.id,
                    }
                    check_id = check_obj.sudo().create(check_val)
                    ###########LOG#############################
                    log_obj = self.env['check.log']
                    log_obj.create({'move_description': 'Out Standing Check',
                           'move_id': move_id.move_id.id,
                            'move_date': datetime.today(),
                            'check_id': check_id.id,
                            })
        # if self.check_followup == False:
        #     super(AccountPaymentInherit,self).post()

    def _prepare_payment_moves(self):
        res = super(AccountPaymentInherit, self)._prepare_payment_moves()
        name = self.communication

        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name

        if self.payment_type == 'outbound' and self.check_followup == True:
            res[0]['line_ids'][1][2]['account_id'] = self.journal_id.out_account.id
        if self.payment_type == 'inbound' and self.check_followup == True:
            res[0]['line_ids'][1][2]['account_id'] = self.journal_id.in_account.id





        # If the journal has a currency specified, the journal item need to be expressed in this currency
        # if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
        #     amount = self.currency_id._convert(amount, self.journal_id.currency_id, self.company_id, self.payment_date or fields.Date.today())
        #     debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date)._compute_amount_fields(amount, self.journal_id.currency_id, self.company_id.currency_id)
        #     vals.update({
        #         'amount_currency': amount_currency,
        #         'currency_id': self.journal_id.currency_id.id,
        #     })
        return res


