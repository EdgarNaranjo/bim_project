# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2020 Todooweb
#    (<http://www.todooweb.com>).
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
    'name': 'BIM Construction',
    'version': '15.0.0.1.0',
    'category': 'Project Management',
    'summary': """BIM Project Construction.""",
    'description': """BIM Project Construction: Quotations, Bill of Materials, Projects, Workspaces.""",
    'license': 'AGPL-3',
    'author': "Todooweb (www.todooweb.com)",
    'website': "https://todooweb.com/",
    'contributors': [
        "Equipo Dev <devtodoo@gmail.com>",
        "Edgar Naranjo <edgarnaranjof@gmail.com>",
    ],
    'support': 'devtodoo@gmail.com',
    'depends': [
        'web',
        'sale_management',
        'project',
        'sale_project',
        'calendar',
        'stock',
        'purchase',
        'hr_timesheet',
        'documents',
        'note',
        'board',
        # 'planning',
    ],
    'data': [
        # 'views/res_groups_views.xml',
        'views/bim_project_view.xml',
        'views/mail_activity_views.xml',
        #'views/ir_actions_act_window_views.xml',
        #'views/ir_actions_actions_views.xml',
        #'views/ir_actions_report_views.xml',
        #'views/ir_actions_server_views.xml',
        #'views/ir_attachment_views.xml',
        #'views/ir_default_views.xml',
        #'views/ir_model_access_views.xml',
        #'views/ir_model_constraint_views.xml',
        #'views/ir_model_fields_views.xml',
        #'views/ir_ui_menu_views.xml',
        #'views/ir_ui_view_views.xml',
    ],
    #'images': ['static/description/screenshot_lang.png'],
    #'live_test_url': 'https://youtu.be/JPcVxHTeJzI',
    'installable': True,
    'auto_install': False,
    'application': True,
    #'price': 5.99,
    #'currency': 'EUR',
}
