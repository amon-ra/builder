# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Module Builder',
    'version': '13.0.1.0.0',
    'category': 'Programming',
    'summary': 'Build your modules right inside Odoo',
    'description': """
This module aims to help in the development of new modules
=======================================================================================

""",
    'author': 'Soluciones Moebius, Oondeo C.B.',
    #"license": "AGPL-3",
    'website': 'https://www.oondeo.es/',
    'depends': ['web', 'web_diagram', 'website'], #software
    'data': [
        # 'security/base_security.xml',
        'security/ir.model.access.csv',

        'data/oe.css.classes.xml',
        'wizard/module_generate_view.xml',
        'wizard/model_lookup_wizard_view.xml',
        'wizard/menu_lookup_wizard_view.xml',
        'wizard/action_lookup_wizard_view.xml',
        'wizard/website_asset_bulk_add_view.xml',
        'wizard/website_media_item_bulk_add_view.xml',
        'wizard/website_page_import_view.xml',
        'wizard/model_access_generate_wizard_view.xml',
        'wizard/demo_creator_wizard_view.xml',

        'views/views/base_view.xml',
        'views/views/calendar_view.xml',
        'views/views/form_view.xml',
        'views/views/gantt_view.xml',
        'views/views/graph_view.xml',
        'views/views/kanban_view.xml',
        'views/views/search_view.xml',
        'views/views/tree_view.xml',
        'views/views/selector_view.xml',
        'views/website_view.xml',

        'views/demo/char_views.xml',
        'views/demo/name_views.xml',
        'views/demo/email_views.xml',
        'views/demo/autoincrement_views.xml',
        'views/demo/selection_views.xml',
        'views/demo/normal_views.xml',
        'views/demo/custom_list_views.xml',
        'views/demo/m2o_views.xml',
        'views/demo/m2m_views.xml',
        'views/demo/date_views.xml',
        'views/demo/binary_views.xml',

        'wizard/module_data_import_view.xml',
        'wizard/module_import_view.xml',
        'wizard/module_export_view.xml',
        'wizard/model_import_view.xml',
        'wizard/group_import_view.xml',

        'views/menu_view.xml',
        'views/module_view.xml',
        'views/field_view.xml',
        'views/model_view.xml',
        'views/res_config_model_view.xml',
        'views/action_view.xml',
        'views/data_view.xml',
        'views/security_view.xml',
        'views/cron_view.xml',
        # 'views/workflow_view.xml',
        'views/menu.xml',

        'views/backend_assets.xml',
        'views/snippet_templates.xml',
        'views/designer/website_page_designer.xml',
        'views/designer/designer_snippets.xml',

    ],
    # 'test': [
    #     'test/test_demo.yml',
    # ],
    'images': [
        'static/description/module_info.png',
        'static/description/designer.png',
    ],
    #'qweb': [],
     # 'qweb': ['static/src/xml/templates.xml'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}
