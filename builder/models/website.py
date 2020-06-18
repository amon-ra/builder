import random
from jinja2 import Template
import re
__author__ = 'one'

from odoo import models, fields, api, _

CONTROLLER_MODEL_SEARCH_METHOD="""
        \"""get search result for auto suggestions\"""
        strings = '%' + kw.get('name') + '%'
        try:
            domain = [('website_published', '=', True)]
            blog = request.env['blog.post'].with_user(SUPERUSER_ID).search(domain)
            sql = \"""select id as res_id, name as name, name as value from blog_post where name ILIKE '{}'\"""
            extra_query = ''
            limit = " limit 15"
            qry = sql + extra_query + limit
            request.cr.execute(qry.format(strings, tuple(blog and blog.ids)))
            name = request.cr.dictfetchall()
        except:
            name = {'name': 'None', 'value': 'None'}
        return json.dumps(name)
"""
CONTROLLER_MODEL_METHOD="""
        \"""function related to blog display\"""
        date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')
        published_count, unpublished_count = 0, 0

        domain = request.website.website_domain()
        blog_post = request.env['blog.post']
        blogs = request.env['blog.blog'].search(domain, order="create_date asc", limit=2)
        # retrocompatibility to accept tag as slug
        active_tag_ids = tag and [int(unslug(t)[1]) for t in tag.split(',')] if tag else []
        if active_tag_ids:
            fixed_tag_slug = ",".join(slug(t) for t in request.env['blog.tag'].browse(active_tag_ids))
            if fixed_tag_slug != tag:
                return request.redirect(
                    request.httprequest.full_path.replace("/tag/%s/" % tag, "/tag/%s/" % fixed_tag_slug, 1), 301)
            domain += [('tag_ids', 'in', active_tag_ids)]
        if blog:
            domain += [('blog_id', '=', blog.id)]
        if date_begin and date_end:
            domain += [("post_date", ">=", date_begin), ("post_date", "<=", date_end)]

        if request.env.user.has_group('website.group_website_designer'):
            count_domain = domain + [("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())]
            published_count = blog_post.search_count(count_domain)
            unpublished_count = blog_post.search_count(domain) - published_count

            if state == "published":
                domain += [("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())]
            elif state == "unpublished":
                domain += ['|', ("website_published", "=", False), ("post_date", ">", fields.Datetime.now())]
        else:
            domain += [("post_date", "<=", fields.Datetime.now())]

        blog_url = QueryURL('', ['blog', 'tag'], blog=blog, tag=tag, date_begin=date_begin, date_end=date_end)

        search_string = opt.get('search', None)

        blog_posts = blog_post.search([('name', 'ilike', search_string)],
                                      offset=(page - 1) * self._blog_post_per_page,
                                      limit=self._blog_post_per_page) if search_string \
            else blog_post.search(domain,
                                  order="post_date desc")

        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=len(blog_posts),
            page=page,
            step=self._blog_post_per_page,
            url_args=opt,
        )
        pager_begin = (page - 1) * self._blog_post_per_page
        pager_end = page * self._blog_post_per_page
        blog_posts = blog_posts[pager_begin:pager_end]

        all_tags = request.env['blog.tag'].search([])
        use_cover = request.website.viewref('website_blog.opt_blog_cover_post').active
        fullwidth_cover = request.website.viewref('website_blog.opt_blog_cover_post_fullwidth_design').active
        offset = (page - 1) * self._blog_post_per_page
        first_post = blog_posts
        if not blog:
            first_post = blog_posts.search(domain + [('website_published', '=', True)], order="post_date desc, id asc",
                                           limit=1)
            if use_cover and not fullwidth_cover:
                offset += 1

        # function to create the string list of tag ids, and toggle a given one.
        # used in the 'Tags Cloud' template.

        def tags_list(tag_ids, current_tag):
            tag_ids = list(tag_ids)  # required to avoid using the same list
            if current_tag in tag_ids:
                tag_ids.remove(current_tag)
            else:
                tag_ids.append(current_tag)
            tag_ids = request.env['blog.tag'].browse(tag_ids).exists()
            return ','.join(slug(tags) for tags in tag_ids)

        tag_category = sorted(all_tags.mapped('category_id'), key=lambda category: category.name.upper())
        other_tags = sorted(all_tags.filtered(lambda x: not x.category_id), key=lambda tags: tags.name.upper())
        values = {
            'blog': blog,
            'blogs': blogs,
            'first_post': first_post.with_prefetch(blog_posts.ids) if not search_string else None,
            'other_tags': other_tags,
            'state_info': {"state": state, "published": published_count, "unpublished": unpublished_count},
            'active_tag_ids': active_tag_ids,
            'tags_list': tags_list,
            'posts': blog_posts,
            'blog_posts_cover_properties': [json.loads(b.cover_properties) for b in blog_posts],
            'pager': pager,
            'nav_list': self.nav_list(blog),
            'blog_url': blog_url,
            'date': date_begin,
            'tag_category': tag_category,
        }
        response = request.render("website_blog.blog_post_short", values)
        return response
"""

