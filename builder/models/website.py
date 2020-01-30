import random
from jinja2 import Template
import re
__author__ = 'one'

from odoo import models, fields, api, _


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

    @api.one
    @api.depends('attr_name')
    def _compute_attr_id(self):
        if not self.attr_id and self.attr_name:
            self.attr_id = re.sub('[^a-zA-Z_]', '_', self.attr_name) + str(1 + len(self.search([])))

    @api.onchange('attr_name')
    def _onchange_attr_id(self):
        if not self.attr_id and self.attr_name:
            self.attr_id = re.sub('[^a-zA-Z_]', '_', self.attr_name) + str(1 + len(self.search([])))

class ControllerRouterParameter(models.Model):
    _name = 'builder.website.route.parameter'

    name = fields.Char('Argument name',required=True)
    default = fields.Char('Default Value',default='')
    route_id = fields.Char('builder.website.route',required=True)

class ControllerRoute(models.Model):
    _name = 'builder.website.route'

    website_id = fields.Many2one('builder.website.page',required=True)
    name = fields.Char('Route',required=True,help="""Examples: 
    /blog/<model("blog.blog", "[('website_id', 'in', (False, current_website_id))]"):blog_argument>,
    /blog/<model("blog.blog"):blog_argument>/page/<int:blog_page>,
    /blog/<model("blog.blog"):blog_argument>/tag/<string:blog_tag>,
    /blog/<model("blog.blog"):blog_argument>/tag/<string:tag>/page/<int:blog_page>,
    /blog/search_content,
Where blog_argument,blog_page,blog_tag must be created as arguments above    
        """)
    parameter_ids = fields.One2many('builder.website.route.parameter',
        'route_id',string='Parameters')

    @api.model
    def create(self,vals):
        name = vals.get('name')
        website = vals.get('website')
        if name and website:
            record_id = self.search([
                ('website_id','=',website),
                ('name','=',name)
            ])
            if record_id:
                return record_id
        super().create(vals)

class Pages(models.Model):
    _name = 'builder.website.page'

    _rec_name = 'attr_name'

    model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade')
    module_id = fields.Many2one('builder.ir.module.module', 'Module',
                                ondelete='cascade', required=True)
    attr_name = fields.Char(string='Name', required=True)
    attr_id = fields.Char('XML ID', required=True)
    attr_inherit_id = fields.Char('Inherit Asset')
    attr_priority = fields.Integer('Priority', default=10)
    attr_page = fields.Boolean('Page', default=True)
    visibility = fields.Selection([
        ('public','Public'),('user','Private')
        ],string="Visibility", default='public')
    csrf = fields.Boolean('CSRF',default=True)
    gen_controller = fields.Boolean('Generate Controller', default=False)
    # controller_route = fields.Char('Route')
    controller_route = fields.One2many('builder.website.route','website_id',
        string='Route')
    content = fields.Html('Body', sanitize=False)
    website_method_ids = fields.One2many('builder.website.method','module_id','Custom Methods', copy=True)
    import_ids = fields.One2many('builder.python.file.import', 'website_id', 'Imports', copy=True)
    custom_code_line_ids = fields.One2many('builder.python.file.line','website_id', 'Custom Code', copy=True)

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

    @api.onchange('attr_page')
    def _onchange_page(self):
        self.gen_controller = not self.attr_page


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

    @api.one
    @api.depends('name')
    def _compute_snippet_id(self):
        self.snippet_id = self.name.lower().replace(' ', '_').replace('.', '_') if self.name else ''

    @api.one
    @api.depends('category')
    def _compute_is_custom_category(self):
        self.is_custom_category = self.category == 'custom'

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

class WebsiteControllerMethod(models.Model):
    _name = 'builder.website.method'

    _order = 'sequence, id'

    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    sequence = fields.Integer('Sequence', default=60)

    name = fields.Char(string='Name', required=True)
    visibility = fields.Selection([
        ('public','Public'),('user','Private')
        ],string="Visibility", default='public')
    route_type = fields.Selection([
        ('html','html'),('json','json'),('xml','xml')],string='Type',default='json')
    route_method = fields.Selection([
        ('POST','POST'),('GET','GET'),('PUT','PUT')],string='Method')
    controller_route = fields.One2many('builder.website.route','website_id',
        string='Route')
    custom_code_line_ids = fields.One2many('builder.python.file.line','website_method_id', 'Custom Code', copy=True)
   

class Module(models.Model):
    _inherit = 'builder.ir.module.module'

    website_media_item_ids = fields.One2many('builder.website.media.item', 'module_id', 'Media Items', copy=True)
    # website_media_item_ids = fields.Many2many('builder.data.file', 'website_media_item_file_rel', 'module_id', 'file_id', 'Media Items', domain=[('is_image', '=', True)])
    website_menu_ids = fields.One2many('builder.website.menu', 'module_id', 'Menu', copy=True)
    website_asset_ids = fields.One2many('builder.website.asset', 'module_id', 'Assets', copy=True)
    website_theme_ids = fields.One2many('builder.website.theme', 'module_id', 'Themes', copy=True)
    website_page_ids = fields.One2many('builder.website.page', 'module_id', 'Pages', copy=True)
    website_snippet_ids = fields.One2many('builder.website.snippet', 'module_id', 'Snippets', copy=True)



class PythonFileLine(models.Model):
    _inherit = 'builder.python.file.line'

    website_method_id = fields.Many2one('builder.website.method', 'Website Method', ondelete='cascade')

    @api.model
    def create(self,vals):
        # PythonFile
        name = vals.get('name')
        field = 'website_method_id'
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

    website_id = fields.Many2one('builder.website.page', 'Page', ondelete='cascade')
    # module_id = fields.Many2one('builder.ir.module.module', string='Module', related='model_id.module_id',
    #                             ondelete='cascade')

    @api.model
    def create(self, vals):
        #Return record if exists
        name = vals.get('name')
        # module = vals.get('module_id')
        import_ref = 'website_id'
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

    website_id = fields.Many2one('builder.website.page', 'Page', ondelete='cascade')

    @api.model
    def create(self,vals):
        # PythonFile
        name = vals.get('name')
        field = 'website_id'
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
