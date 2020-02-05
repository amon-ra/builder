from lxml import html
import lxml.etree as etree
__author__ = 'one'

from odoo import models, api, fields, _


class PageImport(models.TransientModel):
    _name = 'builder.website.page.import.wizard'

    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='CASCADE')
    page_ids = fields.Many2many('ir.ui.view', 'builder_website_page_import_wizard_rel', 'wizard_id', 'view_id', 'Pages', domain="[('type', '=', 'qweb'), ('page_ids', '!=', ())]")
    include_menu = fields.Boolean('Include Menu', default=True)

    def action_import(self):
      for record_id in self:
        # asset = self.env[self.env.context.get('active_model')].search([('id', '=', self.env.context.get('active_id'))])
        page_item_model = self.env['builder.website.page']
        menu_item_model = self.env['builder.website.menu']

        for page in record_id.page_ids:
            page_id = False
            for p in page.page_ids:
                page_id = p

            data = self.env['ir.model.data'].search([('model', '=', 'ir.ui.view'), ('res_id', '=', page.id)])
            current_page = page_item_model.search([('module_id', '=', record_id.module_id.id), ('attr_id', '=', data.name)])

            page_source = html.fromstring(page.arch)

            while page_source.xpath('//t'):
                for t in page_source.xpath('//t'):
                    t. getparent().remove(t)

            while page_source.xpath('//data'):
                for t in page_source.xpath('//data'):
                    t. getparent().remove(t)

            if not current_page.id:
                data = {
                    'module_id': record_id.module_id.id,
                    'attr_id': data.name,
                    'attr_name': page.name,
                    'content': etree.tostring(page_source, pretty_print=True, xml_declaration=True),
                    'attr_page': True,
                    # 'wrap_layout': 'website.layout',
                    'attr_priority': page.priority,
                    'attr_inherit_id': page.inherit_id.xml_id
                }
                if page_id:
                    data['attr_page']=True
                    data['website_published'] = page_id.website_published
                    data['website_indexed'] = page_id.website_indexed
                    data['url'] = page_id.url
                else:
                    data['attr_page']=False
                    if page.inherit_id:
                        data['attr_inherit_id']= page.inherit_id.xml_id
                new_item = page_item_model.create(data)

        return {'type': 'ir.actions.act_window_close'}