CONTROLLER_SEARCH_AUTOCOMPLETE_JS="""
odoo.define('{module}.{model}', function (require) {
"use strict";
var ajax = require('web.ajax');
$(function() {
    $(".{model}_search_query").autocomplete({
        source: function(request, response) {
            $.ajax({
            url: "{route}",
            method: "POST",
            dataType: "json",
            data: { name: request.term},
            success: function( data ) {
                response( $.map( data, function( item ) {
                    return {
                        label: item.name,
                        value: item.name,
                        id: item.res_id,
                    }
                }));
            },
            error: function (error) {
               alert('error: ' + error);
            }
            });
        },
        select:function(suggestion,term,item){
            window.location.href= "{dest_route.name}/"+term.item.id
        },
        minLength: 1
    });

});
});
"""

class BackendAssets(models.Model):
    _name = 'builder.web.asset'

    _rec_name = 'attr_id'
    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    attr_name = fields.Char(string='Name')
    attr_id = fields.Char(string='XML ID')
    attr_priority = fields.Integer('Priority', default=10)

    item_ids = fields.One2many('builder.web.asset.item', 'asset_id', 'Items', copy=True)


class WebAssetItem(models.Model):
    _name = 'builder.web.asset.item'

    sequence = fields.Integer('Sequence', default=10)
    file_id = fields.Many2one('builder.data.file', 'File', ondelete='CASCADE')
    asset_id = fields.Many2one('builder.web.asset', 'Asset', ondelete='CASCADE')


class WebsiteAssets(models.Model):
    _name = 'builder.website.asset'

    _rec_name = 'attr_id'
    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    attr_name = fields.Char(string='Name')
    attr_id = fields.Char(string='XML ID', required=True)
    attr_active = fields.Boolean('Active')
    attr_customize_show = fields.Boolean('Customize Show')
    attr_inherit_id = fields.Char('Inherit Asset')
    attr_priority = fields.Integer('Priority', default=10)
    item_ids = fields.One2many('builder.website.asset.item', 'asset_id', 'Items', copy=True)


class AssetItem(models.Model):
    _name = 'builder.website.asset.item'

    sequence = fields.Integer('Sequence', default=10)
    file_id = fields.Many2one('builder.data.file', 'File', ondelete='CASCADE')
    asset_id = fields.Many2one('builder.website.asset', 'Asset', ondelete='CASCADE')


