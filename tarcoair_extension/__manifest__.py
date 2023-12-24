# -*- coding: utf-8 -*-

{
    "name": "Tarcoair Extension",
    "version": "1.6",
    "depends": [
        'base', 'account', 'contacts','analytic'
    ],
    'data': [
        'security/security_view.xml',
        'view/partner_category_views.xml',
        'view/res_users.xml',
        'view/res_company.xml',
        # 'view/customer_vendor_view.xml',
    ],
    "author": "SGT",
    "category": "Accounting",
    "installable": True,
    "auto_install": False,
    "application": True,
}
