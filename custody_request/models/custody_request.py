from odoo import fields , models,api,tools,_
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError
# from odoo import amount_to_text


class FinanceApprovalRequest(models.Model):
    _name = 'custody.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Petty Cash Request'

    # def default_employee(self):
    #     return self.env.user.name
    custody_clear_id = fields.Many2one('custody.clear.request',string='Reconcile')

    def default_currency(self):
        return self.env.user.company_id.currency_id

    @api.depends('amount','currency_id')
    def _onchange_amount(self):
        from ..models.money_to_text_ar import amount_to_text_arabic
        if self.amount:
            self.num2wo = amount_to_text_arabic(
                self.amount, self.env.user.company_id.currency_id.name)

    def default_company(self):
        return self.env.user.company_id

    def default_user_analytic(self):
        return self.env.user

    @api.returns('self')
    def _default_employee_get(self):
        return self.env.user

    # def manager_default(self):
    #     return self.env.user.manager_id

    @api.depends('amount', 'currency_id')
    def _onchange_amount(self):

        self.num2wo = self.currency_id.amount_to_text(self.amount) if self.currency_id else ''

    name = fields.Char('Reference',readonly=True,default='New')
    description = fields.Char(compute='get_desc', string='Description')
    user_name = fields.Many2one('res.users', string='User name',readonly=True, default=_default_employee_get)
    check_date = fields.Date('Cheque Date', )
    num2wo = fields.Char(string="Amount in word", compute='_onchange_amount', store=True)
    electronig = fields.Boolean(string='Cheque', copy=False)
    cheque_number = fields.Char('Cheque number')
    check_count = fields.Integer(compute='_compute_check')
    count_je = fields.Integer(compute='_count_je_compute')
    count_diff = fields.Integer(compute='_count_diff_compute')
    check_term = fields.Selection([('not_followup', 'Not Follow-up'),
                                   ('followup', 'Follow-up')
                                   ],
                                  default='not_followup', invisible=True)
    person = fields.Char(string= 'Ben', track_visibility='onchange')

    bank_template = fields.Many2one(related='journal_id.bank_id')
    check_id = fields.Many2one('check.followup', string="Check Reference", readonly=True)
    custody_date = fields.Date('Date', default=lambda self: fields.Date.today(),track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency',default=default_currency,required=True)
    amount = fields.Monetary('Amount',required=True,track_visibility='onchange')
    sequence = fields.Integer(required=True, default=1,)
    state = fields.Selection([('draft','Draft'),
                              ('dm','Submitted'),
                              ('am','Confirmed'),
                              ('fm','Approved'),
                              ('post','Posted'),
                              ('cancel','Cancel')],default='draft', track_visibility='onchange')
    company_id = fields.Many2one('res.company',string="Company",default=default_company)

    # Accounting Fields
    move_id = fields.Many2one('account.move',string='JV Ref',readonly=True)
    journal_id = fields.Many2one('account.journal',string='Pay by',domain="[('type','in',['cash','bank'])]")
    custody_journal_id = fields.Many2one('account.journal',string='Employee Account',domain="[('type','=','general')]")
    journal_type = fields.Selection(related='journal_id.type')
    account_id = fields.Many2one('account.account',compute='_account_compute',string='Custody account')
    user_id = fields.Many2one('res.users', default=default_user_analytic)
    count_journal_entry = fields.Integer(compute='_compute_je')

    def _compute_je(self):
        if self.move_id:
            self.count_journal_entry = 1
        else:
            self.count_journal_entry = 0

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
    @api.onchange('custody_journal_id')
    def get_desc(self):
        self.description = 'Custody for account' + ' ' + str(self.custody_journal_id.name)

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

    def action_journal_entry(self):

        tree_view = self.env.ref('account.view_move_tree')
        form_view = self.env.ref('account.view_move_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Journal Entry',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', '=', self.move_id.id)],

        }

    @api.depends('user_name')
    def _account_compute(self):
        setting_ob = self.env['res.config.settings'].search([],order='id desc', limit=1)
        print('aaaaaaaaaaaaaaaaaaa',setting_ob)
        if setting_ob.petty_account_id:
            self.account_id = setting_ob.petty_account_id
        if not self.company_id.petty_account_id:
            raise ValidationError('Please Insert Petty cash account In Company Configuration')
        else:
            self.account_id = self.company_id.petty_account_id

    analytic_account = fields.Many2one('account.analytic.account',string='Analytic Account')

    def confirm_dm(self):
        if self.amount <= 0:
            raise ValidationError("Please Make Sure Amount Field Grater Than Zero !!")
        if self.env.user.name != self.user_id.name:
            raise ValidationError("Please This Request is not For You")
        if self.electronig==True:
            if not self.check_date and not self.check_number:
                raise ValidationError(_('Please enter cheque date and number'))

        self.write({'state': 'dm'})
        desc=self.account_id.id
        self.description= 'Custody for account' + ' ' + str(self.custody_journal_id.name)
    def confirm_am(self):

        self.write({'state': 'am'})

    def confirm_fm(self):
       ## if self.check_term == 'followup' and self.journal_type != 'bank':
         ##   raise ValidationError("Please Don't Filling Check Information")
       ## elif self.check_term == 'followup' and self.journal_type == 'bank':
         ##   if not self.check_date or not self.check_number or not self.bank_template:
           ##     raise ValidationError("Please Fill Check Information First !")
        self.write({'state': 'fm'})


        if not self.journal_id or not self.account_id or not self.custody_journal_id:
            raise ValidationError("Please Fill Accounting information (Journal-Employee-Account)")

    @api.model
    def get_amount(self):
        if self.currency_id != self.env.user.company_id.currency_id:
            return self.amount * self.env.user.company_id.currency_id.rate
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

    # confirm Finance Approval (Posted)
    def confirm_post(self):
        global check_obj, check_val
        account_move_object = self.env['account.move']
        if not self.account_id or not self.journal_id or not self.custody_journal_id:
            raise ValidationError("Please Make Sure Partner Accounting Tab was Entered or Journal !!")
        if self.account_id and self.journal_id and self.custody_journal_id and self.electronig==False:
            l = []
            if not self.account_id or not self.journal_id and not self.custody_journal_id:
                raise ValidationError("Please Fill Accounting Information !!")
            # if self.check_term != 'followup':
            debit_val = {
                'move_id': self.move_id.id,
                'name': 'Custody for account' + ' ' + str(self.custody_journal_id.name),
                'account_id': self.account_id.id,
                'debit': self.get_amount(),
                # 'analytic_account_id': self.analytic_account.id or False,
                'currency_id': self.get_currency() or False,
                'partner_id': self.user_name.partner_id.id,
                'amount_currency': self.amount_currency_debit() or False,
                # 'company_id': self.company_id.id,

            }
            l.append((0, 0, debit_val))
            credit_val = {

                'move_id': self.move_id.id,
                'name': 'Custody for account' + ' ' + str(self.custody_journal_id.name),
                # 'account_id': self.journal_id.account_id.id,
                'account_id': self.journal_id.default_credit_account_id.id,
                'credit': self.get_amount(),
                'currency_id': self.get_currency() or False,
                # 'partner_id': self.user_name.partner_id.id,
                'amount_currency': self.amount_currency_credit() or False,
                # 'analytic_account_id': ,
                # 'company_id': ,

            }
            l.append((0, 0, credit_val))
            print("List", l)
            vals = {
                'journal_id': self.custody_journal_id.id,
                'date': self.custody_date,
                'ref': self.name,
                # 'company_id': ,
                'line_ids': l,
            }
            self.move_id = account_move_object.create(vals)
            self.move_id.post()
            ###############################################
            # report_ob = self.env['pettycash.report']
            # report_vals ={
            #     'company_id': self.company_id.id,
            #     'currency_id': self.currency_id.id,
            #     'user_id': self.user_name.id,
            #     'amount': self.amount,
            #     'analytic_id': self.analytic_account.id,
            #     'request_id': self.id,
            #     'date': self.custody_date,
            # }
            # report_ob.sudo().create(report_vals)
            ###############################################
            self.state = 'post'

        if self.account_id and self.journal_id and self.custody_journal_id and self.electronig==True:
            l = []
            person = self.person
            check_obj = self.env['check.followup']
            credit_name = 'Cheque number' + '  ' + self.cheque_number
            if not self.account_id or not self.journal_id and not self.custody_journal_id:
                raise ValidationError("Please Fill Accounting Information !!")
            # if self.check_term != 'followup':
            debit_val = {
                'move_id': self.move_id.id,
                'name': 'Custody for account' + ' ' + str(self.custody_journal_id.name),
                'account_id': self.account_id.id,
                'debit': self.get_amount(),
                # 'analytic_account_id': self.analytic_account.id or False,
                'currency_id': self.get_currency() or False,
                'partner_id': self.user_name.partner_id.id,
                'amount_currency': self.amount_currency_debit() or False,
                # 'company_id': self.company_id.id,

            }
            l.append((0, 0, debit_val))
            credit_val = {

                'move_id': self.move_id.id,
                'name': 'Custody for account' + ' ' + str(self.custody_journal_id),
                'account_id': self.journal_id.out_account.id,
                'credit': self.get_amount(),
                'currency_id': self.get_currency() or False,
                # 'partner_id': self.user_name.partner_id.id,
                'amount_currency': self.amount_currency_credit() or False,
                # 'analytic_account_id': ,
                # 'company_id': ,

            }
            l.append((0, 0, credit_val))
            print("List", l)
            vals = {
                'journal_id': self.custody_journal_id.id,
                'date': self.custody_date,
                'ref': self.name,
                # 'company_id': ,
                'line_ids': l,
            }
            self.move_id = account_move_object.create(vals)
            self.move_id.post()
            ###############################################
            # report_ob = self.env['pettycash.report']
            # report_vals ={
            #     'company_id': self.company_id.id,
            #     'currency_id': self.currency_id.id,
            #     'user_id': self.user_name.id,
            #     'amount': self.amount,
            #     # 'analytic_id': self.analytic_account.id,
            #     'request_id': self.id,
            #     'date': self.custody_date,
            # }
            #
            # report_ob.sudo().create(report_vals)
            ###############################################


            check_val = {
            'check_created': self.custody_date,
            'check_date': self.check_date,
            'cheque_number': self.cheque_number,
             'source_document': self.name,
             'beneficiary': person,
            'currency_id': self.currency_id.id,
            'amount': self.amount,
            'state': 'out_standing',
            'check_type': 'out',
            'partner_id': False,
        # 'check_move_id': a.id,
            'bank_id': self.journal_id.id,
            'memo': credit_name,

            }


            check_id = check_obj.sudo().create(check_val)

            log_obj = self.env['check.log']
            log_obj.create({'move_description': 'Out cheque ',
                    'move_id': self.move_id.id,
                    'move_date': self.custody_date,
                    'check_id': check_id.id, })
            self.state = 'post'

    @api.model
    def create(self, vals):
        code = 'custody.request.code'
        if vals.get('name', 'New') == 'New':
            message = 'Petty cash request' + self.env['ir.sequence'].next_by_code(code)
            vals['name'] = message
            # self.message_post(subject='Create CR', body='This is New CR Number' + str(message))
        return super(FinanceApprovalRequest, self).create(vals)

    # @api.multi
    def unlink(self):
        for i in self:
            if i.state != 'draft':
                raise ValidationError("Please Make Sure State in DRAFT !!")
            else:
                super(FinanceApprovalRequest, i).unlink()

    def copy(self):
        raise ValidationError("Can not Duplicate a Record !!")

    def cancel_request(self):
        if self.custody_journal_id.update_posted == False:
            raise ValidationError("Please Check Allow Cancel Journal Entry In Journal First !!")
        else:
            # Cancel JE and Delete it
            self.move_id.button_cancel()
            self.move_id.unlink()

            # delete report line
            report_id = self.env['pettycash.report'].search([('request_id','=',self.id)])
            report_id.sudo().unlink()

            # Change the state
            self.state = 'cancel'

    def reject(self):
        self.state = 'draft'


class InheritCompany(models.Model):
    _inherit = 'res.company'

    petty_account_id = fields.Many2one('account.account',string='Petty cash account')
