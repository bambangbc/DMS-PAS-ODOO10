# -*- coding: utf-8 -*-
{
    'name': "Pelita Sale",
    'category': 'Uncategorized',
    'version': '0.1',
    'summary': """
                Customization Pelita Air Services Sales
             """,

    'description': """ 
        This module extend Sales Apps for Pelita Air Service Purposes """,

    'author': "Alfie Qashwa",
    'website': "https://github.com/alfieqashwa",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
   

    # any module necessary for this one to work correctly
    'depends': ['sale',
               'crm',
               #'pelita_fleet',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/view.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    
    #'demo': [
    #   'demo/demo.xml',
    #],
    'installable': True,
    'auto_install': False,
}
