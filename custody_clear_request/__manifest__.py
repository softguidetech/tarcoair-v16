{
    'name': 'Custody Clear Request',
    'version': '1.0',
    'author': 'Abdelwhab Alim',
    'data': [

        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/custody_clear_request_view.xml',
        # 'views/configure_view.xml',
        'reports/custody_report.xml',
    ],
    'depends': ['base','hr','account','hr_payroll_community','analytic','custody_request'],




    'installable': True,
    'application': True,






}
