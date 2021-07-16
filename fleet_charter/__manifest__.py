# -*- coding: utf-8 -*-

{
    'name': 'Aircraft Charter Management',
    'version': '10.0.3.1.0',
    'summary': "Pelita Air Service Management: Contracts, Charter, Invoice",

    'description': """
==============================================================================================
 The Module Helps You To Manage Charter Contracts, Setup Aircraft, Charter Booking, & Invoice
==============================================================================================
    """,
    'category': "Industries",
    'author': 'Alfie Qashwa',
    'depends': ['base', 'account', 'fleet', 'maintenance', 'hr_maintenance','mail'],
    'data': ['security/charter_security.xml',
             'security/ir.model.access.csv',
             'views/craft_charter_view.xml',
             'views/checklist_view.xml',
             'views/craft_tools_view.xml',
             'reports/charter_report.xml',
    ],
    'images': ['static/description/banner.png'],

    'installable': True,
    'application': True,
}
