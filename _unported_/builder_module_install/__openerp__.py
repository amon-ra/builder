# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Soluciones Moebius (<http://www.solucionesmoebius.com>).
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

# noinspection PyStatementEffect
{
    'name': 'Module Builder Install',
    'version': '0.1',
    'category': 'Programming',
    'summary': 'Build your modules right inside Odoo',
    'description': """
Module Builder Install
=======================================================================================

""",
    'author': 'Soluciones Moebius',
    "license": "AGPL-3",
    'website': 'http://www.solucionesmoebius.com/',
    'depends': ['builder', 'base_import_module'],
    'data': [
        'views/view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}