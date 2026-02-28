from odoo import models, fields

class CreditLimit(models.Model):
    _name = 'credit.limit'
    _description = 'Credit Limit'

    date = fields.Date(string='Date', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer ID')
    customer_ref = fields.Char(string='Customer Reference')

    cash_statement_id = fields.Integer(string='ID Cash Statement')
    name = fields.Char(string='Name')
    agency_name = fields.Char(string='Agency Name')
    date_of_payment = fields.Datetime(string='Date of payment')
    payment_amount = fields.Char(string='Payment amount (Sale currency)')
    sale_currency = fields.Char(string='Sale currency')
    available_credit_before = fields.Char(string='Available credit before payment (incl. authorized credit)')
    currency_before = fields.Char(string='Currency Before')
    available_credit_after = fields.Char(string='Available credit after payment (incl. authorized credit)')
    currency_after = fields.Char(string='Currency After')
    payment_registered = fields.Char(string='Payment registered by')
    authorized_credit = fields.Char(string='Authorized credit (credit limit)')
    currency_credit = fields.Char(string='Currency Credit')
    total_sold = fields.Char(string='Total sold')
    sold_currency = fields.Char(string='Sold Currency')
    total_paid = fields.Char(string='Total Paid')
    total_paid_currency = fields.Char(string='Total Paid Currency')
    reference_number = fields.Char(string='Reference number')
    sales_report = fields.Char(string='Sales report')
    fop = fields.Char(string='FOP')

    transaction_number = fields.Char(string='Transaction number')
    payment_amount_base_currency = fields.Char(string='Payment Amount Base Currency')
    available_credit_before_payment = fields.Char(string='CL Currency Available Credit Before Payment')

    '''
                               'PaymentAmountBaseCurrency': '1106500.00',
                               'CLCurrencyAvailableCreditBeforePayment': 'SDG',
                               'BanktransactionNumber': None'''

    '''
    'ID_Customer': 10358060,
                'AgencyName': 'PZU ALLUALWAH TRAVEL AGENCY',
                'DateOfPayment': datetime.datetime(2024, 2, 3, 23, 36, 58),
                'PaymentAmountSaleCurrency': '1106500.00',
                'PaymentAmountBaseCurrency': '1106500.00',
                'AvailableCreditBeforePayment': '0.00',
                'AvailableCreditAfterPayment': '1106500.00',
                'PaymentRegisteredBy': 'sufyan emad',
                'AutorizedCredit': '0.00',
                'TotalSold': '140847821.80',
                'TotalPaid': '140847821.80',
                'ReferenceNumber': '789332',
                'IsLinkedSalesReport': 0,
                'FOP': 189,
                'SaleCurrency': 'SDG',
                'BaseCurrency': 'SDG',
                'CLCurrencyAvailableCreditBeforePayment': 'SDG',
                'CLCurrencyAvailableCreditAfterPayment': 'SDG',
                'CLCurrencyAutorizedCredit': 'SDG',
                'CLCurrencyTotalSold': 'SDG',
                'CLCurrencyTotalPaid': 'SDG',
                'BanktransactionNumber': None
  
  '''