class MediaItem(models.Model):
    _name = 'builder.website.media.item'

    _rec_name = 'attr_name'

    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    attr_id = fields.Char('XML ID', compute='_compute_attr_id', readonly=False, store=True)
    file_id = fields.Many2one('builder.data.file', 'Image', required=True, ondelete='cascade')
    attr_name = fields.Char(string='Name', related='file_id.filename', store=False, search=True)
    is_image = fields.Boolean('Image', related='file_id.is_image', store=False, search=True)
    image = fields.Binary('Image', related='file_id.content', store=False, search=True)
    image_small = fields.Binary('Image Small', related='file_id.image_small', store=False, search=True)
    size = fields.Integer('Size', related='file_id.size', store=False, search=True)

    @api.constrains('file_id')
    def constraint_file_id_image(self):
        if self.file_id and not self.file_id.is_image:
            raise ValueError(
                _("You must select only images files."))

        return True

    @api.depends('attr_name')
    def _compute_attr_id(self):
      for record_id in self:
        if not record_id.attr_id and record_id.attr_name:
            record_id.attr_id = re.sub('[^a-zA-Z_]', '_', record_id.attr_name) + str(1 + len(record_id.search([])))

    @api.onchange('attr_name')
    def _onchange_attr_id(self):
        if not self.attr_id and self.attr_name:
            self.attr_id = re.sub('[^a-zA-Z_]', '_', self.attr_name) + str(1 + len(self.search([])))

class WebsiteRouteMethod(models.Model):
    _name = 'builder.website.route.method'

    name = fields.Selection([
        ('POST','POST'),('GET','GET'),('PUT','PUT')],string='Method')
    method_id = fields.Many2one('builder.website.method',required=True)

class WebsiteControllerMethod(models.Model):
    _name = 'builder.website.method'
    _inherit = 'builder.python.file.method'

    controller_id = fields.Many2one('builder.website.controller', 'Controller', ondelete='cascade')
    csrf = fields.Boolean('CSRF',default=True)
    visibility = fields.Selection([
        ('public','Public'),('user','Private')
        ],string="Visibility", default='public')
    route_type = fields.Selection([
        ('html','html'),('json','json'),('xml','xml')],string='Type',default='json')
    route_method_ids = fields.One2many('builder.website.route.method','method_id',
        string='Method')
    controller_route = fields.One2many('builder.website.route','method_id',
        string='Route')
    page_id = fields.Many2one('builder.website.page',string='Page')


# class ControllerRouterParameter(models.Model):
#     _name = 'builder.website.route.parameter'

#     name = fields.Char('Argument name',required=True)
#     default = fields.Char('Default Value',default='')
#     route_id = fields.Char('builder.website.route',required=True)

class ControllerRoute(models.Model):
    _name = 'builder.website.route'

    method_id = fields.Many2one('builder.website.method',required=True)
    name = fields.Char('Route',required=True,help="""Examples:
    /blog/<model("blog.blog", "[('website_id', 'in', (False, current_website_id))]"):blog_argument>,
    /blog/<model("blog.blog"):blog_argument>/page/<int:blog_page>,
    /blog/<model("blog.blog"):blog_argument>/tag/<string:blog_tag>,
    /blog/<model("blog.blog"):blog_argument>/tag/<string:tag>/page/<int:blog_page>,
    /blog/search_content,
Where blog_argument,blog_page,blog_tag must be created as arguments above
        """)
    parameters = fields.Char('Add to Route',default='')
    # parameter_ids = fields.One2many('builder.website.route.parameter',
    #     'route_id',string='Parameters')

    @api.model
    def create(self,vals):
        name = vals.get('name')
        website = vals.get('method_id')
        if name and website:
            record_id = self.search([
                ('controller_id','=',website),
                ('name','=',name)
            ])
            if record_id:
                return record_id
        super().create(vals)

