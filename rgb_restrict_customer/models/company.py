from odoo import api, fields, models

class ResCompany(models.Model):

    _inherit = 'res.company'

    print_only_posted_invoices = fields.Boolean(
        string="Print Only Posted Invoices",
        help="If checked, only posted invoices will be printed. "
             "If unchecked, all invoices will be printed regardless of their state.",
        default=False
    )
