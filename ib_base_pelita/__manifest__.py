# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782

{
    'name': 'Custom Modules',
    'version': '10.0.0.1.0',
    'category': 'Productivity',
    'summary': 'Advance of a module by Ibrohim Binladin',
    'description': """
Custom Module : 
=====================================================
* Sale Division, Sales Area, Transaction Type, Disc.Channel, Business Unit PAS, etc.
* Custom view and form in Sale Order Form
* Support Other Modules, such as Operational, Fleet, iCrew, etc.
* Contract and Analytic in Sales
""",
    'demo': [],
    'test': [],
    'depends': [
        'base',
        'sale',
        'hr',
        'contract',
        'eofice', 
        'project',
        'sales_team',
        'maintenance',
        'pelita_equipment',
        'pelita_master_data',
        'pelita_sale',
        'sales_team',
        'pelita_crew',
        # 'partner_pelita',
        'pelita_operation',
        'web_widget_color',
    ],
    'author': 'Ibrohim Binladin | +6283871909782 | ibradiiin@gmail.com',
    'website': 'http://ibrohimbinladin.wordpress.com',
    'data': [
        'data/ir_sequence_data.xml',
        'data/master_data.xml',
        'security/res_groups_pelita.xml',
        'security/rules.xml',
        'security/ir.model.access.csv',
        'wizard/flight_info_view.xml',
        'wizard/air_service_info_view.xml',
        'wizard/update_logs_view.xml',
        'views/invisible.xml',
        'views/view.xml',
        'views/sale_view.xml',
        'views/menu.xml',
        'views/user_view.xml',
        'views/business_unit.xml',
        'views/partner_view.xml',
        'views/analytic_account.xml',
        'views/account_invoice.xml',
        'views/project_view.xml',
        # 'views/res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
