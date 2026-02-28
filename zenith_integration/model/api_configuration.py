from odoo import models, fields, api, _
from zeep import Client
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError



class APIConfiguration(models.Model):
    _name = 'zenith.api.configuration'
    _description = 'API Configuration'

    name = fields.Char(string='Name')
    active = fields.Boolean('Active', default=True)
    code = fields.Char(string='Code')
    login = fields.Char(string='Login')
    url = fields.Char(string='URL',
                      default='http://preprod4.ttinteractive.com/TTIDotNet/WebService/Internal/RevenueAccountingWebService/RevenueAccountingService.svc?wsdl')
    password = fields.Char(string='Password')
    air_line_vendor_id = fields.Char(string='Air line Vendor ID')
    credit_limit_last_update = fields.Date(string='Credit Limit Last update')
    tickets_last_update = fields.Date(string='Tickets Last update')
    flow_tickets_last_update = fields.Date(string='Flown Tickets Last update')
    _sql_constraints = [
        ('unique_login_password_airline_vendor', 'unique(login, password, air_line_vendor_id)',
         'Login, Password, and Air line Vendor ID must be unique!')
    ]

    def action_sync_credit_limit_payments(self):
        api_credential = self.env['zenith.api.configuration'].search([('active', '=', True)], limit=1)
        current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        current_date = datetime.now()
        today_date = fields.Date.today()

        url = api_credential.url
        login = api_credential.login
        password = api_credential.password
        air_line_vendor_id = api_credential.air_line_vendor_id
        
        # Get the last update date, default to 30 days ago if not set
        if api_credential.credit_limit_last_update:
            start_date = api_credential.credit_limit_last_update
        else:
            start_date = today_date - timedelta(days=30)
        
        # Format date for API - use today's date for DateLT (fetch all records up to today)
        # We'll filter by start_date on the client side
        end_date_str = today_date.strftime('%Y-%m-%d')

        # Create a Zeep client using the WSDL URL
        client = Client(url)

        # Construct the request payload - use DateLT with today's date
        request_payload = {
            'request': {
                'POS': {'Source': {'AirlineVendorID': air_line_vendor_id}},
                'Login': login,
                'Password': password,
                'DateLT': end_date_str,  # Fetch all records up to today
                'TimeStamp': current_timestamp,
                'UseWrappedExceptionInFaultException': True
            }
        }

        try:
            # Make the SOAP request using the GetOdooCreditLimitPayments operation
            response = client.service.GetOdooCreditLimitPayments(**request_payload)
            all_records = []
            if not response.CreditLimits or not response.CreditLimits.OdooCreditLimitPayment:
                return
            
            # Convert start_date to datetime for comparison
            if isinstance(start_date, date) and not isinstance(start_date, datetime):
                start_date_dt = datetime.combine(start_date, datetime.min.time())
            elif isinstance(start_date, datetime):
                start_date_dt = start_date
            else:
                try:
                    start_date_dt = datetime.strptime(str(start_date), '%Y-%m-%d')
                except:
                    start_date_dt = datetime.combine(fields.Date.from_string(str(start_date)), datetime.min.time())
            
            for record_data in response.CreditLimits.OdooCreditLimitPayment:
                # Filter records by date - only include records from start_date onwards
                payment_date = getattr(record_data, 'DateOfPayment', None)
                if payment_date:
                    # Convert payment_date to datetime for comparison
                    if isinstance(payment_date, datetime):
                        payment_date_dt = payment_date
                    elif isinstance(payment_date, str):
                        try:
                            payment_date_dt = datetime.strptime(payment_date, '%Y-%m-%dT%H:%M:%S')
                        except:
                            try:
                                payment_date_dt = datetime.strptime(payment_date, '%Y-%m-%d')
                            except:
                                payment_date_dt = None
                    else:
                        payment_date_dt = None
                    
                    # Skip records before start_date
                    if payment_date_dt and payment_date_dt < start_date_dt:
                        continue
                # Convert numeric values to strings for Char fields
                payment_amount = getattr(record_data, 'PaymentAmountSaleCurrency', 0)
                available_credit_before = getattr(record_data, 'AvailableCreditBeforePayment', 0)
                available_credit_after = getattr(record_data, 'AvailableCreditAfterPayment', 0)
                authorized_credit = getattr(record_data, 'AutorizedCredit', 0)
                total_sold = getattr(record_data, 'TotalSold', 0)
                total_paid = getattr(record_data, 'TotalPaid', 0)
                payment_amount_base = getattr(record_data, 'PaymentAmountBaseCurrency', 0)
                sales_report = getattr(record_data, 'IsLinkedSalesReport', False)
                fop_value = getattr(record_data, 'FOP', '')
                
                all_records.append({
                    'date': current_date,
                    'name': getattr(record_data, 'AgencyName', '') or '',  # Use agency name as name
                    'customer_ref': getattr(record_data, 'ID_Customer', None),
                    'cash_statement_id': getattr(record_data, 'ID_CashStatement', None),
                    'agency_name': getattr(record_data, 'AgencyName', ''),
                    'date_of_payment': getattr(record_data, 'DateOfPayment', None),
                    'payment_amount': str(payment_amount) if payment_amount else '',
                    'sale_currency': getattr(record_data, 'SaleCurrency', ''),
                    'available_credit_before': str(available_credit_before) if available_credit_before else '',
                    'currency_before': getattr(record_data, 'BaseCurrency', ''),
                    'available_credit_after': str(available_credit_after) if available_credit_after else '',
                    'currency_after': getattr(record_data, 'CLCurrencyAvailableCreditAfterPayment', ''),
                    'payment_registered': getattr(record_data, 'PaymentRegisteredBy', ''),
                    'authorized_credit': str(authorized_credit) if authorized_credit else '',
                    'currency_credit': getattr(record_data, 'CLCurrencyAutorizedCredit', ''),
                    'total_sold': str(total_sold) if total_sold else '',
                    'sold_currency': getattr(record_data, 'CLCurrencyTotalSold', ''),
                    'total_paid': str(total_paid) if total_paid else '',
                    'total_paid_currency': getattr(record_data, 'CLCurrencyTotalPaid', ''),
                    'reference_number': getattr(record_data, 'ReferenceNumber', ''),
                    'sales_report': 'Yes' if sales_report else 'No',  # Convert boolean to string
                    'fop': str(fop_value) if fop_value else '',
                    'payment_amount_base_currency': str(payment_amount_base) if payment_amount_base else '',
                    'available_credit_before_payment': getattr(record_data, 'CLCurrencyAvailableCreditBeforePayment', ''),
                    'transaction_number': getattr(record_data, 'BanktransactionNumber', None) or '',
                })
            if all_records:
                self._create_credit_limits(all_records)
                api_credential.credit_limit_last_update = fields.Date.today()
        except Exception as e:
            # client.Close()
            print("An error occurred:", e)

    def action_sync_flown_tickets(self):
        api_credential = self.env['zenith.api.configuration'].search([('active', '=', True)], limit=1)
        current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        current_date = datetime.now()
        today_date = fields.Date.today()

        url = api_credential.url
        login = api_credential.login
        password = api_credential.password
        air_line_vendor_id = api_credential.air_line_vendor_id
        
        # Get the last update date, default to 30 days ago if not set
        if api_credential.flow_tickets_last_update:
            start_date = api_credential.flow_tickets_last_update
        else:
            start_date = today_date - timedelta(days=30)
        
        # Format date for API - use today's date for DateLT (fetch all records up to today)
        # We'll filter by start_date on the client side
        end_date_str = today_date.strftime('%Y-%m-%d')
        
        # Create a Zeep client using the WSDL URL
        client = Client(url)

        # Construct the request payload - use DateLT with today's date
        request_payload = {
            'request': {
                'POS': {'Source': {'AirlineVendorID': air_line_vendor_id}},
                'Login': login,
                'Password': password,
                'DateLT': end_date_str,  # Fetch all records up to today
                'TimeStamp': current_timestamp,
                'UseWrappedExceptionInFaultException': True
            }
        }

        try:
            # Make the SOAP request using the GetOdooFlownTickets operation
            response = client.service.GetOdooFlownTickets(**request_payload)
            all_records = []
            if response and not response.FlownTickets or not response.FlownTickets.OdooFlownTicket:
                return
            
            # Convert start_date to datetime for comparison
            if isinstance(start_date, date) and not isinstance(start_date, datetime):
                start_date_dt = datetime.combine(start_date, datetime.min.time())
            elif isinstance(start_date, datetime):
                start_date_dt = start_date
            else:
                try:
                    start_date_dt = datetime.strptime(str(start_date), '%Y-%m-%d')
                except:
                    start_date_dt = datetime.combine(fields.Date.from_string(str(start_date)), datetime.min.time())
            
            for record_data in response.FlownTickets.OdooFlownTicket:
                # Filter records by date - only include records from start_date onwards
                coupon_created = getattr(record_data, 'CouponIssuedCreated', None)
                if coupon_created:
                    # Convert coupon_created to datetime for comparison
                    if isinstance(coupon_created, datetime):
                        coupon_date_dt = coupon_created
                    elif isinstance(coupon_created, str):
                        try:
                            coupon_date_dt = datetime.strptime(coupon_created, '%Y-%m-%dT%H:%M:%S')
                        except:
                            try:
                                coupon_date_dt = datetime.strptime(coupon_created, '%Y-%m-%d')
                            except:
                                coupon_date_dt = None
                    else:
                        coupon_date_dt = None
                    
                    # Skip records before start_date
                    if coupon_date_dt and coupon_date_dt < start_date_dt:
                        continue
                
                exchanged_ticket = getattr(record_data, 'IATATicketNumberExchanged', None)
                exchanged_check = getattr(record_data, 'IATATicketCheckDigitExchanged', None)
                arrival_elem = getattr(record_data, 'TVLArrivalElement', None)
                continuation_elem = getattr(record_data, 'TVLContinuationElement', None)
                excess_weight = getattr(record_data, 'EBDExcedentBagWeight', None)
                excess_fee = getattr(record_data, 'EBDAmountExcessBagPayedSaleCurrency', None)
                
                all_records.append({
                    'date': fields.Date.today(),
                    'coupon_issued_created': getattr(record_data, 'CouponIssuedCreated', None),
                    'coupon_issued_modified': getattr(record_data, 'CouponIssuedModified', None),
                    'export_id': getattr(record_data, 'ID_CouponAccountingExport', None),
                    'customer_ref': getattr(record_data, 'ID_Customer', None),
                    'pnr_alphanumeric': getattr(record_data, 'RCIRLoc', ''),
                    'iata_ticket_number': getattr(record_data, 'IATATicketNumber', ''),
                    'iata_ticket_check_digit': getattr(record_data, 'IATATicketCheckDigit', ''),
                    'coupon_order_on_ticket': str(getattr(record_data, 'CPNOrderOnTicket', '')),
                    'coupon_order_on_segment': str(getattr(record_data, 'CPNSegmentOrder', '')),
                    'Original_iata_ticket_number': getattr(record_data, 'IATATicketNumberOriginator', ''),
                    'Original_iata_ticket_check_digit': getattr(record_data, 'IATATicketCheckDigitOriginator', ''),
                    'exchanged_iata_ticket_number': exchanged_ticket if exchanged_ticket else '',
                    'exchanged_iata_ticket_check_digit': exchanged_check if exchanged_check else '',
                    'zenith_coupon_status': str(getattr(record_data, 'ID_CPNAeropackStatus', '')) if getattr(record_data, 'ID_CPNAeropackStatus', '') else '',
                    'aircraft_type': getattr(record_data, 'TVLAircraftType', ''),
                    'arrival_element': arrival_elem if arrival_elem else '',
                    'continuation_element': continuation_elem if continuation_elem else '',
                    'class_of_service': getattr(record_data, 'TVLCabinClassOfServiceCode', ''),
                    'airline_designator': getattr(record_data, 'TVLAirlineDesignator', ''),
                    'Flight_number': getattr(record_data, 'TVLFlightNumber', ''),
                    'local_dep_datetime': getattr(record_data, 'TVLDepartureDateAndHourLT', None),
                    'local_arr_datetime': getattr(record_data, 'TVLArrivalDateAndHourLT', None),
                    'departure_airport': getattr(record_data, 'TVLIATADepartureAirport', ''),
                    'arrival_airport': getattr(record_data, 'TVLIATAArrivalAirport', ''),
                    'booking_class': getattr(record_data, 'TVLClassCodePRBD', ''),
                    'coupon_service': getattr(record_data, 'ID_AeropackFareBasisClass', ''),
                    'fare_basis_class': getattr(record_data, 'PTSFareBasisClass', ''),
                    'point_of_sale': getattr(record_data, 'PointOfSaleName', ''),
                    'point_of_sale_code': getattr(record_data, 'CompanyUserCode', ''),
                    'payment_type_identifier': getattr(record_data, 'ID_PaymentMode', ''),
                    'customer_name': getattr(record_data, 'CustomerName', ''),
                    'coupon_price_taxes_commission': str(getattr(record_data, 'CPNHNetFareWithoutTaxSaleCurrency', 0)),
                    'coupon_price_taxes': str(getattr(record_data, 'CPNEEquivalentFareWithoutTaxSaleCurrency', 0)),
                    'total_turnover_amount': str(getattr(record_data, 'TotalTurnoverAmountSaleCurrency', 0)),
                    'coupon_commission_amount': str(getattr(record_data, 'CPNFCommissionAmountSaleCurrency', 0)),
                    'total_taxes_already': str(getattr(record_data, 'TotalTaxesAlreadyIncludedinCPNEEquivalentFareWithoutTaxSaleCurrency', 0)),
                    'coupon_taxes_amount': str(getattr(record_data, 'CPNTaxAmountSaleCurrency', 0)),
                    'iata_taxes_amount': str(getattr(record_data, 'IATATaxesAmountInSaleCurrency', 0)),
                    'airline_taxes_amount': str(getattr(record_data, 'AirlineTaxesAmountInSaleCurrency', 0)),
                    'yq_tax_amount': str(getattr(record_data, 'YQ_SALE', 0)),
                    'yr_tax_amount': str(getattr(record_data, 'YR_SALE', 0)),
                    'service_fee_taxes_amount': str(getattr(record_data, 'ServiceFeeTaxesAmountInSaleCurrency', 0)),
                    'issuance_tax_amount': str(getattr(record_data, 'IssuanceTaxesAmountInSaleCurrency', 0)),
                    'total_amount': str(getattr(record_data, 'CPNITransactionTotalAmountCommissionDeductedSaleCurrency', 0)),
                    'total_amount_excl': str(getattr(record_data, 'CPNHNetFareWithoutTaxSaleCurrency', 0)),
                    'coupon_penalty_amount': str(getattr(record_data, 'CPNPenaltyAmountSaleCurrency', 0)),
                    'excess_baggage_weight': str(excess_weight) if excess_weight else '',
                    'excess_baggage_fee_collected': str(excess_fee) if excess_fee else '',
                    'acm': str(getattr(record_data, 'ACMAmountInSaleCurrency', 0)),
                    'adm': str(getattr(record_data, 'ADMAmountInSaleCurrency', 0)),
                    'coupon_mileage': str(getattr(record_data, 'CouponMileage', 0)),
                    'ticket_mileage': str(getattr(record_data, 'TickettotalMileage', 0)),
                    'pnr_of_operating_airline': getattr(record_data, 'TVLOperationRLOC', ''),
                    'designator_of_operating_airline': getattr(record_data, 'TVLOperationAirlineDesignator', ''),
                    'flight_number_on_operating_airline': getattr(record_data, 'TVLOperationFlightNumber', ''),
                    'booking_class_on_operating_airline': getattr(record_data, 'TVLOperationClassCodePRBD', ''),
                    'pnr_of_marketing_airline': getattr(record_data, 'TVLMarketingRLOC', ''),
                    'designator_of_marketing_airline': getattr(record_data, 'TVLMarketingAirlineDesignator', ''),
                    'flight_number_of_marketing_airline': getattr(record_data, 'TVLMarketingFlightNumber', ''),
                    'sales_currency': getattr(record_data, 'MONSaleCurrency', ''),
                    'iata_passenger_type': getattr(record_data, 'TIFIATAPassengerType', ''),
                    'passenger_civility': getattr(record_data, 'TIFPassengerCivility', ''),
                    'passenger_surname': getattr(record_data, 'TIFTravelerSurname', ''),
                    'passenger_first_name': getattr(record_data, 'TIFTravelerFirstName', ''),
                    'datetime_lt_of_issuance': getattr(record_data, 'PTKIssuanceDateAndHourLT', None),
                })
            if all_records:
                self._create_flown_ticket(all_records)
                api_credential.flow_tickets_last_update = fields.Date.today()
        except Exception as e:
            # client.Close()
            print("An error occurred:", e)

    def action_sync_odoo_tickets(self):
        api_credential = self.env['zenith.api.configuration'].search([('active', '=', True)], limit=1)
        if not api_credential:
            raise UserError(_('No active API configuration found.'))
            
        current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        current_date = datetime.now()
        today_date = fields.Date.today()

        url = api_credential.url
        login = api_credential.login
        password = api_credential.password
        air_line_vendor_id = api_credential.air_line_vendor_id
        
        # Get the last update date, default to 30 days ago if not set
        if api_credential.tickets_last_update:
            start_date = api_credential.tickets_last_update
        else:
            start_date = today_date - timedelta(days=30)
        
        # Format dates for API - use today's date for DateLT (fetch all records up to today)
        # We'll filter by start_date on the client side
        end_date_str = today_date.strftime('%Y-%m-%d')
        
        # Create a Zeep client using the WSDL URL
        client = Client(url)

        # Try with date range first, fallback to DateLT if that doesn't work
        request_payload = {
            'request': {
                'POS': {'Source': {'AirlineVendorID': air_line_vendor_id}},
                'Login': login,
                'Password': password,
                'DateLT': end_date_str,  # Fetch all records up to today
                'TimeStamp': current_timestamp,
                'UseWrappedExceptionInFaultException': True
            }
        }

        try:
            # Make the SOAP request using the GetOdooTickets operation
            response = client.service.GetOdooTickets(**request_payload)
            all_records = []
            if not response.Tickets or not response.Tickets.OdooTicket:
                return
            
            # Convert start_date to datetime for comparison if it's a date object
            if isinstance(start_date, date) and not isinstance(start_date, datetime):
                start_date_dt = datetime.combine(start_date, datetime.min.time())
            elif isinstance(start_date, datetime):
                start_date_dt = start_date
            else:
                try:
                    start_date_dt = datetime.strptime(str(start_date), '%Y-%m-%d')
                except:
                    start_date_dt = datetime.combine(fields.Date.from_string(str(start_date)), datetime.min.time())

            # Helper function to get field value from nested object or direct attribute
            def get_field_value(source, field_names, default=''):
                """Try to get field value from nested object or direct attribute"""
                if not source:
                    return default
                for field_name in field_names:
                    try:
                        value = getattr(source, field_name, None)
                        if value is not None and value != '':
                            return value
                    except:
                        continue
                return default
            
            # Debug: Log first record's available attributes (only once)
            import logging
            _logger = logging.getLogger(__name__)
            if response.Tickets and response.Tickets.OdooTicket:
                first_record = response.Tickets.OdooTicket[0]
                try:
                    # Try to get all attributes from the Zeep object
                    available_attrs = [attr for attr in dir(first_record) if not attr.startswith('_')]
                    _logger.info("Available attributes in OdooTicket: %s", available_attrs[:50])  # Log first 50
                except:
                    pass
            
            for record_data in response.Tickets.OdooTicket:
                # Filter records by date - only include records from start_date onwards
                # Use getattr for Zeep objects (not dictionaries)
                export_date = getattr(record_data, 'ExportDateHour', None)
                if export_date:
                    # Convert export_date to datetime for comparison
                    if isinstance(export_date, datetime):
                        export_date_dt = export_date
                    elif isinstance(export_date, str):
                        try:
                            export_date_dt = datetime.strptime(export_date, '%Y-%m-%dT%H:%M:%S')
                        except:
                            try:
                                export_date_dt = datetime.strptime(export_date, '%Y-%m-%d')
                            except:
                                export_date_dt = None
                    else:
                        export_date_dt = None
                    
                    # Skip records before start_date
                    if export_date_dt and export_date_dt < start_date_dt:
                        continue
                
                taxes_list = []
                taxes_string = ''

                # Extract tax information
                taxes = getattr(record_data, 'Taxes', [])
                if taxes:
                    for tax in taxes:
                        tax_name = getattr(tax, 'TaxName', '')
                        tax_amount = getattr(tax, 'Amount', 0)
                        taxes_list.append({
                            'name': tax_name,
                            'amount': tax_amount
                        })
                    # Convert taxes_list to string format for taxes field
                    taxes_string = ', '.join([f"{t['name']}: {t['amount']}" for t in taxes_list])

                # Try to get passenger information - check if it's nested
                passenger_info = getattr(record_data, 'PassengerInfo', None) or getattr(record_data, 'TravelerInfo', None) or getattr(record_data, 'TIF', None)
                flight_info = getattr(record_data, 'FlightInfo', None) or getattr(record_data, 'TravelInfo', None) or getattr(record_data, 'TVL', None)
                
                passenger_name = ''
                if passenger_info:
                    passenger_name = getattr(passenger_info, 'Name', '') or getattr(passenger_info, 'PassengerName', '') or ''
                else:
                    passenger_name = getattr(record_data, 'PassengerName', '') or getattr(record_data, 'TIFTravelerFirstName', '') or ''
                
                passenger_name_parts = passenger_name.split() if passenger_name else []
                passenger_first_name = passenger_name_parts[0] if passenger_name_parts else False
                passenger_surname = ' '.join(passenger_name_parts[1:]) if len(passenger_name_parts) > 1 else False

                all_records.append({
                    'sale_statement_export_id': getattr(record_data, 'ID_SaleStatementAccountingExport', None),
                    'date': getattr(record_data, 'ExportDateHour', None),
                    'name': getattr(record_data, 'RecordStatement', ''),
                    'record_locator': getattr(record_data, 'RecordReferenceNumber', ''),
                    'pnr_zenith': getattr(record_data, 'RCIRLoc', None) or False,
                    'pnr_alphanumeric': getattr(record_data, 'RCIRLoc', None) or False,
                    'heading_st_type': getattr(record_data, 'Heading', ''),
                    'iata_agency_code': getattr(record_data, 'IATAAgencyCode', ''),
                    'point_of_sales': getattr(record_data, 'PointOfSale', ''),
                    'customer': getattr(record_data, 'Customer', ''),
                    'payment_type': getattr(record_data, 'PaymentMode', ''),
                    'balance_sale_currency': getattr(record_data, 'NetFareToPaySaleCurrency', ''),
                    'yq_tax_amount': getattr(record_data, 'YQTaxesSaleCurrency', ''),
                    'yr_tax_amount': getattr(record_data, 'YRTaxesSaleCurrency', ''),
                    'service_fee_tax_amount': getattr(record_data, 'ServiceFeeTaxesAmountInSaleCurrency', ''),
                    'insurance_tax_amount': getattr(record_data, 'InsuranceTaxesAmountInSaleCurrency', '') or '',
                    'other_tax_amount': getattr(record_data, 'OtherTaxesAmountInSaleCurrency', ''),
                    'airline_tax_amount': getattr(record_data, 'AirlineTaxesSaleCurrency', ''),
                    'iata_tax_amount': getattr(record_data, 'IATATaxesAmountInSaleCurrency', ''),
                    'total_tax_amount': getattr(record_data, 'TotaltaxSaleCurrency', ''),
                    'sale_agent': getattr(record_data, 'SaleStatementCreatorName', ''),
                    'original_ticket_number': getattr(record_data, 'IATATicketNumberOriginator', ''),
                    'ticket_number': getattr(record_data, 'IATATicketNumber', ''),
                    'exchanged_ticket_number': getattr(record_data, 'IATATicketNumberExchanged', ''),
                    'customer_id': getattr(record_data, 'CustomerID', ''),
                    'journal_type': getattr(record_data, 'JournalType', '') or '',
                    'taxes_list': str(taxes_list) if taxes_list else '',  # Store as string
                    'taxes': taxes_string,  # Store as formatted string
                    'fair_basis_list': getattr(record_data, 'FareBasisList', ''),
                    'pnr_creator': getattr(record_data, 'PNRCreator', ''),
                    'base_fair': getattr(record_data, 'BaseFareSaleCurrency', '') or '',
                    'sale_statement_status': getattr(record_data, 'SaleStatementStatus', ''),
                    # Passenger information - try nested object first, then TIF prefix, then direct names
                    'iata_passenger_type': get_field_value(passenger_info, ['IATAPassengerType', 'TIFIATAPassengerType']) or getattr(record_data, 'TIFIATAPassengerType', '') or getattr(record_data, 'IATAPassengerType', '') or '',
                    'passenger_civility': get_field_value(passenger_info, ['PassengerCivility', 'Civility', 'TIFPassengerCivility']) or getattr(record_data, 'TIFPassengerCivility', '') or getattr(record_data, 'PassengerCivility', '') or '',
                    'passenger_surname': get_field_value(passenger_info, ['Surname', 'TravelerSurname', 'TIFTravelerSurname']) or getattr(record_data, 'TIFTravelerSurname', '') or passenger_surname or '',
                    'passenger_first_name': get_field_value(passenger_info, ['FirstName', 'TravelerFirstName', 'TIFTravelerFirstName']) or getattr(record_data, 'TIFTravelerFirstName', '') or passenger_first_name or '',
                    'nationality': get_field_value(passenger_info, ['Nationality', 'TIFNationality']) or getattr(record_data, 'TIFNationality', '') or getattr(record_data, 'Nationality', '') or '',
                    'date_of_birth': get_field_value(passenger_info, ['DateOfBirth', 'TIFDateOfBirth'], None) or getattr(record_data, 'TIFDateOfBirth', None) or getattr(record_data, 'DateOfBirth', None),
                    'place_of_birth': get_field_value(passenger_info, ['PlaceOfBirth', 'TIFPlaceOfBirth']) or getattr(record_data, 'TIFPlaceOfBirth', '') or getattr(record_data, 'PlaceOfBirth', '') or '',
                    'passport_number': get_field_value(passenger_info, ['PassportNumber', 'TIFPassportNumber']) or getattr(record_data, 'TIFPassportNumber', '') or getattr(record_data, 'PassportNumber', '') or '',
                    'email_address': get_field_value(passenger_info, ['EmailAddress', 'Email', 'TIFEmailAddress']) or getattr(record_data, 'TIFEmailAddress', '') or getattr(record_data, 'EmailAddress', '') or '',
                    'mobile_number': get_field_value(passenger_info, ['MobileNumber', 'Mobile', 'Phone', 'TIFMobileNumber']) or getattr(record_data, 'TIFMobileNumber', '') or getattr(record_data, 'MobileNumber', '') or '',
                    # Flight information - try nested object first, then TVL prefix, then direct names
                    'flight_number': get_field_value(flight_info, ['FlightNumber', 'TVLFlightNumber']) or getattr(record_data, 'TVLFlightNumber', '') or getattr(record_data, 'FlightNumber', '') or '',
                    'flight_date': get_field_value(flight_info, ['DepartureDateAndHourLT', 'FlightDate', 'TVLDepartureDateAndHourLT'], None) or getattr(record_data, 'TVLDepartureDateAndHourLT', None) or getattr(record_data, 'FlightDate', None),
                    'class_of_service': get_field_value(flight_info, ['CabinClassOfServiceCode', 'ClassOfService', 'TVLCabinClassOfServiceCode']) or getattr(record_data, 'TVLCabinClassOfServiceCode', '') or getattr(record_data, 'ClassOfService', '') or '',
                    'booking_class': get_field_value(flight_info, ['ClassCodePRBD', 'BookingClass', 'TVLClassCodePRBD']) or getattr(record_data, 'TVLClassCodePRBD', '') or getattr(record_data, 'BookingClass', '') or '',
                    'coupon_status': getattr(record_data, 'ID_CPNAeropackStatus', '') or getattr(record_data, 'CouponStatus', '') or getattr(record_data, 'CPNAeropackStatus', '') or '',
                    'aircraft_type': get_field_value(flight_info, ['AircraftType', 'TVLAircraftType']) or getattr(record_data, 'TVLAircraftType', '') or getattr(record_data, 'AircraftType', '') or '',
                    # Financial fields - try various possible field names
                    'commission': getattr(record_data, 'CPNFCommissionAmountSaleCurrency', '') or getattr(record_data, 'CommissionAmountSaleCurrency', '') or getattr(record_data, 'Commission', '') or '',
                    'discount': getattr(record_data, 'DiscountAmountSaleCurrency', '') or getattr(record_data, 'Discount', '') or '',
                    'tour_code_discount': getattr(record_data, 'TourCodeDiscountSaleCurrency', '') or getattr(record_data, 'TourCodeDiscount', '') or '',
                    'adjustment': getattr(record_data, 'AdjustmentAmountSaleCurrency', '') or getattr(record_data, 'Adjustment', '') or '',
                    'penalty': getattr(record_data, 'CPNPenaltyAmountSaleCurrency', '') or getattr(record_data, 'PenaltyAmountSaleCurrency', '') or getattr(record_data, 'Penalty', '') or '',
                    'acm': getattr(record_data, 'ACMAmountInSaleCurrency', '') or getattr(record_data, 'ACMAmountSaleCurrency', '') or getattr(record_data, 'ACM', '') or '',
                    'adm': getattr(record_data, 'ADMAmountInSaleCurrency', '') or getattr(record_data, 'ADMAmountSaleCurrency', '') or getattr(record_data, 'ADM', '') or '',
                    'baggage_supplement': getattr(record_data, 'EBDAmountExcessBagPayedSaleCurrency', '') or getattr(record_data, 'BaggageSupplementAmountSaleCurrency', '') or getattr(record_data, 'BaggageSupplement', '') or '',
                    'baggage_supplement_cancelation': getattr(record_data, 'BaggageSupplementCancellationAmountSaleCurrency', '') or getattr(record_data, 'BaggageSupplementCancellation', '') or '',
                    'tax_a3': taxes_list[0]['amount'] if taxes_list else None,  # Extract tax amount for tax_a3
                    'tax_ac': taxes_list[1]['amount'] if len(taxes_list) > 1 else None,  # Extract tax amount for tax_ac
                    'tax_ae': taxes_list[2]['amount'] if len(taxes_list) > 2 else None,  # Extract tax amount for tax_ae
                })
            if all_records:
                self._create_update_tickets(all_records)
                api_credential.tickets_last_update = fields.Date.today()
            else:
                # Log if no records found
                import logging
                _logger = logging.getLogger(__name__)
                _logger.info("No ticket records found for date range: %s to %s", start_date, today_date)

        except Exception as e:
            # Log the error for debugging
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error syncing Odoo tickets: %s", str(e))
            raise UserError(_('Error syncing tickets: %s') % str(e))

    def _check_customer(self, client_id, name=''):
        # Check if a customer with the given ID already exists
        res_ob = self.env['res.partner'].sudo()
        customer = res_ob.search([('client_id', '=', client_id)], limit=1)
        if not customer:
            # Create a new customer with the provided ID and values
            customer = res_ob.create({
                'client_id': client_id,
                'name': name or client_id
            })
        return customer.id


    def _create_or_update_records(self, model_name, id_field, all_records):
        try:
            # Extract ids from all_records
            ids = [record_data[id_field] for record_data in all_records]

            # Search for existing records based on id_field
            existing_records = self.env[model_name].sudo().search([(id_field, 'in', ids)])

            # Create dictionaries to hold records for update and creation
            records_to_update = {}
            records_to_create = []

            # Populate dictionaries based on existing records
            for existing_record in existing_records:
                records_to_update[getattr(existing_record, id_field)] = existing_record

            # Separate records for update and creation
            for record_data in all_records:
                if record_data[id_field] in records_to_update:
                    records_to_update[record_data[id_field]].write(record_data)
                else:
                    records_to_create.append(record_data)

            # Create new records
            if records_to_create:
                self.env[model_name].sudo().create(records_to_create)

        except Exception as e:
            print(f"An error occurred while processing {model_name}: {e}")


    def _create_credit_limits(self, all_records):
        self._create_or_update_records('credit.limit', 'cash_statement_id', all_records)


    def _create_update_tickets(self, all_records):
        self._create_or_update_records('ticket.transaction', 'sale_statement_export_id', all_records)


    def _create_flown_ticket(self, all_records):
        self._create_or_update_records('flown.ticket', 'export_id', all_records)