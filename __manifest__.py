{
    'name': "Helpdesk",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'mail'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        # 'security/record_rule.xml',

        'views/tickets.xml',

        'views/user_form.xml',
        'views/my_tasks.xml',
        'views/service_type.xml',

    ],
    'demo': [],
    'summary': "logic_tickets",
    'description': "this_is_my_app",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': False
}
