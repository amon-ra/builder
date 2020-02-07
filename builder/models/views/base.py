from odoo.exceptions import ValidationError
from odoo import models, api, fields, _


import logging
_logger = logging.getLogger(__name__)

# Oondeo
FIELD_WIDGETS_ALL = [
    ('barchart', "FieldBarChart"),
    ('binary', "FieldBinaryFile"),
    ('boolean', "FieldBoolean"),
    ('char', "FieldChar"),
    ('char_domain', "FieldCharDomain"),
    ('date', "FieldDate"),
    ('datetime', "FieldDatetime"),
    ('email', "FieldEmail"),
    ('float', "FieldFloat"),
    ('float_time', "FieldFloat"),
    ('html', "FieldTextHtml"),
    ('image', "FieldBinaryImage"),
    ('integer', "FieldFloat"),
    ('id', "FieldID"),
    ('kanban_state_selection', "KanbanSelection"),
    ('many2many', "FieldMany2Many"),
    ('many2many_binary', "FieldMany2ManyBinaryMultiFiles"),
    ('many2many_checkboxes', "FieldMany2ManyCheckBoxes"),
    ('many2many_kanban', "FieldMany2ManyKanban"),
    ('many2many_tags', "FieldMany2ManyTags"),
    ('many2one', "FieldMany2One"),
    ('many2onebutton', "Many2OneButton"),
    ('monetary', "FieldMonetary"),
    ('one2many', "FieldOne2Many"),
    ('one2many_list', "FieldOne2Many"),
    ('percentpie', "FieldPercentPie"),
    ('priority', "Priority"),
    ('progressbar', "FieldProgressBar"),
    ('radio', "FieldRadio"),
    ('reference', "FieldReference"),
    ('selection', "FieldSelection"),
    ('statinfo', "StatInfo"),
    ('statusbar', "FieldStatus"),
    ('text', "FieldText"),
    ('url', "FieldUrl"),
    ('x2many_counter', "X2ManyCounter"),
]
VIEW_TYPES = {
    'calendar': 'builder.views.calendar',
    'form': 'builder.views.form',
    'gantt': 'builder.views.gantt',
    'graph': 'builder.views.graph',
    'kanban': 'builder.views.kanban',
    'search': 'builder.views.search',
    'tree': 'builder.views.tree',
    'qweb': 'builder.ir.ui.view',
    'diagram': 'builder.ir.ui.view',
    'pivot': 'builder.ir.ui.pivot',
}

SEL_VIEW_TYPES = [
            ('form', 'Form'),
            ('tree', 'Tree'),
            ('calendar', 'Calendar'),
            ('gantt', 'Gantt'),
            ('kanban', 'Kanban'),
            ('graph', 'Graph'),
            ('search', 'Search'),
            ('diagram', 'Diagram'),
            ('qweb', 'QWeb'),
            ('pivot', 'Pivot')    
]

class ViewSelector(models.TransientModel):
    _name = 'builder.views.selector'

    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade', required=True)
    model_name = fields.Char('Model Name', related='model_id.name', store=False)
    add_inherited_fields = fields.Boolean('Add Inherited Fields', default=True)
    model_inherit_type = fields.Selection([('mixed', 'Mixed'), ('class', 'Class'), ('prototype', 'Prototype'), ('delegation', 'Delegation')], 'Inherit Type', related='model_id.inherit_type')
    special_states_field_id = fields.Many2one('builder.ir.model.fields', 'States Field',
                                              related='model_id.special_states_field_id')
    model_groups_date_field_ids = fields.One2many('builder.ir.model.fields', string='Has Date Fields',
                                                  related='model_id.groups_date_field_ids')
    type = fields.Selection(
        SEL_VIEW_TYPES , 'Type', required=True, default='form')

    inherit_view = fields.Boolean('Inherit')
    inherit_view_id = fields.Many2one('ir.ui.view', 'Inherit View')
    inherit_view_ref = fields.Char('Inherit View Ref')

    @api.onchange('inherit_view_id')
    def onchange_inherit_view_id(self):
        self.inherit_view_ref = False
        if self.inherit_view_id:
            data = self.env['ir.model.data'].search([('model', '=', 'ir.ui.view'), ('res_id', '=', self.inherit_view_id.id)])
            self.inherit_view_ref = "{module}.{id}".format(module=data.module, id=data.name) if data else False

    @api.onchange('type')
    def onchange_type(self):
        self.inherit_view_ref = False
        self.inherit_view_id = False

    @api.onchange('inherit_view')
    def onchange_inherit_view(self):
        if self.inherit_view and self.model_id and self.type:
            views = self.env['ir.ui.view'].search([('type', '=', self.type), ('model', '=', self.model_id.model)])
            if views:
                self.inherit_view_id = views[0].id

    @api.constrains('inherit_view_ref')
    def _check_view_ref(self):
      for record_id in self:
        if record_id.inherit_view_ref:
            exists = self.env['ir.model.data'].xmlid_lookup(record_id.inherit_view_ref)
            if exists:
                view = self.env['ir.model.data'].get_object(*record_id.inherit_view_ref.split('.'))
                if not view.model == record_id.model_id.model:
                    raise ValidationError("View Ref is not a valid view reference")

    
    def action_show_view(self):
        res_id = False
        wizard = False
        if self.type == 'wizard':
            self.type = 'form'
            wizard = True
            # res_id = self.env['builder.views.form'].create({
            #     'wizard': True,
            #     'type': 'form',
            #     'model_id': self.model_id.id,
            #     'special_states_field_id': self.special_states_field_id.id,
            #     'module_id': self.model_id.module_id.id,
            #     'add_inherited_fields': self.add_inherited_fields,
            #     'inherit_view': self.inherit_view,
            #     'inherit_view_id': self.inherit_view_id.id,
            #     'inherit_view_ref': self.inherit_view_ref,
            # })

        view_type_names = { x[0]:x[1] for x in SEL_VIEW_TYPES}

        return {
            'name': view_type_names[self.type],
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'builder.views.' + self.type,
            'views': [(False, 'form')],
            'res_id': res_id,
            'target': 'new',
            'context': {
                'default_wizard': wizard,
                'default_model_id': self.model_id.id,
                'default_special_states_field_id': self.special_states_field_id.id,
                'default_module_id': self.model_id.module_id.id,
                'add_inherited_fields': self.add_inherited_fields,
                'default_inherit_view': self.inherit_view,
                'default_inherit_view_id': self.inherit_view_id.id,
                'default_inherit_view_ref': self.inherit_view_ref,
            },
        }


