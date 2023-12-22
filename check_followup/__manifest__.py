{
    'name': 'Check Followup (PDC)',
    'version': '12.0',
    'author': 'Abdelwhab',
    'data': [
        'security/ir.model.access.csv',
        'views/check_followup_view.xml',
        'views/journal_view.xml',
        'views/payment_view.xml',
        'reports/check_report.xml',
        'wizard/change_bank_view.xml',

    ],
    'depends': ['account','payment'],

    'installable': True,
    'application': True,
}
