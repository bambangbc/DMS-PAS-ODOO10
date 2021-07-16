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
    'name': 'Flight Operations [PAS]',
    'version': '10.0.0.1.0',
    'category': 'Productivity',
    'summary': 'Flight Service Operations Module for Pelita Air Service',
    'author': 'PT. Gemilang Inti Teknologi Sistem',
    'website': 'http://www.gemilangits.com',
    'depends': [
        'base',
        'hr',
        'pelita_master_data',
        'web_map',
    ],
    'contributors': [
        'Mohamad Taufik <mohamad.taufik2008@gmail.com>',
        'Ibrohim Binladin <ibradiiin@gmail.com>',
    ],
    'description': """
Basic Flight Service Module for PAS Operations
=====================================================
* Office Duty
* Flight Schedule, Schedule Type, Route Flight Operations, HR.Crew, Flight Attendant
* Base Operation, Area Operation, Regulation, Flight Hours Price, Routes, Duty Time
* Flight Maintenance Log, FML Lines (Rotary and Fixed Wing) 
* Flight Requisition


Contributors :
=====================================================
* Mohamad Taufik <mohamad.taufik2008@gmail.com>
* Ibrohim Binladin <ibradiiin@gmail.com>

""",
    'demo': [],
    'test': [],
    'data': [
        'data/ir_sequence_data.xml',
        'data/sequence.xml',
        'security/operation_group.xml',
        'security/ir.model.access.csv',
        'views/operation_data_views.xml',
        'views/operation_schedule_views.xml',
        'views/flight_maintenance_log_views.xml',
        'views/office_duty_views.xml',
        'views/flight_requisition_views.xml',
        'wizard/flt_schedule_approve_crew.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
