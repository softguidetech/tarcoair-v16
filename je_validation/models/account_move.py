# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"


    def action_post(self):
        if self.amount_total == 0;
            raise ValidationError('Please be sure total of entry should be greater than zero !!')
        for rec in self.invoice_line_ids:
            if rec.price_total == 0:
                raise ValidationError('Please be sure total of some line should be greater than zero !!')
        super(AccountMove,self).action_post()
