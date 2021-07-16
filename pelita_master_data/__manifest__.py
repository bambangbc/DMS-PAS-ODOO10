# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2017 PT. Gemilang Inti Teknologi Sistem
#    (<http://www.www.gemilangits.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Fleet Management [PAS]',
    'version': '10.0.0.1.0',
    'category': 'Productivity',
    'author': 'PT. Gemilang Inti Teknologi Sistem',
    'website': 'http://www.gemilangits.com',
    'description': """
Module for Fleet Management Pelita Air Services
=====================================================
* Aircraft, Aircraft Acquisition, Aircraft Category, Engine Type, Propeller Type, Documents
* Fleet Administration, Fleet Performance
* Document Certificate, Engine Spare


Contributors :
=====================================================
* Mohamad Taufik <mohamad.taufik2008@gmail.com>
* Ibrohim Binladin <ibradiiin@gmail.com>

""",
    'summary': 'Master Data Pelita Air Services',
    'depends': ['base'],
    'contributors': [
        'Mohamad Taufik <mohamad.taufik2008@gmail.com>',
        'Ibrohim Binladin <ibradiiin@gmail.com>',
    ],
    'demo': [],
    'test': [],
    'data': [
        'views/master_aircraft_views.xml',
        'views/aircraft_acquisition_views.xml',
        'views/fleet_performance_views.xml',
        'views/fleet_administration_views.xml',
        'security/pelita_fleet_group.xml',
        'security/ir.model.access.csv'
        
    ],
    'css': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
