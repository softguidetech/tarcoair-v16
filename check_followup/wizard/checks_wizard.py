# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ChecksWizard(models.TransientModel):
    _name = "checks.wizard"
    _description = "Check wizard"

    partner = fields.Char(string='Partner')
    check_date = fields.Date(string='Check Date')
    amount = fields.Float(readonly=1,string='A/C Reg')
    amount_text = fields.Text(readonly=1,string='A/C Reg')

    def check_report(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'partner': context.get(partner_id),
                'date_end': self.date_end,
                'ac_reg': self.ac_reg.name,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `get_report_values()` and pass `data` automatically.
        return self.env.ref('fuel_department.static_report_fuel').report_action(self, data=data)

class FuelReport(models.AbstractModel):
    _name = 'report.fuel_department.report_fuel'

    @api.model
    def get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        ac_reg = data['form']['ac_reg']
        sales_records = []
        if not self.flight_number:
            docs = self.env['health.info'].search([('f_date', '>=', date_start), ('f_date', '<=', date_end)])
        if self.date_start:
            docs = self.env['health.info'].search([('f_date', '>=', date_start), ('f_date', '<=', date_end),
                                                   ('flight_number', '=', self.flight_number)])
        if docs.date_start and docs.date_end:
            for order in docs:
                if parse(docs.date_start) <= parse(order.f_date) and parse(docs.date_end) >= parse(order.f_date):
                    sales_records.append(order)
        if docs.date_start and docs.date_end:
                for order in docs:
                        if parse(docs.date_start) <= parse(order.f_date) and parse(docs.date_end) >= parse(                            order.f_date) and parse(
                            docs.flight_number) == parse(order.flight_number):
                                sales_records.append(order)

                        else:
                            raise UserError("Please enter duration")


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'ac_reg': ac_reg,
            'docs': docs,
        }