class View(models.Model):
    _name = 'builder.ir.ui.view'
    _rec_name = 'xml_id'

    _inherit = ['ir.mixin.polymorphism.superclass']

    define = fields.Boolean('Is defined',default=True)
    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='CASCADE')
    model_id = fields.Many2one('builder.ir.model', ondelete='cascade')
    model_inherit_type = fields.Selection([('mixed', 'Mixed'), ('class', 'Class'), ('prototype', 'Prototype'), ('delegation', 'Delegation')], 'Inherit Type', related='model_id.inherit_type', store=False, search=True)
    model_name = fields.Char('Model Name', related='model_id.name', store=False)
    special_states_field_id = fields.Many2one('builder.ir.model.fields', 'States Field',
                                              related='model_id.special_states_field_id')
    model_groups_date_field_ids = fields.One2many('builder.ir.model.fields', string='Has Date Fields',
                                                  related='model_id.groups_date_field_ids')
    group_ids = fields.Many2many('builder.res.groups', 'builder_ir_ui_view_group_rel', 'view_id', 'group_id', string='Groups', help="If this field is empty, the view applies to all users. Otherwise, the view applies to the users of those groups only.")

    # type = fields.Char('View Type')
    type = fields.Selection(
       SEL_VIEW_TYPES , 'Type', required=True, default='form')

    name = fields.Char('View Name', required=True)
    xml_id = fields.Char('View ID', required=True)
    priority = fields.Integer('Sequence')

    inherit_id = fields.Many2one('builder.ir.ui.view', 'Inherited View', ondelete='cascade', index=True)
    inherit_children_ids = fields.One2many('builder.ir.ui.view', 'inherit_id', 'Inherit Views')
    field_parent = fields.Char('Child Field')

    inherit_view = fields.Boolean('Inherit')
    inherit_view_id = fields.Many2one('ir.ui.view', 'Inherit View')
    inherit_view_ref = fields.Char('Inherit View Ref')
    inherit_change_ids = fields.One2many(
        comodel_name='builder.ir.ui.view.inherit.change',
        inverse_name='view_id',
        string='Changes',
    )
    arch = fields.Text('XML Data')
    custom_arch = fields.Boolean('Custom XML')

    @api.onchange('type')
    def _onchange_type(self):
        self.subclass_model = 'builder.views.' + self.type

    
    def action_open_view(self):
        model = self
        action = model.get_formview_action(self.ids)
        action.update({'target': 'new'})
        return action

    
    def action_save(self):
        return {'type': 'ir.actions.act_window_close'}

    @property
    def real_xml_id(self):
        return self.xml_id if '.' in self.xml_id else '{module}.{xml_id}'.format(module=self.module_id.name, xml_id=self.xml_id)

