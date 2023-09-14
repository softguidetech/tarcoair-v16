from odoo import fields , models,api,tools,_
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError
from num2words import num2words



class CheckVoucher(models.Model):
    _name = 'check.voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Check Vouchers'

    # def default_employee(self):
    #     return self.env.user.name

    @api.onchange('cash_journal_id')
    def _onchange_journal(self):
        if self.cash_journal_id:
            # self.account_id = self.cash_journal_id.account_id.id
            self.account_id = self.cash_journal_id.default_account_id.id
            # self.account_id = self.cash_journal_id.default_credit_account_id.id

    @api.depends('amount', 'currency_id')
    def _onchange_amount(self):
        from ..models.money_to_text_ar import amount_to_text_arabic
        if self.amount:
            self.num2wo = amount_to_text_arabic(
                self.amount, self.currency_id.name)


    def default_currency(self):
        return self.env.user.company_id.currency_id
    def invoice_tree_view(self):
        tree_view = {
            'name': _('Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'main',
            'domain': [('id', '=', self.x_bill_no.id)],
        }
        return tree_view

    def compute_permits(self):
        payment_count = self.env['account.move'].sudo().search_count([('id', '=', self.x_bill_no.id)])
        self.x_doc_count = payment_count
    @api.onchange('x_bill_no')
    def get_bill(self):
        c = self.env["account.move"].search([('name', '=', self.x_bill_no.name)])
        if c.name:
            self.amount = float(c.amount_total)
            self.check_date = c.date
            self.person=c.partner_id.name
            self.currency_id = c.currency_id.id
        for i in self.x_bill_no:
            sale_order_line = self.env['check.voucher.line'].create({
                'account_id': i.partner_id.property_account_payable_id.id,
                'partner_id': i.partner_id.id,
                'cash_request_id': self.id,
                'name': 'سداد فاتورة',
                'amount': float(i.amount_total)
            })

    def default_company(self):
        return self.env.user.company_id

    def default_user_analytic(self):
        return self.env.user

    @api.returns('self')
    def _default_employee_get(self):
        return self.env.user

    # def manager_default(self):
    #     return self.env.user.manager_id

    name = fields.Char('Reference',readonly=True,default='New')
    x_bill_no = fields.Many2one('account.move', string='Bill No', domain = "[('move_type','=','in_invoice')]")

    user_name = fields.Many2one('res.users', string='User Name',readonly=True, default=_default_employee_get)
    # manager_id = fields.Many2one('res.users','Manager',default=manager_default)
    request_date = fields.Date('تاريخ التحرير', readonly=True, required=True, default=fields.Date.today())
    currency_id = fields.Many2one('res.currency', string='Currency',default=default_currency,required=True)
    amount = fields.Monetary('المبلغ',required=True, track_visibility='onchange')
    sequence = fields.Integer(required=True, default=1,)
    state = fields.Selection([('draft', 'مسودة'),
                              ('manager', 'اعتماد المدير'),
                              ('audit', 'اعتماد المراجعة'),
                              ('done', 'اعتماد الخزينة'),
                              ('post', 'مرحل'),

                              ('cancel', 'ملغي')], default='draft', track_visibility='onchange')
    num2wo = fields.Char(readonly=True, string="المبلغ كتابة",compute='_onchange_amount',store=True)
    check_journal_id = fields.Many2one('account.journal', readonly=True, string='دفتر اليومية',
                                       default=lambda self: self.env['account.journal'].search(
                                           [('name', '=', 'سند صرف شيك')]))
    person = fields.Char(string= 'المستفيد', track_visibility='onchange')
    company_id = fields.Many2one('res.company',string="الشركة",default=default_company)
    check_date = fields.Date(string='تاريخ الاستحقاق', copy=False, default=fields.Date.today())
    cheque_number = fields.Char(string='رقم الشيك', copy=False)
    check_count = fields.Integer(compute='_compute_check')
    # Accounting Fields
    total_amount_ex = fields.Float('الاجمالي',readonly=True)
    move_id = fields.Many2one('account.move',string='قيد المصروف',readonly=True)
    description = fields.Char(string='الوصف')
    cash_journal_id = fields.Many2one('account.journal',string='البنك',domain="[('type','in',['bank'])]")
    #employee_name = fields.Many2one('res.partner', string="Employee Name",domain="[('is_employee','=',True)]")
    # account_id = fields.Many2one(related='cash_journal_id.default_debit_account_id', string='الحساب', readonly=1)
    account_id = fields.Many2one(related='cash_journal_id.default_account_id', string='الحساب', readonly=1)

    total_with_ex = fields.Float('الاجمالي الفرعي',compute='_total_with_ex')
    total = fields.Float('اجمالي المصروفات',compute='_total_expense')
    x_doc_count = fields.Integer(compute='compute_permits',
                               string="Bills")
    count_je = fields.Integer(compute='_count_je_compute')
    count_diff = fields.Integer(compute='_count_diff_compute')



    def action_check_view(self):
        if self.check_date:
            tree_view_out = self.env.ref('check_followup.view_tree_check_followup_out')
            form_view_out = self.env.ref('check_followup.view_form_check_followup_out')
            return {
                'type': 'ir.actions.act_window',
                'name': 'View Vendor Checks',
                'res_model': 'check.followup',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view_out.id, 'tree'), (form_view_out.id, 'form')],
                'domain': [('source_document', '=', self.name)],

            }
    def _compute_check(self):
        payment_count = self.env['check.followup'].sudo().search_count([('source_document','=',self.name)])
        self.check_count = payment_count

    def _count_je_compute(self):
        for i in self:
            if i.move_id:
                i.count_je = 1
            else:
                i.count_je = 0

    def _count_diff_compute(self):
        for i in self:
            if i.move_id2:
                i.count_diff = 1
            else:
                i.count_diff = 0

    def action_move(self):
        tree_view = self.env.ref('account.view_move_tree')
        form_view = self.env.ref('account.view_move_form')
        return {
                'type': 'ir.actions.act_window',
                'name': 'View Journal',
                'res_model': 'account.move',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
                'domain': [('id', '=', self.move_id.id)],

        }



    # @api.one
    @api.depends('custody_line_ids')
    def _total_with_ex(self):
        total_without = 0
        for i in self.custody_line_ids:
            total_without += i.amount
        self.total_with_ex = total_without

    @api.depends('custody_line_ids')
    def _compute_tax(self):
        total =0
        for i in self.custody_line_ids:
            total += i.tax_amount
        self.total_tax = total

    @api.depends('custody_line_ids')
    def _total_expense(self):
        total_tax = 0
        total_am = 0
        for i in self.custody_line_ids:
            total_tax +=i.tax_amount
            total_am +=i.amount
        self.total = total_tax + total_am

    @api.depends('user_name')
    def _compute_account(self):
        # setting_ob = self.env['res.config.settings'].search([], order='id desc', limit=1)
        #
        # if not setting_ob.petty_account_id:
        #     raise ValidationError('Please Insert Petty cash account In Setting')
        # if setting_ob.petty_account_id:
        #     self.account_id = setting_ob.petty_account_id
        if not self.company_id.petty_account_id:
            raise ValidationError('Please Insert Petty cash account In Company Configuration')
        else:
            self.account_id = self.company_id.petty_account_id

    user_id = fields.Many2one('res.users', default=default_user_analytic)
    # analytic_account = fields.Many2one(related='user_id.analytic_account_id', string='Analytic Account')

    # analytic_account = fields.Many2one('account.analytic.account',string='Analytic Account')
    # check_term = fields.Selection([('not_followup','Not Follow-up'),
    #                                ('followup','Follow-up')
    #                                ],
    #                               default='not_followup',invisible=True)
    # voucher_type = fields.Selection([('cash_vs', 'Cash'),
    #                                ('check_vs', 'Check')
    #                                ],
    #                               default='cash_vs', invisible=True)

    # clrarance Line Many2one
    custody_line_ids = fields.One2many('check.voucher.line','cash_request_id',string='Expenses Line')
    # Check Details
    # check_date = fields.Date('Check Date',)
    # check_number = fields.Char('Check Number')
    # bank_template = fields.Many2one('res.bank')
    # check_id = fields.Many2one('check.followup',string="Check Reference",readonly=True)
    #
    # move_id2 = fields.Many2one('account.move',string='Difference Move',readonly=True)

    # def confirm_dm(self):
    #     # total_ex = 0
    #     # remmaing = 0
    #     # for i in self.custody_line_ids:
    #     #     total_ex +=i.amount
    #     #if self.amount < self.total and self.total_history_amount > self.amount:
    #        # raise ValidationError('Please make sure (total expense amount) must be less than reconcile balance')
    #
    #    # if self.amount > self.total and self.total_history_amount < self.amount:
    #      #   raise ValidationError('Please make sure (total expense amount) must be equal reconcile balance')
    #
    #    # if self.amount > self.total_history_amount:
    #     #    raise ValidationError('Sorry you have not enough balance in petty cash to reconcile , Request new petty cash')
    #     # best onetax_amount
    #
    #     if self.amount <= 0:
    #         raise ValidationError("Please Make Sure Amount Field Grater Than Zero !!")
    #    # if self.total_history_amount <= 0:
    #     #    raise ValidationError("You can not reconcile Because (negative) petty cash balance")
    #     if not self.custody_line_ids:
    #         raise ValidationError("Please Insert at Least One Line Expense")
    #     if self.env.user.name != self.user_id.name:
    #         raise ValidationError("Please This Request is not For You")
    #     if not self.custody_line_ids:
    #         raise ValidationError("Please Insert Columns in ")
    #     else:
    #
    #         self.write({'state': 'dm'})
    #
    #
    # def confirm_am(self):
    #
    #     self.write({'state': 'am'})
    #
    #
    # def confirm_fm(self):
    #     # if self.check_term == 'followup' and self.journal_type != 'bank':
    #     #     raise ValidationError("Please Don't Filling Check Information")
    #     # else:
    #     for i in self.custody_line_ids:
    #         if not i.account_id:
    #             raise ValidationError('Please insert expense accounts !!')
    #     self.write({'state': 'fm'})
    #     if not self.journal_id or not self.account_id or not self.custody_journal_id:
    #         raise ValidationError("Please Fill Accounting information (Journal-Employee-Account)")
    #     if self.check_term == 'followup':
    #         if not self.check_number or not self.check_date or not self.bank_template:
    #             raise ValidationError("Please Fill Check Details !!")
    @api.model
    def get_amount(self):
        for i in self.custody_line_ids:
            if self.amount:
                if i.currency_id != self.env.user.company_id.currency_id:
                    return i.amount * self.env.user.company_id.currency_id.rate
                if i.currency_id == self.env.user.company_id.currency_id:
                    return i.amount

            # if self.amount < self.total_amount_ex:
            #     if i.currency_id != self.env.user.company_id.currency_id:
            #         return i.amount / i.currency_id.rate
            #     if i.currency_id == self.env.user.company_id.currency_id:
            #         return i.amount
            #
            # if self.amount == self.total_amount_ex:
            #     if i.currency_id != self.env.user.company_id.currency_id:
            #         return i.amount / i.currency_id.rate
            #     if i.currency_id == self.env.user.company_id.currency_id:
            #         return i.amount

    @api.model
    def get_amount_general(self):
        for i in self.custody_line_ids:
            if self.amount > self.total_amount_ex:
                if i.currency_id != self.env.user.company_id.currency_id:
                    return i.amount * i.currency_id.rate
                if i.currency_id == self.env.user.company_id.currency_id:
                    return i.amount

            # if self.amount < self.total_amount_ex:
            #     if i.currency_id != self.env.user.company_id.currency_id:
            #         return i.amount / i.currency_id.rate
            #     if i.currency_id == self.env.user.company_id.currency_id:
            #         return i.amount
            #
            if self.amount == self.total_amount_ex:
                if i.currency_id != self.env.user.company_id.currency_id:
                    return i.amount * i.currency_id.rate
                if i.currency_id == self.env.user.company_id.currency_id:
                    return i.amount


    @api.model
    def get_currency(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return i.currency_id.id

    @api.model
    def amount_currency_debit(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return i.amount


    @api.model
    def amount_currency_credit(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return i.amount * -1
    @api.model
    def amount_currency_credit_equal(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return self.amount * -1

    @api.model
    def get_total_credit_amount_ex(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return self.total_amount_ex * -1



    def confirm_post(self):
        account_move_object = self.env['account.move']

        if not self.cash_journal_id and not self.account_id:
            raise ValidationError(_('يرجي ادخال يومية السداد و الحساب'))
        if self.amount != self.total:
            raise ValidationError(_('اجمالي المبلغ لا يساوي اجمالي المصروف'))
        if self.amount == self.total:

            l = []
            curr_amount = 0
            amount = 0
            credit_name =  'شيك رقم' + '  '+str(self.cheque_number)
            list = []
            currency_id = False
            check_obj = self.env['check.followup']
            for i in self.custody_line_ids:
                description = i.name

                conc = str(i.name or '') + '/' + ' '
                list.append(conc)
                desc = ', '.join(list)
                self.description = desc
                partner_name = i.partner_id.id



                if i.currency_id != self.env.user.company_id.currency_id:
                    amount = self.amount * self.env.user.company_id.currency_id.rate
                    curr_amount = self.amount
                    currency_id = i.currency_id.id

                if i.currency_id == self.env.user.company_id.currency_id:
                    amount = i.amount
                    currency_id = False
                    curr_amount = 0
                debit_val = {
                'move_id': self.move_id.id,
                'name': description,
                'account_id': i.account_id.id,
                'debit': amount,
                # 'analytic_account_id': i.analytic_accont_id.id or False,
                'currency_id': currency_id,
                'partner_id': partner_name if self.custody_line_ids.partner_id else False,
                'amount_currency': curr_amount or False,
                # 'company_id': self.company_id.id or False,

            }
                l.append((0, 0, debit_val))
            credit_val = {

                        'move_id': self.move_id.id,
                        'name': credit_name,
                        'account_id': self.account_id.id,
                        'credit': self.amount,
                        'currency_id': currency_id,
                        'partner_id': self.user_name.partner_id.id,
                        'amount_currency': curr_amount * -1 or False,
                        # # 'analytic_account_id': ,
                        # 'company_id': self.company_id.id or False,

                    }
            l.append((0, 0, credit_val))



            check_val = {
                'check_created': self.request_date,
                'check_date': self.check_date,
                'cheque_number': self.cheque_number,
                'source_document': self.name,
                'beneficiary': self.person,
                'currency_id': currency_id,
                'amount': amount,
                'state': 'out_standing',
                'check_type': 'out',
                # 'partner_id': partner_name or False,
                # 'check_move_id': a.id,
                'bank_id': self.cash_journal_id.id,
                'memo': credit_name,

            }

            vals = {
                'journal_id': self.cash_journal_id.id,
                'date': self.request_date,
                'ref': self.name,
                # 'company_id': ,
                'line_ids': l,
            }
            self.move_id = account_move_object.create(vals)
            self.move_id.post()


            check_id = check_obj.sudo().create(check_val)
            ###########LOG#############################
            log_obj = self.env['check.log']
            log_obj.create({'move_description': 'شيك صادر ',
                            'move_id': self.move_id.id,
                            'move_date': self.request_date,
                            'check_id': check_id.id,
                            })

            self.state = 'post'



    def total_credit(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return self.total * self.currency_id.rate
            else:
                return self.total

    def total_debit(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return i.amount

    def amount_debit(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return i.amount * i.currency_id.rate
            else:
                return i.amount

    def amount_currency_debit_difference(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return self.amount - self.total

    def amount_currency_credit_diffrence(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                diff = self.amount - self.total
                return diff * -1

    def amount_currency_total(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return self.total * -1

    @api.model
    def create(self, vals):
        code = 'check.voucher.code'

        if vals.get('name', 'New') == 'New':
            message = 'سند صرف شيك' + self.env['ir.sequence'].next_by_code(code)
            vals['name'] = message
            # self.message_post(subject='Create CCR', body='This is New CCR Number' + str(message))
        return super(CheckVoucher, self).create(vals)

    # @api.multi
    def unlink(self):
        for i in self:
            if i.state != 'draft':
                raise ValidationError("Please Make Sure State in DRAFT !!")
            else:
                super(CheckVoucher, i).unlink()

    def copy(self):
        raise ValidationError("Can not Duplicate a Record !!")

    def cancel_request(self):

        if self.journal_id.update_posted == False:
            raise ValidationError("Please Check Allow Cancel Journal Entry In Journal First !!")

        else:
            # Cancel JE and Delete it
            self.move_id.button_cancel()
            self.move_id.unlink()
            self.state = 'cancel'

    def reject(self):
        self.state = 'draft'

    def confirm_manager(self):
        list = []
        for i in self.custody_line_ids:
            description = i.name
            conc = str(i.name or '') + '/' + ' '
            list.append(conc)
            desc = ', '.join(list)
            self.description = desc
            partner_name = i.partner_id.id
        self.state = 'manager'
    def confirm_audit(self):
        list = []
        for i in self.custody_line_ids:
            description = i.name
            conc = str(i.name or '') + '/' + ' '
            list.append(conc)
            desc = ', '.join(list)
            self.description = desc
            partner_name = i.partner_id.id
        self.state = 'done'


    def confirm_cashier(self):
        list = []
        for i in self.custody_line_ids:
            description = i.name
            conc = str(i.name or '') + '/' + ' '
            list.append(conc)
            desc = ', '.join(list)
            self.description = desc
            partner_name = i.partner_id.id
            if self.amount != self.total:
                raise ValidationError(_('اجمالي المبلغ لا يساوي اجمالي فئات العملة'))
            if self.amount == self.total:
                self.state = 'audit'

class CheckVoucherLine(models.Model):
    _name = 'check.voucher.line'



    def _default_user(self):

        return self.env.user.id

    name = fields.Char('البيان',required=True)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel5', 'doc_id', 'attach_id6', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    analytic_accont_id = fields.Many2one('account.analytic.account',string='Analytic Account', track_visibility='onchange')
    amount = fields.Float('المبلغ',required=True)
    cash_request_id = fields.Many2one('check.voucher',string='سند الصرف')
    account_id = fields.Many2one('account.account',string='الحساب')
    #############

    partner_id = fields.Many2one('res.partner', string='الشريك')
    currency_id = fields.Many2one('res.currency','العملة',compute='_compute_currency')
    company_id = fields.Many2one('res.company','الشركة',compute='_compute_company')
    user_id = fields.Many2one('res.users','المستخدم',compute='_compute_user')
    date_clear = fields.Date(string='Clear Date',compute='_compute_date')
    # analytic_id = fields.Many2one('account.analytic.account',compute='_compute_analytic')
    #############
    state = fields.Selection(string="الحالة", related='cash_request_id.state')
    user_name = fields.Many2one(string="المستخدم", related='cash_request_id.user_name')
    # user_id = fields.Many2one('res.users',default=_default_user)
    tax_amount = fields.Float('الضريبة')


    @api.depends('cash_request_id.currency_id')
    def _compute_currency(self):
        self.currency_id = self.cash_request_id.currency_id
    ######################3
    @api.onchange('partner_id')
    def _get_partner(self):
        partner_account = self.env['account.account'].search([('name', '=', 'الدائنون')])
        if self.partner_id:
            self.account_id = partner_account

    @api.depends('cash_request_id.company_id')
    def _compute_company(self):
        self.company_id = self.cash_request_id.company_id

    @api.depends('cash_request_id.user_name')
    def _compute_user(self):
        self.user_id = self.cash_request_id.user_name

    @api.depends('cash_request_id.request_date')
    def _compute_date(self):
        self.date_clear = self.cash_request_id.request_date

    # @api.onchange('tax_id')
    # def _tax_amount_compute(self):
    #     if self.tax_id and self.amount:
    #         if self.tax_id.amount_type == 'percent':
    #             self.tax_amount = (self.amount * self.tax_id.amount) / 100
    #         if self.tax_id.amount_type == 'fixed':
    #             self.tax_amount = self.tax_id.amount


# class ClearRequestInherit(models.Model):
#     _inherit = 'custody.request'
#
#     clear_ids = fields.One2many('custody.clear.request','request_id',string='Reconcile Request')
#     clear_num = fields.Integer(compute="_compute_clear_num")
#
#     def _compute_clear_num(self):
#         search_clear_ids = self.env['custody.clear.request'].search_count([('request_id','=',self.id)])
#         self.clear_num = search_clear_ids
#
#     def action_reconcile_request(self):
#         search_clear_ids = self.env['custody.clear.request'].search([('request_id','=',self.id)])
#         lis = []
#         for i in search_clear_ids:
#             lis.append(i.id)
#         tree_view = self.env.ref('custody_clear_request.custody_clear_request_tree')
#         form_view = self.env.ref('custody_clear_request.custody_clear_request_form')
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'View Reconcile Request',
#             'res_model': 'custody.clear.request',
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
#             'domain': [('id', 'in', lis)],
#
#         }