class Controllers(models.Model):
    _name = 'builder.website.controller'

    index_page_id = fields.Many2one('builder.website.page','Page')
    page_id = fields.Many2one('builder.website.page','Page')
    model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade')
    module_id = fields.Many2one('builder.ir.module.module', 'Module',
                                ondelete='cascade', required=True)
    name = fields.Char('Name',required=True)
    parent = fields.Char('Parent')
    controller_method_ids = fields.One2many('builder.website.method','controller_id','Custom Methods', copy=True)
    import_ids = fields.One2many('builder.python.file.import', 'controller_id', 'Imports', copy=True)
    custom_code_line_ids = fields.One2many('builder.python.file.line','controller_id', 'Custom Code', copy=True)
    asset_ids = fields.Many2many('builder.website.asset','Assets', copy=False)

    def create_model_search(self):
        Assets = self.env['builder.website.asset']
        Methods = self.env['builder.website.method']
        Routes = self.env['builder.website.route']
        DataFile = self.env['builder.data.file']
        for record_id in self:
            v = record_id.get_version()
            Generator = self.env['builder.generator.v'+v]
            if not (record_id.model_id and record_id.page_id): continue
            method_name = record_id.model_id.model.replace('.','_'
                )
            route_name = '/'+record_id.model_id.name.replace(' ','')
            for m in record_id.controller_method_ids:
                if m.name == method_name:
                    continue
            d = {
                'controller_id': record_id.id,
                'csrf': False,
                'visibility': 'public',
                'route_type': 'html',
                'name': method_name,
                'custom_code': Generator.code('controllers/model_method.py.jinja2',{
                    'module': record_id.module_id.name,
                    'model': record_id.model_id.model,
                    'page_id': record_id.page_id.attr_id,
                })
            }
            method_id = record_id.controller_method_ids.create(d)
            method_id.controller_route.create({
                'name': route_name,
                # 'parameters': '/'
            })
            method_id.controller_route.create({
                'name': route_name,
                'parameters': '/search_content'
            })
            d.update({
                'custom_code': Generator.code('controllers/index_model_method.py.jinja2',{
                    'module': record_id.module_id.name,
                    'model': record_id.model_id.model,
                    'page_id': record_id.index_page_id.attr_id,
                    'route': route_name,
                })
            })
            method_id = record_id.controller_method_ids.create(d)
            method_id.controller_route.create({
                'name': route_name,
                'parameters': '/<model("{}"):post>'.format(record_id.model_id.model)
            })
            d.update({
                'name':method_name+'_search_autocomplete',
                'route_type':'json',
                'custom_code': Generator.code('controllers/model_method.py.jinja2',{
                    'module': record_id.module_id.name,
                    'model': record_id.model_id.model,
                    'page_id': record_id.index_page_id.attr_id,
                    'route': route_name,
                })
            })
            method_id = record_id.controller_method_ids.create(d)
            method_id.route_method_ids.create({'name':'POST'})
            method_id.controller_route.create({
                'name': '/'+method_name,
            })
            d = {
                'module_id': record_id.module_id.id,
                'path': method_name+'.js',
                'content': Generator.code('controllers/search.js.jinja2',{
                    'module': record_id.module_id.name,
                    'model': record_id.model_id.model,
                    'route': route_name,
                })
            }
            file_id = DataFile.create(d)
            d = {
                'module_id': record_id.module_id.id,
                'attr_id': method_name,
                'attr_name': method_name,
            }
            asset_id = Assets.create(d)
            asset_id.item_ids.create({
                'file_id': file_id.id,
            })
# class JavascriptDep(models.Model):
#     _name = 'builder.website.controller.javascript.deps'

#     name = fields.Char('Depend')
#     javascript_id = fields.Many2one('builder.website.controller', 'Controller', ondelete='cascade')

# class Javascript(models.Model):
#     _name = 'builder.website.controller.javascript'

#     controller_id = fields.Many2one('builder.website.controller', 'Controller', ondelete='cascade')
#     dependencies = fields.One2many('builder.website.controller.javascript.deps',
#         'javascript_id',string='Dependencies')
#     code


