# -*- coding: utf-8 -*-
{
    'name': "Basic Partner Extension Module",
    'version': '10.0.0.1.0',
    'category': 'Productivity',
    'summary': 'Extend Partner Module for Pelita Operations Application',
    'author': 'PT. Gemilang Inti Teknologi Sistem',
    'website': 'http://www.gemilangits.com',
    'depends': [
        'base',
        'sale',
        'account',
        'ib_base_pelita',
    ],
    'contributors': [
        'Alfie Qashwa [https://github.com/alfieqashwa]',
        'Ibrohim Binladin <ibradiiin@gmail.com>',
    ],
    'description': """
Custom Module : 
=====================================================
* Inherit : Sale Division, Sales Area, Transaction Type, Disc.Channel, Business Unit PAS, etc into ResPartner.
* Custom view in Partner Form
* Inherit Master Data (Partner) into Sales Form

Contributors :
=====================================================
* Alfie Qashwa [https://github.com/alfieqashwa]
* Ibrohim Binladin <ibradiiin@gmail.com>
""",
    'demo': [],
    'test': [],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/master_data.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}