class InheritView(models.AbstractModel):
    _name = 'builder.ir.ui.view.inherit'
    _order = 'sequence, id'
    _rec_name = 'xml_id'

    sequence = fields.Integer('Sequence')
    # module_id = fields.Many2one('builder.ir.module.module','Module')
    view_source = fields.Selection([('module', 'Module'), ('system', 'System')], 'Source', required=True)
    module_view_id = fields.Many2one('builder.ir.ui.view', 'Model', ondelete='cascade')
    system_view_id = fields.Many2one('ir.ui.view', 'View', ondelete='set null')
    system_view_name = fields.Char('View Name')
    xml_id = fields.Char('Model', compute='_compute_xml_id')

    # def create(self, vals):
    #     module = vals.get('module_id')
    #     model = vals.get('model')
    #     field = 'system_view_name'
    #     name = vals.get(field)
    #     if not name:
    #         field = 'module_view_id'
    #         name = vals.get(field)
    #     if module == False:
    #         model_id = self.env['builder.ir.model'].browse([vals['model_id']])
    #         module = model_id.module_id.id
    #         vals['module_id'] = module
    #     if name and model and module:
    #         record_id = self.search([
    #             ('module_id','=',module),
    #             ('model_id','=',model),
    #             (field,'=',name)
    #         ])
    #         if record_id:
    #             record_id.write(vals)
    #             return record_id
    #     return super().create(vals)

    # 
    # def write(self, vals):
    #     if not vals.get('module_id',False):
    #         model = vals.get('model_id',self.model_id.id)
    #         model_id = self.env['builder.ir.model'].browse([model])
    #         vals['module_id'] = model_id.module_id.id
    #     return  super().write(vals)

    @api.depends('model_source', 'module_view_id', 'system_view_id', 'system_view_name')
    def _compute_xml_id(self):
      for record_id in self:
        record_id.xml_id = record_id.system_view_name if record_id.model_source == 'system' else record_id.module_view_id.name

    @api.onchange('model_source', 'module_view_id', 'system_view_id', 'system_view_name')
    def onchange_system_view_id(self):
        self.system_view_name = self.system_view_id.name if self.model_source == 'system' else False
        self.xml_id = self.system_view_name if self.model_source == 'system' else self.module_view_id.name

    def get_model_name(self):
        if self.module_view_id:
            return self.module_view_id.model
        if self.system_view_id:
            return self.system_view_id.model





class InheritViewChange(models.Model):
    _name = 'builder.ir.ui.view.inherit.change'

    view_id = fields.Many2one(
        comodel_name='builder.ir.ui.view',
        string='View',
        ondelete='cascade',
    )
    inherit_view_type = fields.Selection([('field', 'Field'), ('xpath', 'XPath')], 'Selection Type', default='field',
                                         required=False)
    inherit_view_target = fields.Char('Inherit Target', required=True)
    inherit_view_position = fields.Selection([('after', 'After'), ('before', 'Before'), ('inside', 'Inside'), ('replace', 'Replace'), ('attribute', 'Attribute')], 'Inherit Position', default='after',
                                             required=True)
    inherit_view_attribute = fields.Char('Change Attribute')
    inherit_view_attribute_value = fields.Char('Change Attribute Value')
    inherit_view_field = fields.Char('Field')
    inherit_view_arch = fields.Text('XML Data')
    inherit_view_selector = fields.Selection([('field','Field'),('xml','XML')],default='field',string="Content Type")


class AbstractViewField(models.AbstractModel):
    _name = 'builder.views.abstract.field'

    _rec_name = 'field_id'
    _order = 'view_id, sequence'

    view_id = fields.Many2one('builder.ir.ui.view', string='Name', ondelete='cascade')
    sequence = fields.Integer('Sequence')
    field_id = fields.Many2one('builder.ir.model.fields', string='Field', required=True, ondelete='cascade')
    field_ttype = fields.Char(string='Field Type', compute='_compute_field_ttype')
    model_id = fields.Many2one('builder.ir.model', related='view_id.model_id', string='Model')
    special_states_field_id = fields.Many2one('builder.ir.model.fields',
                                              related='view_id.model_id.special_states_field_id', string='States Field')
    module_id = fields.Many2one('builder.ir.model', related='view_id.model_id.module_id', string='Module')
    string = fields.Char('String')

    def create(self, vals):
        if vals.get('module_id',True) is False or vals.get('model_id',True) == False:
            view_id = self.env['builder.ir.ui.view'].browse([vals['view_id']])
            vals['model_id']=view_id.model_id.id
            model_id = self.env['builder.ir.model'].browse([vals['model_id']])
            vals['module_id'] = model_id.module_id.id
        return super().create(vals)

    @api.depends('field_id.ttype')
    def _compute_field_ttype(self):
      for record_id in self:
        record_id.field_ttype = record_id.field_id.ttype


class ViewLine(models.Model):

    _name = 'builder.views.line'
    _order = 'sequence,name'

    name = fields.Char('Name')
    parent_id = fields.Many2one('builder.views.line','Parent', ondelete='cascade')
    child_ids = fields.One2many('builder.views.line', 'parent_id', 'Contains', copy=True)
    # parent_left = fields.Integer('Parent Left')
    # parent_right = fields.Integer('Parent Left')
    parent_path = fields.Char(index=True)
