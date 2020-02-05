from collections import defaultdict
import base64,os

from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

class GeneratorV11(models.TransientModel):
    """
    Their job is to generate code.
    """
    _name = 'builder.generator.v11'
    _inherit = ['builder.generator.base']
    _description = '11.0'

    @api.model
    def get_template_paths(self):
        return [os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'templates', '11.0'))]

    @api.model
    def generate_module(self, zip_file, module):

        has_models = any(model.define for model in module.model_ids)
        module_data = []
        py_packages = {}
        demo_data = []
        # model_packages = []
        _logger.debug(has_models)
        for model in module.model_ids:
            _logger.debug(model)
        if len(module.rule_ids) or len(module.group_ids):
            module_data.append('security/security.xml')
            zip_file.write_template(
                'security/security.xml',
                'security/security.xml.jinja2', {
                    'module': module,
                    'rules': module.rule_ids,
                    'groups': module.group_ids,
                })

        if len(module.model_access_ids):
            module_data.append('security/ir.model.access.csv')
            zip_file.write_template(
                'security/ir.model.access.csv',
                'security/ir.model.access.csv.jinja2', {
                    'module': module,
                    'model_access': module.model_access_ids,
                })

        if module.view_ids:
            for model in module.model_ids:
                filename = 'views/{model}_views.xml'.format(
                        model=model.model.lower().replace('.', '_'))
                module_data.append(filename)
                zip_file.write_template(
                    filename,
                    'views/views.xml.jinja2',
                    {
                        'module': model.module_id,
                        'views': model.view_ids,
                        'actions': model.action_ids,
                        'menus': model.menu_ids
                    }
                )

        actions = module.action_window_ids.filtered(lambda r: not r.model_id)
        menus = module.action_window_ids.filtered(lambda r: not r.model_id)
        filename = 'views/{model}_views.xml'.format(
                        model=module.name.lower().replace('.', '_'))

        if actions or menus:       
            module_data.append(filename)
            zip_file.write_template(
                filename,
                'views/views.xml.jinja2',
                {
                    'module': module.id,
                    'views': [],
                    'actions': actions,
                    'menus': menus
                }
            )            
        #     zip_file.write_template(
        #         'views/actions.xml',
        #         'views/actions.xml.jinja2',
        #         {'module': module}
        #     )
        # if module.action_window_ids:
        #     module_data.append('views/actions.xml')
        #     zip_file.write_template(
        #         'views/actions.xml',
        #         'views/actions.xml.jinja2',
        #         {'module': module}
        #     )

        # if module.menu_ids:
        #     module_data.append('views/menu.xml')
        #     zip_file.write_template(
        #         'views/menu.xml',
        #         'views/menus.xml.jinja2',
        #         {'module': module, 'menus': module.menu_ids}
        #     )

        if has_models:
            # py_packages.append('models')
            # model_packages.append('models')

            # zip_file.write_template(
            #     'models/models.py',
            #     'models/models.py.jinja2',
            #     {'module': module,  'models': [
            #         model for model in module.model_ids if model.define]}
            # )

            for model in module.model_ids:
                if model.define:
                    m = model.model.lower().replace('.', '_')
                    _logger.debug(m)
                    py_packages['models']=py_packages.get('models',[])+[m]
                    filename = 'models/{model}.py'.format(model=m)
                    zip_file.write_template(
                        filename,
                        'models/models.py.jinja2',
                        {'module': module,  'models': [model]}
                    )

        _logger.debug(py_packages)
        for model in module.model_ids:
            if not model.demo_records:
                continue

            filename = 'demo/{model}_demo.xml'.format(model=model.model.lower().replace('.', '_'))
            demo_data.append(filename)
            zip_file.write_template(
                filename,
                'demo/model_demo.xml.jinja2',
                {
                    'module': module,
                    'model': model,
                    'records': model.demo_records
                }
            )

        if len(module.cron_job_ids):
            module_data.append('data/cron.xml')
            zip_file.write_template(
                'data/cron.xml',
                'data/cron.xml.jinja2', {
                    'module': module,
                    'cron_jobs': module.cron_job_ids,
                })

        # if len(module.workflow_ids):
        #     module_data.append('data/workflow.xml')
        #     zip_file.write_template(
        #         'data/workflow.xml',
        #         'data/workflow.xml.jinja2', {
        #             'module': module,
        #             'workflows': module.workflow_ids,
        #         })

        if len(module.backend_asset_ids):
            module_data.append('views/assets.xml')
            zip_file.write_template(
                'views/assets.xml',
                'views/web_assets.xml.jinja2', {
                    'module': module,
                    'assets': module.backend_asset_ids,
                })

        if len(module.setting_ids):
            module_data.append('views/settings.xml')
            zip_file.write_template(
                'views/settings.xml',
                'views/settings.xml.jinja2', {
                    'module': module,
                    'settings': module.setting_ids,
                })

            # model_packages.append('settings')
            py_packages['models']=py_packages.get('models',[])+['settings']
            zip_file.write_template(
                'models/settings.py',
                'models/settings.py.jinja2', {
                    'module': module,
                    'settings': module.setting_ids,
                })

        if module.icon_image:
            zip_file.write(
                'static/description/icon.png',
                base64.decodestring(module.icon_image)
            )

        if module.description_html:
            zip_file.write(
                'static/description/index.html',
                module.description_html
            )

        # website stuff
        for data in module.data_file_ids:
            zip_file.write(
                data.path.strip('/'),
                base64.decodestring(data.content)
            )

        for theme in module.website_theme_ids:
            if theme.image:
                zip_file.write(
                    'static/themes/' + theme.asset_id.attr_id + '.png',
                    base64.decodestring(theme.image)
                )

        if module.website_asset_ids:
            module_data.append('views/website_assets.xml')
            zip_file.write_template(
                'views/website_assets.xml',
                'views/website_assets.xml.jinja2',
                {'module': module, 'assets': module.website_asset_ids},
            )

        if module.website_page_ids:
            module_data.append('views/website_pages.xml')
            zip_file.write_template(
                'views/website_pages.xml',
                'views/website_pages.xml.jinja2',
                {'module': module, 'pages': module.website_page_ids, 'menus': module.website_menu_ids},
            )

        for controller in module.website_controller_ids:
            routes = {}
            parameters = {}
            for method in controller.controller_method_ids:
                parameters[method.name]=parameters.get(method.name,'')
                parameters[method.name]+=','+'auth='+method.visibility
                parameters[method.name]+=','+'type='+method.route_type
                if method.route_method_ids:
                    parameters[method.name]+=','+'methods=['+','.join(
                        [m.name for m in method.route_method_ids])
                if not method.csrf:
                    parameters[method.name]+=','+'csrf=False'
                for route in method.controller_route:
                    routes[method.name]=route.get(
                        method.name,'')+route.name+route.parameters+','                        
                    # parameters[method.name]=parameters.get(
                    #     method.name,'self')
                    # for p in route.parameter_ids:
                    #     if p.name == '**kwargs':
                    #         # parameters='self'
                    #         break
                    #     else:
                    #         parameters+=', '+p.name+'='+p.default                        
            zip_file.write_template(
                'controllers/main.py',
                'controllers/main.py.jinja2',
                {'module': module, 'controller': controller,
                'controller_routes': routes, 'route_parameters': parameters,
                },
            )            

        for f in module.python_file_ids:
            py_packages[f.parent]=py_packages.get(f.parent,
                [])+[f.name]
            filename = '{}/{}.py'.format(f.parent,f.name)
            zip_file.write_template(
                filename,
                'python_file.py.jinja2',
                {'module': module, 'code': f},
            )              

        _logger.debug(py_packages)
        for key, value in py_packages.items():
            _logger.debug(key)
            _logger.debug(value)
            if value:
                zip_file.write_template(
                    key+'/__init__.py',
                    '__init__.py.jinja2',
                    {'packages': value,'module': module}
                )                




        if module.website_theme_ids:
            module_data.append('views/website_themes.xml')
            zip_file.write_template(
                'views/website_themes.xml',
                'views/website_themes.xml.jinja2',
                {'module': module, 'themes': module.website_theme_ids},
            )
        if module.website_media_item_ids:
            module_data.append('views/website_images.xml')
            zip_file.write_template(
                'views/website_images.xml',
                'views/website_images.xml.jinja2',
                {'module': module, 'images': module.website_media_item_ids},
            )

        if module.website_snippet_ids:
            snippet_type = defaultdict(list)
            for snippet in module.website_snippet_ids:
                snippet_type[snippet.is_custom_category].append(snippet)

            module_data.append('views/website_snippets.xml')
            zip_file.write_template(
                'views/website_snippets.xml',
                'views/website_snippets.xml.jinja2',
                {'module': module, 'snippet_type': snippet_type},
            )

        # if model_packages:
        #     zip_file.write_template(
        #         'models/__init__.py',
        #         '__init__.py.jinja2',
        #         {'module': module,'packages': model_packages}
        #     )

        zip_file.write_template(
            '__init__.py',
            '__init__.py.jinja2',
            {'module': module,'packages': list(py_packages.keys())}
        )

        # end website stuff

        # this must be last to include all resources
        zip_file.write_template(
            '__manifest__.py',
            '__manifest__.py.jinja2',
            {
                'module': module,
                'data': module_data,
                'demo': demo_data
            }
        )
