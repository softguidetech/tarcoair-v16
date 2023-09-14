# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Niyas Raphy(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields


class ResUsersInherit(models.Model):
    _inherit = 'account.move'

    username_id = fields.Many2one('tarco.users', string='Username')


class CashVoucherInherit(models.Model):
    _inherit = 'cash.voucher'

    username_id = fields.Many2one('tarco.users', string='Username')

class RequestInboundInherit(models.Model):
    _inherit = 'request.inbound'

    username_id = fields.Many2one('tarco.users', string='Username')

class CheckOutInherit(models.Model):
    _inherit = 'check.voucher'

    username_id = fields.Many2one('tarco.users', string='Username')

class CheckInInherit(models.Model):
    _inherit = 'check.inbound'

    username_id = fields.Many2one('tarco.users', string='Username')

# class PaymentInherit(models.Model):
#     _inherit = 'account.payment'
#     username_id = fields.Many2one('tarco.users', string='Username',required=True)

class TarcoUsers(models.Model):
    _name = 'tarco.users'

    name = fields.Char(string='Username')