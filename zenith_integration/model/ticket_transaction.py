from odoo import models, fields
from odoo.exceptions import ValidationError,UserError


class TicketTransaction(models.Model):
    _name = 'ticket.transaction'
    _description = 'Ticket Transaction'

    company_id = fields.Many2one('res.company',string='Company',compute='_company_com')
    count_invoice = fields.Integer(compute='_count_invoice')
    sale_statement_export_id = fields.Integer(string='ID SaleStatement Accounting Export')
    date = fields.Datetime(string='Date', required=True)
    name = fields.Char(string='Transaction Name')
    pnr_zenith = fields.Char(string='PNR Zenith')
    record_locator = fields.Char(string='Record Locator')
    heading_st_type = fields.Char(string='Heading (Statment Type)')
    iata_agency_code = fields.Char(string='IATA Agency Code')
    point_of_sales = fields.Char(string='Point of Sales')
    customer = fields.Char(string='Customer')
    payment_type = fields.Char(string='Payment Type')
    balance_sale_currency = fields.Char(string='Balance Sale Currency')
    yq_tax_amount = fields.Char(string='YQ Tax Amount')
    yr_tax_amount = fields.Char(string='YR Tax Amount')
    service_fee_tax_amount = fields.Char(string='Service fee Tax amount')
    insurance_tax_amount = fields.Char(string='Insurance Tax amount')
    other_tax_amount = fields.Char(string='Other Tax amount')
    airline_tax_amount = fields.Char(string='Airline Tax amount')
    iata_tax_amount = fields.Char(string='IATA Tax amount')
    total_tax_amount = fields.Char(string='Total Tax amount')
    sale_agent = fields.Char(string='Sale Agent')
    original_ticket_number = fields.Char(string='Original Ticket Number')
    ticket_number = fields.Char(string='Ticket Number')
    exchanged_ticket_number = fields.Char(string='Exchanged Ticket Number')
    customer_id = fields.Char(string='Customer ID')
    journal_type = fields.Char(string='Journal Type')
    taxes_list = fields.Char(string='Taxes List')
    fair_basis_list = fields.Char(string='Fair Basis List')
    pnr_creator = fields.Char(string='PNR Creator')
    base_fair = fields.Char(string='Base Fair')
    sale_statement_status = fields.Char(string='Sale Statement Status')
    taxes = fields.Char(string='Taxes')
    tax_a3 = fields.Char(string='Tax A3')
    tax_ac = fields.Char(string='Tax AC')
    tax_ae = fields.Char(string='Tax AE')
    iata_passenger_type = fields.Char(string='IATA Passenger Type')
    passenger_civility = fields.Char(string='Passenger Civility')
    passenger_surname = fields.Char(string='Passenger Surname')
    passenger_first_name = fields.Char(string='Passenger First name')
    nationality = fields.Char(string='Nationality')
    date_of_birth = fields.Date(string='Date of Birth')
    place_of_birth = fields.Char(string='Place of Birth')
    passport_number = fields.Char(string='Passport Number')
    email_address = fields.Char(string='Email Address')
    mobile_number = fields.Char(string='Mobile Number')
    flight_number = fields.Char(string='Flight Number')
    flight_date = fields.Date(string='Flight Date')
    class_of_service = fields.Char(string='Class of service')
    booking_class = fields.Char(string='Booking Class')
    coupon_status = fields.Char(string='Coupon Status')
    aircraft_type = fields.Char(string='Aircraft Type')
    commission = fields.Char(string='Commission')
    discount = fields.Char(string='Discount')
    tour_code_discount = fields.Char(string='Tour Code Discount')
    adjustment = fields.Char(string='Adjustment')
    penalty = fields.Char(string='Penalty')
    acm = fields.Char(string='Agency Credit Memo')
    adm = fields.Char(string='Agency Debit Memo')
    baggage_supplement = fields.Char(string='Baggage Supplement')
    pnr_alphanumeric = fields.Char(string='PNR Alpha')
    baggage_supplement_cancelation = fields.Char(string='Baggage Supplement Cancelation')
    invoice_id = fields.Many2one('account.move',string='Invoice')

    def _company_com(self):
        company_obj = self.env['res.company'].search([])
        dubai_company = self.env['res.company'].search([('id','=',15)])
        cairo_company = self.env['res.company'].search([('id','=',10)])
        # for rec in self:
        for rec in self:
            for i in company_obj:
                # raise ValidationError(rec.point_of_sales)
                if rec.point_of_sales == 'TARCO AVIATION DUBAI STATION ':
                    rec.company_id = dubai_company
                if rec.point_of_sales == 'Tarco Aviation Cairo Station':
                    rec.company_id = cairo_company
                else:
                    rec.company_id = None

    def _count_invoice(self):
        for rec in self:
            if rec.invoice_id:
                rec.count_invoice = 1
            else:
                rec.count_invoice = 0

    def view_invoice(self):
        list_view = self.env.ref('account.view_out_invoice_list')
        form_view = self.env.ref('account.view_move_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Invoice',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'views': [(list_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', '=', self.invoice_id.id)],

        }
    # @api.multi
    def action_invoice(self):
        rec_obj = self.env['ticket.transaction'].search([('heading_st_type','=','Ticket payment'),
                                                         ('point_of_sales','=','TARCO AVIATION DUBAI STATION ')])
        for rec in rec_obj:
            l = []
            if rec.company_id.id == 15 and not rec.invoice_id:
                if rec.heading_st_type == 'Ticket payment':
                    price = float(rec.balance_sale_currency)
                    account_move_line = {
                        'account_id': rec.company_id.sale_account_id.id,
                        'quantity': 1,
                        'price_unit': price,
                        'tax_ids': None,

                    }
                    l.append((0, 0, account_move_line))
                    # print("List", l).encode("utf-8")
                    account_move = rec.env['account.move']
                    account_move_dic = {
                        'partner_id': rec.company_id.zenith_partner_id.id,
                        'move_type': 'out_invoice',
                        'flight_no': rec.record_locator or rec.pnr_zenith,
                        'pnr_alpha': rec.pnr_alphanumeric,
                        'iata_agency_code': rec.iata_agency_code,
                        'pos': rec.point_of_sales,
                        'customer_name': rec.customer,
                        'customer_zenith_id': rec.customer_id,
                        'transaction_name': rec.name,
                        'payment_type': rec.payment_type,
                        'balance_sales_currency': rec.balance_sale_currency,
                        'sale_agent': rec.sale_agent,
                        'ticket_number': rec.ticket_number,
                        'heading_st_payment': rec.heading_st_type,
                        'invoice_date': rec.date,
                        'invoice_line_ids': l,
                    }
                    rec.invoice_id = account_move.create(account_move_dic)
                    rec.invoice_id.action_post()
                
                
        rec_cairo = self.env['ticket.transaction'].search([('heading_st_type','=','Ticket payment'),
                                                         ('point_of_sales','=','Tarco Aviation Cairo Station')])
        for rec in rec_cairo:
            l = []
            if rec.company_id.id == 10 and not rec.invoice_id:
                if rec.heading_st_type == 'Ticket payment':
                    price = float(rec.balance_sale_currency)
                    account_move_line = {
                        'account_id': rec.company_id.sale_account_id.id,
                        'quantity': 1,
                        'price_unit': price,
                        'tax_ids': None,

                    }
                    l.append((0, 0, account_move_line))
                    # print("List", l).encode("utf-8")
                    account_move = rec.env['account.move']
                    account_move_dic = {
                        'partner_id': rec.company_id.zenith_partner_id.id,
                        'move_type': 'out_invoice',
                        'flight_no': rec.record_locator or rec.pnr_zenith,
                        'pnr_alpha': rec.pnr_alphanumeric,
                        'iata_agency_code': rec.iata_agency_code,
                        'pos': rec.point_of_sales,
                        'customer_name': rec.customer,
                        'customer_zenith_id': rec.customer_id,
                        'transaction_name': rec.name,
                        'payment_type': rec.payment_type,
                        'balance_sales_currency': rec.balance_sale_currency,
                        'sale_agent': rec.sale_agent,
                        'ticket_number': rec.ticket_number,
                        'heading_st_payment': rec.heading_st_type,
                        'invoice_date': rec.date,
                        'invoice_line_ids': l,
                    }
                    rec.invoice_id = account_move.create(account_move_dic)
                    


    def action_test(self):
        from zeep import Client
        wsdl_url = 'http://preprod4.ttinteractive.com/TTIDotNet/WebService/Internal/RevenueAccountingWebService/RevenueAccountingService.svc?wsdl'
        user = 'ws3T'
        password = '2817d7f42c105959e2e673f493a83a3e'

        # Create a Zeep client using the WSDL URL
        client = Client(wsdl_url)

        # Construct the request payload
        # request_payload = {
        #     'request': {
        #         'POS': {'Source': {'AirlineVendorID': '2012'}},
        #         'Login': user,
        #         'Password': password,
        #         'DateLT': '2024-02-02',
        #         'TimeStamp': '2024-02-28T12:00:00',
        #         'UseWrappedExceptionInFaultException': True
        #     }
        # }# request_payload = {
        #     'request': {
        #         'POS': {'Source': {'AirlineVendorID': '2012'}},
        #         'Login': user,
        #         'Password': password,
        #         'DateLT': '2024-02-02',
        #         'TimeStamp': '2024-02-28T12:00:00',
        #         'UseWrappedExceptionInFaultException': True
        #     }
        # }

        # Construct the request payload
        request_payload = {
            'request': {
                'POS': {'Source': {'AirlineVendorID': '2012'}},
                'Login': user,
                'Password': password,
                'DateLT': '2024-02-02',
                'TimeStamp': '2024-02-28T12:00:00',
                'UseWrappedExceptionInFaultException': True
            }
        }

        # request_payload = {
        #     'request': {
        #         'POS': {'Source': {'AirlineVendorID': '2012'}},
        #         'Login': user,
        #         'Password': password,
        #         'StartDateLT': '2024-02-25',
        #         'EndDateLT': '2024-02-28',
        #         'TimeStamp': '2024-02-28T12:00:00',
        #         'UseWrappedExceptionInFaultException': True
        #     }
        # }
        try:
            # Make the SOAP request using the GetOdooTickets operation
            # response = client.service.GetOdooCreditLimitPayments(**request_payload)
            response = client.service.GetFlightInformation(**request_payload)
            print(response)
            client.Close()
        except Exception as e:
            client.Close()
            print("An error occurred:", e)


    '''
      {
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
            }
    '''