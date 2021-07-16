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
    'name': 'Crew [PAS]',
    'version': '10.0.0.1.0',
    'category': 'Employees',
    'author': 'PT. Gemilang Inti Teknologi Sistem',
    'website': 'http://www.gemilangits.com',
    'description': """
Module for Crew Pelita Air Services
=====================================================
* iCrew (hr.employee), hr.cv, hr.qualification
* Flying Hours, Crew Duty Time
* Documents : Education, Training, Carrier, 
* Rating Qualification, Pilot Categ, Crew Categ 


Contributors :
=====================================================
* Mohamad Taufik <mohamad.taufik2008@gmail.com>
* Ibrohim Binladin <ibradiiin@gmail.com>

""",
    'contributors': [
        'Mohamad Taufik <mohamad.taufik2008@gmail.com>',
        'Ibrohim Binladin <ibradiiin@gmail.com>',
    ],
    'summary': 'Crew [Pelita Air Services]',
    'depends': ['base','hr','pelita_operation'],
    'demo': [],
    'test': [],
    'data': [
        'security/crew_group.xml',
        'security/ir.model.access.csv',
        'views/pelita_crew_views.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
