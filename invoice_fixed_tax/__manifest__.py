# -*- coding: utf-8 -*-
{
    'name': 'Invoice Fixed Amount Tax',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Invoice with fixed amount taxes shown as journal items',
    'description': """
Invoice Fixed Amount Tax Module
================================
This module allows you to:
* Add fixed amount taxes to invoice lines as a float field
* Automatically create journal entries (journal items) for fixed taxes
* View fixed taxes in Journal Voucher (JV)

Features:
---------
* Fixed tax amount field on invoice lines
* Automatic journal entry creation for fixed taxes
* Fixed taxes displayed as separate journal items in JV
* Support for multiple fixed taxes per invoice line
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/account_move_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

