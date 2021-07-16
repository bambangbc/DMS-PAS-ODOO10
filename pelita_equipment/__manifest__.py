# -*- coding: utf-8 -*-
{
    'name': "pelita_equipment",

    'summary': """
                Customization Pelita Air Services Equipment
        """,

    'description': """
=====================================================================
 This module extend Maintenance Apps for Pelita Air Service Purposes
=====================================================================
    """,

    'author': "Alfie Qashwa",
    'website': "https://github.com/alfieqashwa",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'maintenance',
        'pelita_master_data',
    ],
    'data': ['views/views.xml'],
    'installable': True,
    'auto_install': False,
}