# -*- coding: utf-8 -*-
{
    "name": "Airline Invoice",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "summary": "Airline Invoice (Customer Invoice) with ticket/passenger fields",
    "depends": ["account"],
    "data": [
        "views/airline_invoice_menus.xml",
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/report_invoice_views.xml",
        "report/airline_invoice_report.xml",
        "report/airline_invoice_templates.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}


