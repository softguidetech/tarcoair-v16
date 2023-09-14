from odoo import fields , models,api,tools,_
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError
# from odoo import amount_to_text


class CheckFollowup(models.Model):
    _name = 'check.followup'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Check Followups'
    _rec_name = 'cheque_number'
    _order = "cheque_number"

    def currency_default(self):
        return self.env.user.company_id.currency_id

    name_in = fields.Char(readonly=True,)
    name_out = fields.Char(readonly=True, )
    check_type = fields.Selection([('in','Customer Check'),
                                   ('out','Vendor Check')],readonly=True, track_visibility='onchange')
    state = fields.Selection([
                              ('out_standing','صادر آجل'),
                              ('under_collection','تحت التحصيل'),
                              ('deposit_check', 'تم التوريد'),
                              ('withdraw_check', 'مسحوب'),
                              ('cancel_check', 'ملغي'),
                              ('reject','راجع'),], track_visibility='onchange')
    check_date = fields.Date('تاريخ الاستحقاق',required=True, track_visibility='onchange')
    cheque_number = fields.Char('رقم الشيك',required=True, track_visibility='onchange')
    log_ids = fields.One2many('check.log','check_id')
    bank_template = fields.Many2one('res.bank',string='البنك')
    source_document = fields.Char('رقم المعاملة',readonly=True, track_visibility='onchange')
    beneficiary = fields.Char('المستفيد',readonly=True, track_visibility='onchange')
    currency_id = fields.Many2one('res.currency',default=currency_default,readonly=True, track_visibility='onchange')
    amount = fields.Monetary('المبلغ',readonly=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner',string='الشريك',readonly=True, track_visibility='onchange')
    # finance_id = fields.Many2one('finance.approval')
    check_move_id = fields.Many2one('account.move',string='Check JE')
    bank_id = fields.Many2one('account.journal', track_visibility='onchange', readonly=True)
    payment_id = fields.Many2one('account.payment',string='Payment')
    # payment_id2 = fields.Many2one('account.move', string='Payment')
    memo = fields.Char(string='البيان',readonly=True)
    check_created = fields.Date(string='تاريخ التحرير',readonly=True)

    @api.model
    def create(self, vals):
        code = 'check.followup.in.code'
        message = 'CHECK/IN' + self.env['ir.sequence'].next_by_code(code)
        vals['name_in'] = message

        code = 'check.followup.out.code'
        message = 'CHECK/OUT' + self.env['ir.sequence'].next_by_code(code)
        vals['name_out'] = message
        return super(CheckFollowup, self).create(vals)

    @api.model
    def get_amount(self):
        if self.currency_id != self.env.user.company_id.currency_id:
            return self.amount * self.currency_id.rate
        if self.currency_id == self.env.user.company_id.currency_id:
            return self.amount

    @api.model
    def get_currency(self):
        if self.currency_id != self.env.user.company_id.currency_id:
            return self.currency_id.id

    @api.model
    def amount_currency_debit(self):
        if self.currency_id != self.env.user.company_id.currency_id:
            return self.amount

    @api.model
    def amount_currency_credit(self):
        if self.currency_id != self.env.user.company_id.currency_id:
            return self.amount * -1

    def create_move(self,approval_object,date):
        move_obj = self.env['account.move']
        li = []
        self.check_date = date
        debit_val = {
            # 'move_id': self.move_id.id,
            'name': self.memo,
            'account_id': approval_object.journal_id.out_account.id,
            'debit': self.get_amount(),
            # 'analytic_account_id': approval_object.analytic_account.id or False,
            'currency_id': self.get_currency() or False,
            'amount_currency': self.amount_currency_debit() or False,
            # 'company_id': approval_object.company_id.id or False,

        }
        li.append((0, 0, debit_val))
        credit_val = {

            # 'move_id': approval_object.move_id.id,
            'name': self.memo,
            # 'account_id': approval_object.journal_id.account_id.id,
            'account_id': approval_object.journal_id.default_credit_account_id.id,
            'credit': self.get_amount(),
            'currency_id': self.get_currency() or False,
            'amount_currency': self.amount_currency_credit() or False,
            # 'analytic_account_id': ,
            # 'company_id': approval_object.company_id.id or False,

        }
        li.append((0, 0, credit_val))
        # print("List", li)
        vals = {
            'journal_id': approval_object.journal_id.id,
            'date': date,
            'ref': self.memo,
            # 'company_id': ,
            'line_ids': li,
        }
        a = move_obj.create(vals)
        a.post()
        return a

    def create_move2(self, approval_object2, date):
        move_obj = self.env['account.move']
        li = []
        self.check_date = date
        debit_val = {
            # 'move_id': self.move_id.id,
            'name': self.memo,
            'account_id': approval_object2.cash_journal_id.out_account.id,
            'debit': self.amount,
            # 'analytic_account_id': approval_object.analytic_account.id or False,
            # 'currency_id': False,
            # 'amount_currency': False,
            # 'company_id': approval_object.company_id.id or False,

        }
        li.append((0, 0, debit_val))
        credit_val = {

            # 'move_id': approval_object.move_id.id,
            'name': self.memo,
            # 'account_id': approval_object2.cash_journal_id.account_id.id,
            'account_id': approval_object2.cash_journal_id.default_credit_account_id.id,
            'credit': self.amount,
            # 'currency_id': False,
            # 'amount_currency': False,
            # 'analytic_account_id': ,
            # 'company_id': approval_object.company_id.id or False,

        }
        li.append((0, 0, credit_val))
        # print("List", li)
        vals = {
            'journal_id': approval_object2.cash_journal_id.id,
            'date': date,
            'ref': self.source_document,
            # 'company_id': ,
            'line_ids': li,
        }
        a = move_obj.create(vals)
        a.post()
        return a

    def create_move_in(self,approval_object3,date):
        move_obj = self.env['account.move']
        li = []
        self.check_date = date
        self.bank_id = approval_object3.cash_journal_id.id
        debit_val = {
            # 'move_id': self.move_id.id,
            'name': self.memo,
            'account_id': approval_object3.cash_journal_id.default_debit_account_id.id,
            'debit': self.get_amount(),
            # 'analytic_account_id': approval_object.analytic_account.id or False,
            'currency_id': self.get_currency() or False,
            'amount_currency': self.amount_currency_debit() or False,
            # 'company_id': approval_object.company_id.id or False,

        }
        li.append((0, 0, debit_val))
        credit_val = {

            # 'move_id': approval_object.move_id.id,
            'name': self.memo,
            'account_id': approval_object3.cash_journal_id.in_account.id,
            'credit': self.get_amount(),
            'currency_id': self.get_currency() or False,
            'amount_currency': self.amount_currency_credit() or False,
            # 'analytic_account_id': ,
            # 'company_id': approval_object.company_id.id or False,

        }
        li.append((0, 0, credit_val))
        # print("List", li)
        vals = {
            'journal_id': approval_object3.id,
            'date': date,
            'ref': self.memo,
            # 'company_id': ,
            'line_ids': li,
        }
        a = move_obj.create(vals)
        a.post()
        return a
#######################################################
    def create_move_in_2(self,payment,deposit_date,journal_id):
        move_obj = self.env['account.move']
        li = []
        self.check_date = deposit_date
        self.bank_id = journal_id.id
        debit_val = {
            # 'move_id': self.move_id.id,
            'name': self.memo,
            'account_id': journal_id.default_debit_account_id.id,
            'debit': self.amount,
            # 'amount':self.amount,
            # 'analytic_account_id': approval_object.analytic_account.id or False,
            'currency_id': self.get_currency() or False,
            'amount_currency': self.amount_currency_debit() or False,
            # 'company_id': approval_object.company_id.id or False,

        }
        li.append((0, 0, debit_val))
        credit_val = {

            # 'move_id': approval_object.move_id.id,
            'name': self.memo,
            # 'amount': self.amount,
            'account_id': payment.journal_id.in_account.id,
            'credit': self.amount,
            'currency_id': self.get_currency() or False,
            'amount_currency': self.amount_currency_credit() or False,
            # 'analytic_account_id': ,
            # 'company_id': approval_object.company_id.id or False,

        }
        li.append((0, 0, credit_val))
        # print("List", li)
        vals = {
            'journal_id': journal_id.id,
            'date': deposit_date,
            'ref': self.memo,
            # 'company_id': ,
            'line_ids': li,
        }
        a = move_obj.create(vals)
        a.post()
        return a

    def copy(self):
        raise ValidationError("Can Not Duplicate Check !!")

    def cancel_check(self):
        if self.bank_id:
            rec = super(CheckFollowup, self).cancel_check()
            if self.bank_id:
                self.move_id.button_cancel()
                self.move_id.unlink()
                search_with = self.env['check.log'].search([('cheque_id', '=', self.cheque_id.id),
                                                            ('move_description', '=', 'Withdraw Check')])
                search_with.move_id.button_cancel()
                # self.move_id.unlink()
                search_with.move_id.unlink()
                self.check_id.cancel_check()
                channel_group_obj = self.env['mail.message']
                dic = {
                    'subject': 'Payment Canceled',
                    'email_from': self.env.user.name,
                    # 'model': self.name,
                    'body': 'Payment Number ' + self.name + ' Is Canceled ',
                    # 'partner_ids': [(4, self.env.ref('finance_approval.group_finance_approval_fm').id)],
                    'channel_ids': [(4, self.env.ref('mail.channel_all_employees').id)],
                }
                channel_group_obj.create(dic)
                self.state = 'cancel_check'
                return rec

    def withdraw_check(self,date):
        payment_search = self.env['account.payment'].search([('name','=', self.source_document),
                                                             ('cheque_number','=',self.cheque_number)
                                                             ])
        payment_search2 = self.env['check.voucher'].search([('name', '=', self.source_document),
                                                             ('cheque_number', '=', self.cheque_number)
                                                             ])
        payment_search3 = self.env['custody.request'].search([('name', '=', self.source_document),
                                                            ('cheque_number', '=', self.cheque_number)
                                                            ])
        if payment_search:
            create_move = self.create_move(payment_search2,date)
            log_obj = self.env['check.log']
            log_obj.create({'move_description': 'شيك مسحوب من'+ str(payment_search.journal_id.name),
                            'move_id': create_move.id,
                            'move_date': datetime.today(),
                            'check_id': self.id,
                            })
            self.state = 'withdraw_check'

            channel_group_obj = self.env['mail.message']
            dic = {
                'subject': 'شيك مسحوب',
                'email_from': self.env.user.name,
                # 'model': self.name,
                'body': 'شيك رقم ' + self.cheque_number + ' مسحوب',
                # 'partner_ids': [(4, self.env.ref('finance_approval.group_finance_approval_fm').id)],
                'channel_ids': [(4, self.env.ref('mail.channel_all_employees').id)],
            }
            channel_group_obj.create(dic)
        if payment_search2:
            create_move = self.create_move2(payment_search2, date)
            log_obj = self.env['check.log']
            log_obj.create({'move_description': 'شيك مسحوب من' + '  ' + str(payment_search2.cash_journal_id.name),
                            'move_id': create_move.id,
                            'move_date': datetime.today(),
                            'check_id': self.id,
                            })
            self.state = 'withdraw_check'

            channel_group_obj = self.env['mail.message']
            dic = {
                'subject': 'Payment Withdraw Check',
                'email_from': self.env.user.name,
                # 'model': self.name,
                'body': 'Payment Check Number ' + self.cheque_number + ' Withdraw',
                # 'partner_ids': [(4, self.env.ref('finance_approval.group_finance_approval_fm').id)],
                'channel_ids': [(4, self.env.ref('mail.channel_all_employees').id)],
            }
            channel_group_obj.create(dic)
        if payment_search3:
            create_move = self.create_move(payment_search3,date)
            log_obj = self.env['check.log']
            log_obj.create({'move_description': 'شيك مسحوب من'+ str(payment_search.journal_id.name),
                            'move_id': create_move.id,
                            'move_date': datetime.today(),
                            'check_id': self.id,
                            })
            self.state = 'withdraw_check'

            channel_group_obj = self.env['mail.message']
            dic = {
                'subject': 'شيك مسحوب',
                'email_from': self.env.user.name,
                # 'model': self.name,
                'body': 'شيك رقم ' + self.cheque_number + ' مسحوب',
                # 'partner_ids': [(4, self.env.ref('finance_approval.group_finance_approval_fm').id)],
                'channel_ids': [(4, self.env.ref('mail.channel_all_employees').id)],
            }
            channel_group_obj.create(dic)
    def check_reject(self):

        if self.payment_id and self.check_type == 'in' and self.state == 'under_collection':
            move_obj = self.env['account.move']
            li = []
            credit_val = {
                # 'move_id': self.move_id.id,
                'name': str('reverse: ')+str(self.payment_id.name),
                'account_id': self.payment_id.journal_id.in_account.id,
                'credit': self.payment_id.get_amount(),
                'partner_id': self.payment_id.partner_id.id,
                # 'analytic_account_id': approval_object.analytic_account.id or False,
                'currency_id': self.payment_id.get_currency() or False,
                'amount_currency': self.payment_id.amount_currency_credit() or False,
                # 'company_id': approval_object.company_id.id or False,

            }

            li.append((0, 0, credit_val))
            debit_val = {

                # 'move_id': approval_object.move_id.id,
                'name': str('reverse: ')+str(self.payment_id.name),
                'account_id': self.payment_id.partner_id.property_account_receivable_id.id,
                'debit': self.payment_id.get_amount(),
                'partner_id': self.payment_id.partner_id.id,
                'currency_id': self.payment_id.get_currency() or False,
                'amount_currency': self.payment_id.amount_currency_debit() or False,
                # 'analytic_account_id': ,
                # 'company_id': approval_object.company_id.id or False,

            }
            li.append((0, 0, debit_val))
            print("List", li)
            vals = {
                'journal_id': self.payment_id.journal_id.id,
                'date': datetime.today(),
                'ref': str('شيك راجع:')+str(self.payment_id.cheque_number),
                # 'company_id': ,
                'line_ids': li,
            }
            a = move_obj.sudo().create(vals)
            a.post()
            vals = {
                'move_description': 'شيك راجع',
                'check_id': self.id,
                'move_date': datetime.today(),
                'move_id': a.id,

            }
            check_log = self.env['check.log']
            check_log.create(vals)
            self.state = 'reject'

        if self.payment_id and self.check_type == 'out' and self.state == 'out_standing':
            move_obj = self.env['account.move']
            li = []
            credit_val = {
                # 'move_id': self.move_id.id,
                'name': str('reverse: ')+str(self.payment_id.name),
                'account_id': self.payment_id.partner_id.property_account_payable_id.id,
                'credit': self.payment_id.get_amount(),
                'partner_id': self.payment_id.partner_id.id,
                # 'analytic_account_id': approval_object.analytic_account.id or False,
                'currency_id': self.payment_id.get_currency() or False,
                'amount_currency': self.payment_id.amount_currency_credit() or False,
                # 'company_id': approval_object.company_id.id or False,

            }
            li.append((0, 0, credit_val))
            debit_val = {

                # 'move_id': approval_object.move_id.id,
                'name': str('reverse: ')+str(self.payment_id.name),
                'account_id': self.payment_id.journal_id.out_account.id,
                'debit': self.payment_id.get_amount(),
                'partner_id': self.payment_id.partner_id.id,
                'currency_id': self.payment_id.get_currency() or False,
                'amount_currency': self.payment_id.amount_currency_debit() or False,
                # 'analytic_account_id': ,
                # 'company_id': approval_object.company_id.id or False,

            }
            li.append((0, 0, debit_val))
            print("List", li)
            vals = {
                'journal_id': self.payment_id.journal_id.id,
                'date': datetime.today(),
                'ref': str('Reverse Check: ')+str(self.payment_id.cheque_number),
                # 'company_id': ,
                'line_ids': li,
            }
            a = move_obj.create(vals)
            a.post()
            vals = {
                'move_description': 'شيك راجع',
                'check_id': self.id,
                'move_date': datetime.today(),
                'move_id': a.id,

            }
            check_log = self.env['check.log']
            check_log.sudo().create(vals)
            self.state = 'reject'
            ##########
        if not self.payment_id and self.check_type == 'in' and self.state == 'under_collection':
            voucher_obj = self.env['check.inbound'].search([('name', '=', self.source_document),
                                                                ('cheque_number', '=', self.cheque_number)
                                                                ])
            move_obj = self.env['account.move']
            li = []
            credit_val = {
                # 'move_id': self.move_id.id,
                'name': str('شيك راجع:') + str(voucher_obj.cheque_number) + str(voucher_obj.name),
                'account_id': voucher_obj.account_id.id,
                'credit': self.amount,
                'partner_id': voucher_obj.custody_line_ids.partner_id.id,
                # 'analytic_account_id': approval_object.analytic_account.id or False,
                'currency_id': voucher_obj.get_currency() or False,
                'amount_currency': voucher_obj.amount_currency_credit_equal() or False,
                # 'company_id': approval_object.company_id.id or False,

            }

            li.append((0, 0, credit_val))
            debit_val = {

                # 'move_id': approval_object.move_id.id,
                'name': str('شيك راجع:') + str(voucher_obj.cheque_number) + str(voucher_obj.name),
                'account_id': voucher_obj.custody_line_ids.partner_id.property_account_receivable_id.id,
                'debit': voucher_obj.amount,
                'partner_id': voucher_obj.custody_line_ids.partner_id.id,
                'currency_id': voucher_obj.get_currency() or False,
                'amount_currency': voucher_obj.amount_currency_debit() or False,
                # 'analytic_account_id': ,
                # 'company_id': approval_object.company_id.id or False,

            }
            li.append((0, 0, debit_val))
            print("List", li)
            vals = {
                'journal_id': voucher_obj.cash_journal_id.id,
                'date': datetime.today(),
                'ref': str('شيك راجع:') + str(voucher_obj.cheque_number),
                # 'company_id': ,
                'line_ids': li,
            }
            a = move_obj.sudo().create(vals)
            a.post()
            vals = {
                'move_description': 'شيك راجع',
                'check_id': self.id,
                'move_date': datetime.today(),
                'move_id': a.id,

            }
            check_log = self.env['check.log']
            check_log.create(vals)
            self.state = 'reject'
########################################
        if not self.payment_id and self.check_type == 'out' and self.state == 'out_standing':
            voucher_obj = self.env['check.voucher'].search([('name', '=', self.source_document),
                                                                ('cheque_number', '=', self.cheque_number)
                                                                ])
            move_obj = self.env['account.move']
            li = []
            credit_val = {
                # 'move_id': self.move_id.id,
                'name': str('شيك راجع:') + str(voucher_obj.cheque_number) + str(voucher_obj.name),
                'account_id':voucher_obj.custody_line_ids.partner_id.property_account_payable_id.id,
                'credit': self.amount,
                'partner_id': voucher_obj.custody_line_ids.partner_id.id,
                # 'analytic_account_id': approval_object.analytic_account.id or False,
                'currency_id': voucher_obj.get_currency() or False,
                'amount_currency': voucher_obj.amount_currency_credit_equal() or False,
                # 'company_id': approval_object.company_id.id or False,

            }

            li.append((0, 0, credit_val))
            debit_val = {

                # 'move_id': approval_object.move_id.id,
                'name': str('شيك راجع:') + str(voucher_obj.cheque_number) + str(voucher_obj.name),
                'account_id': voucher_obj.account_id.id,
                'debit': voucher_obj.amount,
                'partner_id': voucher_obj.custody_line_ids.partner_id.id,
                'currency_id': voucher_obj.get_currency() or False,
                'amount_currency': voucher_obj.amount_currency_debit() or False,
                # 'analytic_account_id': ,
                # 'company_id': approval_object.company_id.id or False,

            }
            li.append((0, 0, debit_val))
            print("List", li)
            vals = {
                'journal_id': voucher_obj.cash_journal_id.id,
                'date': datetime.today(),
                'ref': str('شيك راجع:') + str(voucher_obj.cheque_number),
                # 'company_id': ,
                'line_ids': li,
            }
            a = move_obj.sudo().create(vals)
            a.post()
            vals = {
                'move_description': 'شيك راجع',
                'check_id': self.id,
                'move_date': datetime.today(),
                'move_id': a.id,

            }
            check_log = self.env['check.log']
            check_log.create(vals)
            self.state = 'reject'

    def change_bank(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Change Bank Wizard',
            'res_model': 'change.bank',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    def change_date(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Change Date Wizard',
            'res_model': 'change.bank',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    def deposit_in_bank(self,deposit_date,journal_id):

        payment_search = self.env['account.payment'].search([('name', '=', self.source_document),
                                                             ])
        voucher_obj = self.env['check.inbound'].search([('name', '=', self.source_document),
                                                        ('cheque_number', '=', self.cheque_number)
                                                        ])
        if payment_search:
            create_move = self.create_move_in_2(payment_search, deposit_date,journal_id)
            log_obj = self.env['check.log']
            log_obj.create({'move_description': 'شيك وارد في' + str(payment_search.journal_id.name),
                            'move_id': create_move.id,
                            'move_date': datetime.today(),
                            'check_id': self.id,
                            })
            self.state = 'deposit_check'
            channel_group_obj = self.env['mail.message']
            dic = {
                'subject': 'Payment Check Reject',
                'email_from': self.env.user.name,
                # 'model': self.name,
                'body': 'Approval Check Number ' + self.cheque_number + ' توريد الشيك ',
                # 'partner_ids': [(4, self.env.ref('finance_approval.group_finance_approval_fm').id)],
                'channel_ids': [(4, self.env.ref('mail.channel_all_employees').id)],
            }
            channel_group_obj.create(dic)
        if voucher_obj:
            create_move = self.create_move_in(voucher_obj, deposit_date)
            log_obj = self.env['check.log']
            log_obj.create({'move_description': 'شيك وارد من' + '  ' + str(voucher_obj.cash_journal_id.name),
                            'move_id': create_move.id,
                            'move_date': datetime.today(),
                            'check_id': self.id,
                            })
            self.state = 'deposit_check'

            channel_group_obj = self.env['mail.message']
            dic = {
                'subject': 'Payment Withdraw Check',
                'email_from': self.env.user.name,
                # 'model': self.name,
                'body': 'Payment Check Number ' + self.cheque_number + ' Deposit',
                # 'partner_ids': [(4, self.env.ref('finance_approval.group_finance_approval_fm').id)],
                'channel_ids': [(4, self.env.ref('mail.channel_all_employees').id)],
            }
            channel_group_obj.create(dic)
        # if voucher_obj:
        #     create_move = self.create_move_in_2(voucher_obj,journal_id,date)
        #     log_obj = self.env['check.log']
        #     log_obj.create({'move_description': 'شيك وارد في'+ str(journal_id.name),
        #                     'move_id': create_move.id,
        #                     'move_date': datetime.today(),
        #                     'check_id': self.id,
        #                     })
        #     self.state = 'deposit_check'
        #     channel_group_obj = self.env['mail.message']
        #     dic = {
        #         'subject': 'توريد شيك',
        #         'email_from': self.env.user.name,
        #         # 'model': self.name,
        #         'body': 'Approval Check Number ' + self.cheque_number + ' توريد الشيك ',
        #         # 'partner_ids': [(4, self.env.ref('finance_approval.group_finance_approval_fm').id)],
        #         'channel_ids': [(4, self.env.ref('mail.channel_all_employees').id)],
        #     }
        #     channel_group_obj.create(dic)


class CheckLog(models.Model):
    _name = 'check.log'
    _description = 'Check Logs'

    move_id = fields.Many2one('account.move','قيد اليومية')
    move_description = fields.Char('البيان',)
    check_id = fields.Many2one('check.followup',string='مرجع الشيك')
    move_date = fields.Date('تاريخ قيد اليومية')
    # finance_id = fields.Many2one('finance.approval',string='Finance Reference')


class JournalObject(models.Model):
    _inherit = 'account.journal'

    out_account = fields.Many2one('account.account', string= 'حساب شيكات صادرة')
    in_account = fields.Many2one('account.account', string= 'حساب شيكات تحت التحصيل')



