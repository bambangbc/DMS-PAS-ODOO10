# -*- coding: utf-8 -*-
##############################################################################
#
#    Auto reset sequence by year,month,day
#    Copyright 2013 wangbuke <wangbuke@gmail.com>
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
    'name': 'ir_sequence_autoreset',
    'version': '0.1',
    'category' : 'Others',
    'description': """
AUTO RESET PER MONTH

""",
    'author': 'bambang bagus candra',
    'website': '',
    'depends': ['base'],
    'data': [
           'view/ir_sequence.xml',
           'data/data.xml',
    ],
    'installable': True,
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
