{
    'name': 'Zenith Integration',
    'version': '16.0.1.0.0',
    'summary': 'Integration with Zenith',
    'description': """
        This module integrates with Zenith.
    """,
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        # 'wizard/zenith_sync_wizard_view.xml',
        # 'view/zenith_integration_view.xml',
        # 'view/transaction_type_view.xml',
        # 'view/transaction_classification_view.xml',
        # 'view/menu_items_view.xml',
        # 'view/zenith_invoice_view.xml',
        'view/ticket_transaction_view.xml',
        'view/flown_ticket_view.xml',
        'view/credit_limit_view.xml',
        'view/api_configuration.xml',
        'view/res_partner.xml',
        'view/account_move_view.xml',
        'view/res_company_view.xml',
        'data/sync_cron_job.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'icon': '/static/description/icon.jpg',

}