class Pages(models.Model):
    _name = 'builder.website.page'

    _rec_name = 'attr_name'


    module_id = fields.Many2one('builder.ir.module.module', 'Module',
                                ondelete='cascade', required=True)
    attr_name = fields.Char(string='Name', required=True)
    attr_id = fields.Char('XML ID', required=True)
    attr_inherit_id = fields.Char('Inherit Asset')
    attr_priority = fields.Integer('Priority', default=10)
    attr_page = fields.Boolean('Page', default=True)
    # inherit_id = fields.Many2one('builder.ir.ui.view.inherit','Inherit View')
    # domain="[('module_id','=',module_id)]")
    website_published = fields.Boolean('Published')
    website_indexed = fields.Boolean('Indexed')
    website_url = fields.Char('URL')
    asset_ids = fields.Many2many('builder.website.asset',string='Assets', copy=False)

    # gen_controller = fields.Boolean('Generate Controller', default=False)
    # controller_route = fields.Char('Route')

    content = fields.Html('Body', sanitize=False)

    def action_edit_html(self):
        # if not len(ids) == 1:
        #     raise ValueError('One and only one ID allowed for this action')
        self.ensure_one()
        url = '/builder/page/designer?model={model}&res_id={id}&enable_editor=1'.format (id = self.id, model=self._name)
        return {
            'name': _('Edit Template'),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    # @api.onchange('attr_page')
    # def _onchange_page(self):
    #     self.gen_controller = not self.attr_page


class Theme(models.Model):
    _name = 'builder.website.theme'

    _rec_name = 'attr_name'

    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    attr_id = fields.Char(string='ID', required=True)
    attr_name = fields.Char(string='Name', required=True)
    attr_description = fields.Html('Description')
    image = fields.Binary(string='Image')
    color = fields.Char(string='Color')
    font_name = fields.Char("Font Name")
    font_attr = fields.Char("Font", help="ex: Times New Roman")
    type = fields.Selection([('layout', 'Layout'),('color', 'Color'), ('font', 'Font'), ('other', 'Other')], string='Type', required=True, default='layout')
    item_ids = fields.One2many('builder.website.theme.item', 'theme_id', 'Items', copy=True)


class ThemeAssetItem(models.Model):
    _name = 'builder.website.theme.item'

    sequence = fields.Integer('Sequence', default=10)
    file_id = fields.Many2one('builder.data.file', 'File', ondelete='CASCADE')
    theme_id = fields.Many2one('builder.website.theme', 'Theme', ondelete='CASCADE')


class Menu(models.Model):
    _name = 'builder.website.menu'

    _order = 'sequence, id'

    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    sequence = fields.Integer('Sequence', default=60)
    name = fields.Char(string='Name', required=True)
    url = fields.Char("URL")
    page_id = fields.Many2one('builder.website.page', 'Page', required=True)
    parent_id = fields.Many2one('builder.website.menu', 'Parent')

    @api.onchange('page_id')
    def onchange_page_id(self):
        if self.page_id:
            self.name = self.page_id.attr_name
            if self.page_id.attr_page:
                self.url = '/page/website.' + self.page_id.attr_id
            else:
                if self.page_id.controller_route:
                    self.url = self.page_id.controller_route[0].name

SNIPPET_TEMPLATE = Template("""
    <xpath expr="//div[@id='snippet_{{ category }}']/div[@class='o_panel_body']" position="inside">
        <!-- begin snippet declaration -->
        <div>

            <div class="oe_snippet_thumbnail">
                <span class="oe_snippet_thumbnail_img" src="data:base64,{{ image }}"/>
                <span class="oe_snippet_thumbnail_title">{{ name }}</span>
            </div>

            <div class="oe_snippet_body {{ snippet_id }}">
                {{ content }}
            </div>
        </div>
        <!-- end of snippet declaration -->


    </xpath>

    <xpath expr="//div[@id='snippet_options']" position="inside">
        <div data-snippet-option-id='{{ snippet_id }}'
             data-selector=".{{ snippet_id }}"
             data-selector-siblings="{{ siblings|default('') }}"
             data-selector-children="{{ children|default('') }}"
             >
        </div>
    </xpath>
""")


class WebsiteSnippet(models.Model):
    _name = 'builder.website.snippet'

    _order = 'sequence, name'

    name = fields.Char('Name', required=True)

    sequence = fields.Integer('Sequence')
    category = fields.Selection(
        selection=[
            ('structure', 'Structure'),
            ('content', 'Content'),
            ('feature', 'Features'),
            ('effect', 'Effects'),
            ('custom', 'Custom'),
        ],
        string='Category',
        required=True,default='custom'
    )

    is_custom_category = fields.Boolean('Is Custom Category', compute='_compute_is_custom_category')

    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade', required=True)

    # Source
    source_url = fields.Char('Source URL', readonly=True)
    xpath = fields.Char('XPath', readonly=True)

    # Snippet
    snippet_id = fields.Char('ID', compute='_compute_snippet_id', store=True, readonly=False, required=True)
    content = fields.Html('Content', sanitize=False)
    image = fields.Binary('Image')

    # Options
    siblings = fields.Char('Allowed Siblings')
    children = fields.Char('Allowed Children')

    @api.depends('name')
    def _compute_snippet_id(self):
      for record_id in self:
        record_id.snippet_id = record_id.name.lower().replace(' ', '_').replace('.', '_') if record_id.name else ''

    @api.depends('category')
    def _compute_is_custom_category(self):
      for record_id in self:
        record_id.is_custom_category = record_id.category == 'custom'

    def action_edit_html(self):
        # if not len(ids) == 1:
        #     raise ValueError('One and only one ID allowed for this action')
        self.ensure_one()
        url = '/builder/page/designer?model={model}&res_id={id}&enable_editor=1'.format (id = self.id, model=self._name)
        return {
            'name': _('Edit Snippet'),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }


class Module(models.Model):
    _inherit = 'builder.ir.module.module'

    website_media_item_ids = fields.One2many('builder.website.media.item', 'module_id', 'Media Items', copy=True)
    # website_media_item_ids = fields.Many2many('builder.data.file', 'website_media_item_file_rel', 'module_id', 'file_id', 'Media Items', domain=[('is_image', '=', True)])
    website_menu_ids = fields.One2many('builder.website.menu', 'module_id', 'Menu', copy=True)
    website_asset_ids = fields.One2many('builder.website.asset', 'module_id', 'Assets', copy=True)
    website_theme_ids = fields.One2many('builder.website.theme', 'module_id', 'Themes', copy=True)
    website_page_ids = fields.One2many('builder.website.page', 'module_id', 'Pages', copy=True)
    website_snippet_ids = fields.One2many('builder.website.snippet', 'module_id', 'Snippets', copy=True)
    website_controller_ids = fields.One2many('builder.website.controller', 'module_id', 'Controllers', copy=True)



class PythonFileLine(models.Model):
    _inherit = 'builder.python.file.line'

    page_method_id = fields.Many2one('builder.website.method', 'Website Method', ondelete='cascade')

    @api.model
    def create(self,vals):
        # PythonFile
        name = vals.get('name')
        field = 'page_method_id'
        model = vals.get(field)
        if name and model:
            record_id = self.search([
                    (field,'=',model),
                    ('name','=',name),
                ])
            if record_id:
                record_id.write(vals)
                return record_id
        return super(PythonFileLine,self).create(vals)


class WebsiteFileImports(models.Model):
    _inherit = 'builder.python.file.import'

    controller_id = fields.Many2one('builder.website.page', 'Page', ondelete='cascade')
    # module_id = fields.Many2one('builder.ir.module.module', string='Module', related='model_id.module_id',
    #                             ondelete='cascade')

    @api.model
    def create(self, vals):
        #Return record if exists
        name = vals.get('name')
        # module = vals.get('module_id')
        import_ref = 'controller_id'
        model = vals.get(import_ref)
        if model and name:
            record_id = self.search([
                (import_ref,'=', model),
                ('name','=', name)
            ])
            if record_id:
                record_id.write(vals)
                return record_id
        return super().create(vals)

class WebsitePythonFileLine(models.Model):
    _inherit = 'builder.python.file.line'

    controller_id = fields.Many2one('builder.website.page', 'Page', ondelete='cascade')

    @api.model
    def create(self,vals):
        # PythonFile
        name = vals.get('name')
        field = 'controller_id'
        model = vals.get(field)
        if name and model:
            record_id = self.search([
                    (field,'=',model),
                    ('name','=',name),
                ])
            if record_id:
                record_id.write(vals)
                return record_id
        return super().create(vals)
