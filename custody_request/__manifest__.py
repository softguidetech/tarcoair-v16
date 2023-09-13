{
    'name': 'Custody Request',
    'version': '1.0',
    'author': 'Abdelwhab',
    'data': [

        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/custody_request_view.xml',
        'views/configure_view.xml',
        'reports/custody_report.xml',
    ],
    'depends': ['base','hr','account','hr_payroll_community','analytic', 'check_followup'],




    'installable': True,
    'application': True,






}
