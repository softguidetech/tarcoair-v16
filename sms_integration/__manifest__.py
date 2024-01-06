{
    'name': 'Custom SMS Templates',
    'version': '16.0',
    'depends': ['base','account'],
    'data': [
        'security/ir.model.access.csv',
        # 'view/twilio_config_view.xml',
        'view/account_move.xml',
        'view/sms_template.xml',
        'view/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
