from odoo import fields , models,api,tools,_


class ChangeBankWizard(models.TransientModel):
    _name = 'change.bank'

    def _default_bank(self):
        active_id = self.env['check.followup'].browse(self._context.get('active_id'))
        return active_id.bank_id

    def _default_type(self):
        active_id = self.env['check.followup'].browse(self._context.get('active_id'))
        return active_id.check_type

    journal_id = fields.Many2one('account.journal',string='Change Bank To',required=True,domain=[('type','=','bank')],
                                 default=_default_bank)
    deposit_date = fields.Date(string='Deposit Date', required=True, default=fields.Date.today())
    withdraw_date = fields.Date(string='Withdraw Date', required=True, default=fields.Date.today())
    check_type = fields.Char(default=_default_type)

    def wizard_submit(self):
        active_id = self.env['check.followup'].browse(self._context.get('active_id'))
        if active_id.check_type == 'in':
            active_id.deposit_in_bank(self.deposit_date,self.journal_id)

        if active_id.check_type == 'out':
            active_id.withdraw_check(self.withdraw_date)
