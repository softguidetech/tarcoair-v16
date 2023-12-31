{
    'name': 'Cash Vouchers',
    'version': '1.0',
    'author': 'Hany Bageeg',
    'data': [

        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/partner_category_views.xml',
        'views/res_partner.xml',
        'views/cash_voucher_view.xml',
        'views/check_voucher_view.xml',
        'views/request_inbound_view.xml',
        'views/check_inbound_view.xml',
        'reports/check_printing.xml',

        'reports/cash_report.xml',
        'reports/check_report.xml',
        'reports/inbound_report.xml',
        'reports/check_inbound_report.xml',
    ],
    'depends': ['base','account','analytic', 'contacts', 'check_followup','payment'],




    'installable': True,
    'application': True,






}
