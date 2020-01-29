# -*- coding: utf-8 -*-


from odoo import http
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class WebsiteDesigner(http.Controller):
    @http.route('/builder/designer', type='http', auth="user", website=True)
    def designer(self, model, res_id, field, return_url=None, **kw):
        if not model or not model in request.env or not res_id:
            return request.redirect('/')
        model_fields = request.env[model]._fields

        if not field or not field in model_fields:
            return request.redirect('/')

        res_id = int(res_id)
        obj_ids = request.env[model].browse([res_id])
        if not obj_ids:
            return request.redirect('/')
        # try to find fields to display / edit -> as t-field is static, we have to limit
        # cr, uid, context = request.cr, request.uid, request.context
        record = request.env[model].browse([id])
        model_name = request.env[model]._description

        values = {
            'record': record,
            'templates': None,
            'model': model,
            'model_name': model_name,
            'res_id': res_id,
            'field': field,
            'return_url': return_url,
        }

        return request.render("builder.designer", values)

    @http.route(['/builder/page/designer'], type='http', auth="user", website=True)
    def index(self, model, res_id, enable_editor=1, **kw):
        if not model or not model in request.env or not res_id:
            return request.redirect('/')
        model_fields = request.env[model]._fields
        res_id = int(res_id)
        obj_ids = request.env[model].browse([res_id])
        if not obj_ids:
            return request.redirect('/')
        # try to find fields to display / edit -> as t-field is static, we have to limit
        # cr, uid, context = request.cr, request.uid, request.context
        record = request.env[model].browse([res_id])
        _logger.debug(record)
        return_url = '/web#return_label=Website&model={model}&id={id}&view_type=form'.format(model=model, id=record.id)
        if model == 'builder.ir.module.module':
            field_template = 'builder.page_designer_builder_ir_module_module_description_html'
        elif model == 'builder.website.page':
            field_template = 'builder.page_designer_builder_website_page_content'
        elif model == 'builder.website.snippet':
            field_template = 'builder.page_designer_builder_website_snippet_content'
        else:
            return request.redirect('/')

        values = {
            'record': record,
            'model': model,
            'res_id': res_id,
            'returnUrl': return_url,
            'field_template': field_template
        }

        return request.render("builder.page_designer", values)
        # return request.render("builder.page_designer", {})


    @http.route(['/builder/page/snippets'], type='json', auth="user", website=True)
    def snippets(self):
        return request.render('builder.page_designer_snippets',{})
