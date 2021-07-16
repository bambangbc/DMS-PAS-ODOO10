# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782

{
    'name': 'Reporting for PAS',
    'version': '10.0.0.1.0',
    'category': 'Reporting',
    'author': 'Ibrohim Binladin | +6283871909782 | ibradiiin@gmail.com',
    'website': 'http://ibrohimbinladin.wordpress.com',
    'depends':[
        'base',
        'sale',
        'jasper_reports',
        'maintenance',
        'pelita_equipment',
        'pelita_master_data',
        'pelita_sale',
        'ib_base_pelita',
    ],
    'description': """
Custom Report Created By Ibrahim Binladin
=====================================================
* List of Sale Order Line, exported from sale order line and made Excel file.
* Single Report - Sales Order to attach in email.
* Operational Reporting (Data Jam Terbang,Test Flight, etc)
""",
    'demo': [],
    'test': [],
    'data':[
        'views/reports.xml',
        'data/mail_template_data.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_report_view.xml',
        'views/view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
