from collections import defaultdict
import inspect

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

OVERRIDE_METHODS = {
    'create': (['api.model'],'vals','',''),
    'write': ([''],'vals','',''),
    'default_get': (['api.model'],'fields','',''),
    'view_header_get': (['api.model'],"view_id=None, view_type='form'",'',''),
    'fields_view_get': (['api.model'],"view_id=None, view_type='form', toolbar=False, submenu=False",'',''),
    'unlink': ([''],'','',''),
    'read': ([''],"fields=None, load='_classic_read",'',''),
    '_search': (['api.model'],'args, offset=0, limit=None, order=None, count=False, access_rights_uid=None','','')
}
BASE_METHODS = ['env','id','ids']

AUTO_FIELDS = ['id', 'write_date', 'create_date','__last_update', 'write_uid', 'create_uid']

def get_model_members(model_id, inherit_model_name):
    """ Get methods names from a model with the diference with his inherits"""
    ret = []
    # name = model_id.model
    # m = self.env[name]
    # m = model_id
    l = dir(model_id)
    _logger.debug(model_id)
    _logger.debug(inherit_model_name)
    _logger.debug(l)
    # for i in inherit_model_names:
    m = model_id.env[inherit_model_name]
    l = list(set(l) - set(dir(m)))
    _logger.debug(l)
    return l

def compute_methods(model_id, inherit_model_name):
    """ Get methods names from a model with the diference with his inherits"""
    ret = []
    # name = model_id.model
    # m = self.env[name]
    # m = model_id
    l = dir(model_id)
    _logger.debug(model_id)
    _logger.debug(inherit_model_name)
    _logger.debug(l)
    # for i in inherit_model_names:
    m = model_id.env[inherit_model_name]
    l = list(set(l) - set(dir(m)))
    _logger.debug(l)
    for i in l:
        try:
            # test if it is defined in source files
            source = inspect.getsource(getattr(model_id, i))
            if callable(getattr(model_id, i)):
                ret.append(i)
        except:
            pass
    return ret

def get_source_code(model_id,method_name):
    ret = ''
    m = getattr(model_id, method_name)
    # _logger.debug("-----lines--------")
    # _logger.debug(inspect.getsourcelines(m))
    # self.method_doc = getattr(model_id, method).__doc__
    ret += "\n# " + model_id._name
    try:
        ret += ':' + inspect.getsourcefile(
            m) + ':' + str(inspect.getsourcelines(m)[1])
    except Exception as e:
        _logger.warn("Source Code not found")
        _logger.info(e)
    ret += "\n" + inspect.getsource(m)

    return ret

def get_parent_source(model,name):
    src = ''
    doc = ''
    for c in inspect.getmro(model.__class__):
        try:
            _logger.debug(c)
            module = inspect.getmodule(c) 
            method = getattr(c,name)
            method_module = inspect.getmodule(method)
            _logger.debug(module)
            if module.__name__ == method_module.__name__ and module.__name__.startswith('odoo.addons'):
                src += module.__name__ + '\n' +inspect.getsource(
                    method) + '\n'
                d = inspect.getdoc(method)
                if d:
                    doc += d + '\n'
        except Exception as e:
            pass
    return src,doc

class IrModel(models.Model):
    _name = 'builder.ir.model'
    _description = "Models"
    _order = 'sequence, model'

    _rec_name = 'model'


    sequence = fields.Integer('Sequence')
    module_id = fields.Many2one('builder.ir.module.module', 'Module', required=True, index=True, ondelete='cascade')
    name = fields.Char('Description', required=True)
    model = fields.Char('Model', required=True, index=True)
    model_src_id = fields.Many2one('builder.ir.model','System Source')

    info = fields.Text('Information')
    rec_name_field_id = fields.Many2one('builder.ir.model.fields', 'Record Name', compute='_compute_rec_name_field_id',
                                        inverse='_inverse_rec_name_field_id',
                                        domain=[('ttype', 'in', ['char', 'text', 'date', 'datetime', 'selection'])])
    wizard = fields.Boolean('Wizard')
    # osv_memory = fields.Boolean('Transient',
    #                             help="This field specifies whether the model is transient or not (i.e. if records are automatically deleted from the database or not)")
    transient = fields.Boolean('Transient',
                                help="This field specifies whether the model is transient or not (i.e. if records are automatically deleted from the database or not)")
    field_ids = fields.One2many('builder.ir.model.fields', 'model_id', 'Fields', required=True, copy=True)
    relation_field_ids = fields.One2many('builder.ir.model.fields', 'relation_model_id', 'Referenced By Fields', copy=True)
    # inherit_model = fields.Char('Inherit', compute='_compute_inherit_model')

    inherit_model_ids = fields.One2many('builder.ir.model.inherit', 'model_id', 'Inherit', copy=True)
    inherits_model_ids = fields.One2many('builder.ir.model.inherits', 'model_id', 'Inherits', copy=True)

    is_inherited = fields.Boolean('Inherited', compute='_compute_inherited', store=True)
    inherit_type = fields.Selection(
        [('mixed', 'Mixed'), ('class', 'Class'), ('prototype', 'Prototype'), ('delegation', 'Delegation')],
        'Inherit Type', compute='_compute_inherited', store=True)

    access_ids = fields.One2many('builder.ir.model.access', 'model_id', 'Access', copy=True)

    view_ids = fields.One2many('builder.ir.ui.view', 'model_id', 'Views', copy=True)
    action_ids = fields.One2many('builder.ir.actions.actions', 'model_id', 'Actions', copy=True)
    menu_ids = fields.One2many('builder.ir.ui.menu', 'model_id', 'Menus', copy=True)
    method_ids = fields.One2many('builder.ir.model.method', 'model_id', 'Models', copy=True)
    import_ids = fields.One2many('builder.ir.model.import', 'model_id', 'Imports', copy=True)
    custom_code_line_ids = fields.One2many('builder.python.file.line','model_id', 'Custom Code', copy=True)

    to_ids = fields.One2many('builder.ir.model.fields', 'relation_model_id', 'Forward Models',
                             domain=[('ttype', 'in', ['many2one', 'one2many', 'many2many']),
                                     ('relation_model_id', '!=', False)])
    from_ids = fields.One2many('builder.ir.model.fields', 'model_id', 'Backward Models',
                               domain=[('ttype', 'in', ['many2one', 'one2many', 'many2many']),
                                       ('relation_model_id', '!=', False)])

    # extra fields

    special_states_field_id = fields.Many2one('builder.ir.model.fields', 'States Field',
                                              compute='_compute_special_fields', store=True)
    special_active_field_id = fields.Many2one('builder.ir.model.fields', 'Active Field',
                                              compute='_compute_special_fields', store=True)
    special_sequence_field_id = fields.Many2one('builder.ir.model.fields', 'Sequence Field',
                                                compute='_compute_special_fields', store=True)
    special_parent_id_field_id = fields.Many2one('builder.ir.model.fields', 'Parent Field',
                                                 compute='_compute_special_fields', store=True)

    groups_date_field_ids = fields.One2many('builder.ir.model.fields', 'model_id', string='Date Fields',
                                            compute='_compute_field_groups')
    groups_numeric_field_ids = fields.One2many('builder.ir.model.fields', 'model_id', string='Numeric Fields',
                                               compute='_compute_field_groups')
    groups_boolean_field_ids = fields.One2many('builder.ir.model.fields', 'model_id', string='Boolean Fields',
                                               compute='_compute_field_groups')
    groups_relation_field_ids = fields.One2many('builder.ir.model.fields', 'model_id', string='Relation Fields',
                                                compute='_compute_field_groups')
    groups_o2m_field_ids = fields.One2many('builder.ir.model.fields', 'model_id', string='O2M Fields',
                                           compute='_compute_field_groups')
    groups_m2m_field_ids = fields.One2many('builder.ir.model.fields', 'model_id', string='M2M Fields',
                                           compute='_compute_field_groups')
    groups_m2o_field_ids = fields.One2many('builder.ir.model.fields', 'model_id', string='M2O Fields',
                                           compute='_compute_field_groups')
    groups_binary_field_ids = fields.One2many('builder.ir.model.fields', 'model_id', string='M2O Fields',
                                              compute='_compute_field_groups')
    groups_inherited_field_ids = fields.One2many('builder.ir.model.fields', 'model_id', string='Inherited Fields',
                                                 compute='_compute_field_groups')

    order_field_ids = fields.One2many(
        comodel_name='builder.ir.model.fields',
        inverse_name='model_id',
        string='Order',
        domain=[('use_to_order', '=', True)],
        copy=True
    )

    status_bar_button_ids = fields.One2many(
        comodel_name='builder.views.form.statusbar.button',
        inverse_name='model_id',
        domain=[('type', '=', 'object')],
        string='Status Bar Buttons',
        copy=True
    )

    button_ids = fields.One2many(
        comodel_name='builder.views.form.button',
        inverse_name='model_id',
        domain=[('type', '=', 'object')],
        string='View Buttons',
        copy=True
    )

    @property
    def order_string(self):
        return ','.join(['{field} {order}'.format(field=f.name, order=f.order) for f in self.order_field_ids])

    @property
    def compute_field_methods(self):
        result = defaultdict(list)
        for field in self.field_ids:
            if field.allow_compute:
                result[field.compute_method_name].append(field.name)
        return result

    @property
    def inverse_field_methods(self):
        result = defaultdict(list)
        for field in self.field_ids:
            if field.allow_inverse:
                result[field.inverse_method_name].append(field.name)
        return result

    @property
    def search_field_methods(self):
        result = defaultdict(list)
        for field in self.field_ids:
            if field.allow_search:
                result[field.search_method_name].append(field.name)
        return result

    @property
    def default_field_methods(self):
        result = defaultdict(list)
        for field in self.field_ids:
            if field.allow_default:
                result[field.default_method_name].append(field.name)
        return result

    rewrite_create_method = fields.Boolean('Rewrite Create Method')
    rewrite_write_method = fields.Boolean('Rewrite Write Method')
    rewrite_unlink_method = fields.Boolean('Rewrite Unlink Method')

    diagram_position_x = fields.Integer('X')
    diagram_position_y = fields.Integer('Y')

    define = fields.Boolean('Defined',readonly=True,store=True,compute='_define')
    
    @api.depends('inherit_model_ids','method_ids','status_bar_button_ids','field_ids','model')
    def _define(self):
        _logger.debug("----251-----")
        _logger.debug(len(self.method_ids))
        ret = len(self.inherit_model_ids) or len(self.method_ids) or len(
            self.status_bar_button_ids) or len(self.button_ids) or any(
                not field.is_inherited or field.redefine
                for field in self.field_ids) or (
                self.inherit_model_ids and self.model != self.inherit_model_ids[0].model_id.name)
        _logger.debug(ret)
        self.define = ret

    @api.one
    def _compute_rec_name_field_id(self):
        self.rec_name_field_id = self.env['builder.ir.model.fields'].search([
            ('model_id', '=', self.id),
            ('is_rec_name', '=', True)
        ])

    @api.one
    def _inverse_rec_name_field_id(self):
        self.rec_name_field_id.write({
            'is_rec_name': True
        })

    @api.one
    @api.depends('inherit_model_ids', 'inherits_model_ids')
    def _compute_inherited(self):
        self.is_inherited = len(self.inherit_model_ids) > 0

        self.inherit_type = False
        if len(self.inherit_model_ids):
            if (len(self.inherit_model_ids) == 1) and (self.inherit_model_ids[0].model_display == self.model):
                self.inherit_type = 'class'
            else:
                self.inherit_type = 'prototype'
        else:
            if len(self.inherits_model_ids):
                self.inherit_type = 'delegation'

        if len(self.inherit_model_ids) and len(self.inherits_model_ids):
            self.inherit_type = 'mixed'

    @api.onchange('model')
    def on_model_change(self):
        if not self.name:
            self.name = self.model

    @api.multi
    def find_field_by_name(self, name):
        field_obj = self.env['builder.ir.model.fields']
        return field_obj.search([('model_id', '=', self.id), ('name', '=', name)])

    @api.multi
    def find_field_by_type(self, types):
        field_obj = self.env['builder.ir.model.fields']
        return field_obj.search([('model_id', '=', self.id), ('ttype', 'in', types)])

    @api.one
    @api.depends('field_ids', 'field_ids.name')
    def _compute_special_fields(self):
        self.special_states_field_id = self.find_field_by_name('state')
        self.special_active_field_id = self.find_field_by_name('active')
        self.special_sequence_field_id = self.find_field_by_name('sequence')
        self.special_parent_id_field_id = self.find_field_by_name('parent')

    @api.one
    @api.depends('field_ids', 'field_ids.ttype')
    def _compute_field_groups(self):
        self.groups_date_field_ids = self.find_field_by_type(['date', 'datetime'])
        self.groups_numeric_field_ids = self.find_field_by_type(['integer', 'float'])
        self.groups_boolean_field_ids = self.find_field_by_type(['boolean'])
        self.groups_relation_field_ids = self.find_field_by_type(['one2many', 'many2many', 'many2one'])
        self.groups_o2m_field_ids = self.find_field_by_type(['one2many'])
        self.groups_m2m_field_ids = self.find_field_by_type(['many2many'])
        self.groups_m2o_field_ids = self.find_field_by_type(['many2one'])
        self.groups_binary_field_ids = self.find_field_by_type(['binary'])
        self.groups_inherited_field_ids = self.env['builder.ir.model.fields'].search(
            [('model_id', '=', self.id), ('is_inherited', '=', True)])

    @api.multi
    def compute_methods(self):
        """ Return a list of str with method names, if is installed localy """
        ret = []
        for record in self:
            l = list(set(record) - set(dir(super())))
            for name,o in inspect.getmembers(record,inspect.ismethod):
                if name in l:
                    ret.append(name)
            return ret
    @api.multi
    def getmembers(self):
        ret = []
        for record in self:
            if not record._inherits:
               return  get_model_members(record,'ir.model')
            for i in record._inherits:
                ret += get_model_members(record,i)
            return ret

    @api.model
    def create(self,vals):
        model = vals.get('model')
        if model:
            record = self
            for x in self:
                record = x
                break
            ret = record.search([
                ('module_id','=', record.module_id.id),
                ('model','=', model),
            ])
            if ret:
                return ret
        create = vals.get('wizard')
        if create:
            pass
        skip_imports = vals.pop('skip_imports',False)
        ret = super().create(vals)
        if not skip_imports:
            ret.init_imports()
        return ret

    @classmethod
    def get_module_data(cls, module, model_name):
        data_obj = cls.env['ir.model.data']
        model_obj = cls.env[model_name]

        model_ids = [
            x.res_id
            for x in data_obj.search([('module', '=',
                                    module), ('model', '=', model_obj._name)])
        ]

        return model_obj.search([('id', 'in', model_ids)])


    def get_parent_fields(self):
        """ return str[] """
        field_ids = []
        for inherit_model_id in self.inherit_model_ids:
            model_name = inherit_model_id.get_model_name()
            for field_id in self.get_module_data(self.module_id.id,'ir.model.fields'):
                field_ids.append(field_id.name)
        return field_ids

    def init_imports(self):
        for record in self:
            if not record.import_ids:
                self.import_ids.create({
                    'module_id': record.module_id.id,
                    'model_id': record.id,
                    'parent': 'odoo',
                    'name': 'api,models,fields,tools,_'
                })
                self.import_ids.create({
                    'module_id': record.module_id.id,
                    'model_id': record.id,
                    'name': 'logging'
                })    
                self.custom_code_line_ids.create({
                    'module_id': record.module_id.id,
                    'model_id': record.id,
                    'class_code': False,
                    'custom_code': '_logger = logging.getLogger(__name__)',
                    'name': '_logger',                
                })            

    # def model_access_group_import(self,group_id,group_map={},rule_map={}):
    #     Groups = self.env['builder.res.groups']
    #     Rules = self.env['builder.ir.rule']
    #     Menus = self.env['builder.ir.ui.menu']
    #     for module_model in self:
    #         if not group_map:
    #             for g in Groups.search([
    #                 ('module_id','=',module_model.module_id.id)]):
    #                 group_map[g.xml_id]=g
    #         if not rule_map:
    #             for g in Rules.search([
    #                 ('module_id','=',module_model.module_id.id)]):
    #                 rule_map[g.system_id]=g
    #         if group_id.xml_id not in group_map:
    #             set_inherited = module_model.is_inherited
    #             vals ={
    #                 'module_id': module_model.module_id.id,
    #                 'xml_id': group_id.xml_id,
    #                 'name': group_id.name,
    #                 'category_type': 'system',
    #                 'category_id': group_id.category_id.id,
    #                 'category_ref': group_id.category_id.xml_id,
    #                 'portal': group_id.portal,
    #                 'share': group_id.share,
    #                 'sequence' : group_id.sequence,
    #                 'comment': group_id.comment,
    #                 'inherited': set_inherited
    #             }
    #             group_map[group_id.xml_id]=Groups.create(vals)
    #             for g in group_id.implied_ids:
    #                 group_map,rule_map=module_model.model_access_group_import(g,group_map)
    #             # for line in group_id.model_access:
    #             #     group_map,rule_map=module_model.model_access_import(line,group_map)
    #             for rule_id in group_id.rule_groups:
    #                 if rule_id.id not in rule_map:
    #                     vals = {
    #                         'module_id': module_model.module_id.id,
    #                         'model_id': module_model.id,
    #                         'name': rule_id.name,
    #                         'domain': rule_id.domain,
    #                         'perm_read': rule_id.perm_read,
    #                         'perm_write': rule_id.perm_write,
    #                         'perm_create': rule_id.perm_create,
    #                         'perm_unlink': rule_id.perm_unlink,                                              
    #                     }
    #                     if rule_id.group_id:
    #                         if not rule_id.group_id.xml_id in group_map:
    #                             group_map,rule_map=module_model.model_access_group_import(rule_id.group_id,group_map)
    #                         vals['group_id']=group_map[rule_id.group_id.xml_id].id                    
    #                     Rules.create(vals)
    #     return group_map,rule_map

    # def model_access_import(self,access_id,group_map={},rule_map={}):
    #     Access = self.env['builder.ir.model.access']
    #     for module_model in self:
    #         set_inherited = module_model.is_inherited               
    #         vals ={
    #             'module_id': module_model.module_id.id,
    #             'model_id': module_model.id,
    #             'name': access_id.name,
    #             'perm_read': access_id.perm_read,
    #             'perm_write': access_id.perm_write,
    #             'perm_create': access_id.perm_create,
    #             'perm_unlink': access_id.perm_unlink,
    #         }
    #         if access_id.group_id:
    #             if not access_id.group_id.xml_id in group_map:
    #                 group_map,rule_map=module_model.model_access_group_import(access_id.group_id,group_map)
    #             vals['group_id']=group_map[access_id.group_id.xml_id].id
    #         Access.create(vals)           
    #     return group_map,rule_map
    # def model_views_import(self,view):
    #     for module_model in self:
    #         if not self.env['builder.ir.ui.view'].search([('model_id', '=', module_model.id), ('xml_id', '=', view.xml_id)]):
    #             view_attrs = {
    #                 'module_id':  module_model.module_id.id,
    #                 'model_id': module_model.id,
    #                 'type': view.type,
    #                 'priority': view.priority,
    #                 'name': view.name,
    #                 'xml_id': view.xml_id,
    #                 'arch': view.arch,
    #                 'field_parent': view.field_parent,
    #                 'custom_arch': True,
    #                 'define': False
    #             }
    #             if view.inherit_id:
    #                 view_attrs.update({
    #                     'inherit_view_id': view.inherit_id.id,
    #                     'inherit_view_ref': view.inherit_id.xml_id,
    #                     'inherit_view': True,
    #                 })
    #             if view.type in ['calendar', 'search', 'pivot','tree', 'form', 'graph', 'kanban', 'gantt']:
    #                 view_attrs['custom_arch'] = True
    #                 _logger.debug(view_attrs)
    #                 mview = self.env['builder.views.' + view.type].create(view_attrs)
    #                 mview.write({'arch': view.arch})
    #             else:
    #                 module_model.module_id.view_ids.create(view_attrs)
    #             for child in view.inherit_children_ids:
    #                 module_model.model_views_import(child) 

    def model_fields_import(self,model_id,model_map={},field_list=None,relations_only=False,exclude_auto_fields=True):
        _review_models = set()
        for module_model in self:
            set_inherited = module_model.is_inherited
            if not model_map:
                for m in self.env['builder.ir.model'].search([
                    ('module_id','=',module_model.module_id.id)
                ]):
                    model_map[m.model]=m                                 
            for field in model_id.field_id:
                if not set_inherited and exclude_auto_fields and field.name in AUTO_FIELDS:
                    continue
                if field_list and field.name not in field_list:
                    continue
                if not self.env['builder.ir.model.fields'].search([('model_id', '=', module_model.id), ('name', '=', field.name)]):
                    _logger.debug(field.name)
                    values = {
                        'module_id': module_model.module_id.id,
                        'model_id': module_model.id,
                        'name': field.name,
                        'field_description': field.field_description,
                        'ttype': field.ttype,
                        'selection': field.selection,
                        'required': field.required,
                        'readonly': field.readonly,
                        # 'select_level': field.select_level,
                        'translate': field.translate,
                        'size': field.size,
                        'on_delete': field.on_delete,
                        'domain': field.domain,
                        'selectable': field.selectable,
                        'store': field.store,
                        'is_inherited': set_inherited,
                        'redefine': not set_inherited
                    }

                    if field.ttype in ['one2many', 'many2many', 'many2one']:
                        if not field.relation in model_map:
                            m = self.env['ir.model'].search(
                                [('model','=',field.relation)])[0] 
                            # new_model = self.create_model(
                            #     model_map[model_id.model].module_id.id,m,False)
                            new_model = self.env['builder.ir.model'].create({
                                'module_id': module_model.module_id.id,
                                'name': m.name,
                                'model': m.model,
                                'transient': m._transient == True,
                                # 'inherit_model': self.set_inherited and model.model or False
                            })
                            model_map[field.relation] = new_model
                            # _review_models.add(m)                      
                        values.update({
                            'relation': field.relation,
                            'relation_model_id': model_map[field.relation].id,
                            'relation_field': field.relation_field,
                            'domain': field.domain,
                        })
                    if not relations_only or (relations_only and field.ttype in ['one2many', 'many2many', 'many2one']):
                        _logger.debug(values)
                        model_map[model_id.model].field_ids.create(values)

        for m in _review_models:
            r = relations_only
            if field_list:
                r = True
            model_map = model_map[m.model].model_import(m, model_map, r,exclude_auto_fields)
        return model_map

     
    @api.multi
    def action_fields(self):
        ref = self.env.ref('builder.builder_ir_model_fields_form_view', False)
        return {
            'name': _('Fields'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': self.field_ids._name,
            'views': [(False, 'tree'), (ref.id if ref else False, 'form')],
            'domain': [('model_id', '=', self.id)],
            # 'target': 'current',
            'context': {
                'default_module_id': self.module_id.id,
                'default_model_id': self.id,
            },
        }

    @api.multi
    def action_methods(self):
        return {
            'name': _('Methods'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': self.method_ids._name,
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('model_id', '=', self.id)],
            # 'target': 'current',
            'context': {
                'default_module_id': self.module_id.id,
                'default_model_id': self.id,
            },
        }




class ModelImports(models.Model):
    _name = 'builder.ir.model.import'

    model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade')
    module_id = fields.Many2one('builder.ir.module.module', string='Module', related='model_id.module_id',
                                ondelete='cascade')

    parent = fields.Char(string='Parent')
    name = fields.Char(string='Name', required=True)
    python_file_id = fields.Many2one('builder.python.file', 
                                string="Custom Code",ondelete='cascade')

    @api.model
    def create(self, vals):
        #Return record if exists
        name = vals.get('name')
        module = vals.get('module_id')
        import_ref = 'model_id'
        model = vals.get(import_ref)
        if not model:  
            import_ref = 'model_id'
            model = vals.get(import_ref)                  
        if module and model and name:
            record_id = self.search([
                ('module_id','=', module),
                (import_ref,'=', model),
                ('name','=', name)
            ])
            if record_id:
                record_id.write(vals)
                return record_id
        return super().create(vals)


class ModelMethodDecorator(models.Model):
    _name = 'builder.ir.model.decorator'

    name = fields.Char(string='Name', required=True)
    # arguments = fields.Char(string='Arguments', default='')
    method_id = fields.Many2one('builder.ir.model.method',ondelete='cascade')

    @api.model
    def create(self, vals):
        #Return record if exists
        name = vals.get('name')
        import_ref = 'method_id'
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

class ModelMethod(models.Model):
    _name = 'builder.ir.model.method'

    # define = fields.Boolean("Redefined",default=True)
    # inherit_model_mame = fields.Char('Parent Model')
    model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade')
    module_id = fields.Many2one(related='model_id.module_id', string='Module', 
                                store=True,ondelete='cascade')
    decorator_ids = fields.One2many('builder.ir.model.decorator','method_id',string='Decorators')
    name = fields.Char(string='Name', required=True)
    arguments = fields.Char(string='Arguments', default='')

    use_cache = fields.Boolean('Use Cache', default=False)
    field_ids = fields.Many2many('builder.ir.model.fields',
                                 'builder_ir_model_method_fields_rel', 'model_method_id',
                                 'field_id', string='Fields')

    custom_code = fields.Text('Custom Code')

    parent_code = fields.Text('Parent Code',compute='_get_parent_code')

    type = fields.Selection(
        [
            ('simple_model', 'Model Method'),
            ('simple_instance', 'Instance Method'),
            ('onchange', 'On Change'),
            ('constraint', 'Constraint'),
        ], 'Method Type', required=True)

    @property
    def field_names(self):
        return [field.name for field in self.field_ids]

    def count_defined(self):
        n = 0
        for record in self:
            if record.define:
                n+=1
        return n
    # @api.model
    # def default_get(self, fields):
    #     res = super().default_get(fields)
    #     if not res.get('module_id',False):
    #         _logger.debug(res)
    #         _logger.debug(self.model_id)
    #         model_id = self.env['builder.ir.model'].browse(res['model_id'])
    #         res['module_id']=model_id.module_id
    #     return res

    @api.model
    def create(self, vals):
        #Return record if exists
        name = vals.get('name')
        module = vals.get('module_id',False)
        model = vals.get('model_id')
        _logger.debug(vals)
        if not module:
            model_id = self.env['builder.ir.model'].browse([model])
            module = model_id.module_id.id
            vals['module_id'] = module  
        _logger.debug(vals)                     
        if module and model and name:
            record_id = self.search([
                ('module_id','=', module),
                ('model_id','=', model),
                ('name','=', name)
            ])
            if record_id:
                record_id.write(vals)
                return record_id
        return super().create(vals)

    @api.multi
    def import_source_code(self):
        name = self.name
        model_id = self.env[self.model_id.model]
        src = inspect.getsource(getattr(model_id, name))
        custom_code = False
        self.custom_code = ''
        self.field_ids = (5, _, _)
        self.decorator_ids = (5, _, _)
        for l in src:
            self.custom_code += l
            line = l.strip()
            if custom_code:
                self.custom_code += l
            elif line.startswith('@api.one'):
                self.type = 'simple_instance'
            elif line.startswith('@api.model'):
                self.type = 'simple_model'
            elif line.startswith('@api.multi'):
                self.type = 'simple_model'
            elif line.startswith('@api.returns'):
                pass
            elif line.startswith('@api.constraint'):
                self.type = 'constraint'
            elif line.startswith('@api.onchange'):
                self.type = 'onchange'
            elif line.startswith('@api.depends'):
                #self.type = 'simple_instance'
                line = line.split('(')[1]
                line = line.split(')')[0]
                for arg in line.split(','):
                    self.field_ids = (0, 0, {
                        'name': arg,
                        'model_id': self.model_id,
                        'module_id': self.module_id,

                    })
            elif line.startswith('@'):
                #self.type = 'simple_instance'
                d = line.split('(')
                decorator = d[0][1:]
                args = d[1][:-1]
                self.decorator_ids = (0, 0, {
                    'name': decorator,
                    'arguments': args,
                    'method_id': self.id,
                })
            elif line.startswith('def '):
                custom_code = True
                # method_arr = line[4].split('(')
                # self.name = method_arr[0]
                # for arg in ','.join(method_arr[1:]).split(',')

    @api.depends('name','model_id')
    def _get_parent_code(self):
        for record in self:
            if record.model_id and record.name:
                obj = self.env.get(record.model_id.model)
                if obj:
                    record.parent_code,_ = get_parent_source(
                        self.env[record.model_id.model],
                        record.name
                    )

    @api.depends('name','model_id')
    def get_source_code(self):
        """ 
        return source code if module is installed 
        Code must be marked with __BUILDER_TAG___/module_name/inherit_name
        
        """
        model_id = self.env[self.model_id.model]
        src = inspect.getsource(getattr(
                        model_id, self.name))
        #tag = src.split('\n',1)[0]
        return src

class InheritModelTemplate(models.AbstractModel):
    _name = 'builder.ir.model.inherit.template'
    _order = 'sequence, id'

    sequence = fields.Integer('Sequence')
    model_id = fields.Many2one('builder.ir.model', string='Model', ondelete='cascade')
    module_id = fields.Many2one('builder.ir.module.module', string='Module', related='model_id.module_id',
                                ondelete='cascade')
    model_source = fields.Selection([('module', 'Module'), ('system', 'System')], 'Source', required=True)
    module_model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade')
    system_model_id = fields.Many2one('ir.model', 'Model', ondelete='set null')
    system_model_name = fields.Char('Model Name')
    model_display = fields.Char('Model', compute='_compute_model_display')

    def create(self, vals):
        module = vals.get('module_id')
        model = vals.get('model')
        field = 'system_model_name'
        name = vals.get(field)
        if not name:
            field = 'module_model_id'
            name = vals.get(field)
        if module == False:
            model_id = self.env['builder.ir.model'].browse([vals['model_id']])
            module = model_id.module_id.id
            vals['module_id'] = module
        if name and model and module:
            record_id = self.search([
                ('module_id','=',module),
                ('model_id','=',model),
                (field,'=',name)
            ])
            if record_id:
                record_id.write(vals)
                return record_id
        return super().create(vals)

    @api.multi
    def write(self, vals):
        if not vals.get('module_id',False):
            model = vals.get('model_id',self.model_id.id)
            model_id = self.env['builder.ir.model'].browse([model])
            vals['module_id'] = model_id.module_id.id
        return  super().write(vals)

    @api.one
    @api.depends('model_source', 'module_model_id', 'system_model_id', 'system_model_name')
    def _compute_model_display(self):
        self.model_display = self.system_model_name if self.model_source == 'system' else self.module_model_id.name

    @api.onchange('model_source', 'module_model_id', 'system_model_id', 'system_model_name')
    def onchange_system_model_id(self):
        self.system_model_name = self.system_model_id.name if self.model_source == 'system' else False
        self.model_display = self.system_model_name if self.model_source == 'system' else self.module_model_id.name

    def get_model_name(self):
        if self.module_model_id:
            return self.module_model_id.model
        if self.system_model_id:
            return self.system_model_id.model

    @api.multi
    def compute_system_methods(self):
        ret = []
        for record in self:
            # inherit_model_ids = [self.env[i] for i in record.system_model_id._inherit]
            for i in record.system_model_id._inherit:
                try:
                    ret += compute_methods(record.system_model_id, i)
                except:
                    _logger.debug(record.get_model_name())
                    _logger.debug(i)
                    _logger.debug(ret)
        return ret

    @api.multi
    def compute_methods(self):
        """ Return a list of str with method names """
        ret = []
        for record in self:
            if record.model_source == 'module':
                ret += record.module_model_id.compute_methods()
            if record.model_source == 'system':
                ret += record.compute_system_methods()
        return ret


class InheritModel(models.Model):
    _name = 'builder.ir.model.inherit'
    _inherit = 'builder.ir.model.inherit.template'


class InheritsModel(models.Model):
    _name = 'builder.ir.model.inherits'
    _inherit = 'builder.ir.model.inherit.template'

    field_name = fields.Char('Field')
    field_id = fields.Many2one('builder.ir.model.fields', 'Field')
    field_display = fields.Char('Field', compute='_compute_field_display')

    @api.one
    @api.depends('model_source', 'module_model_id', 'system_model_id', 'system_model_name')
    def _compute_field_display(self):
        self.field_display = self.field_name if self.model_source == 'system' else self.field_id.name


class InheritMethod(models.TransientModel):
    _name = 'builder.ir.model.method.inherit'

    # model_id = fields.Many2one('builder.ir.model',
    #                            'Model')
    # method_id = fields.Many2one('builder.ir.model.method',
    #                            'Method')

    # method_doc = fields.Text(string="Documentation",readonly=True)
    name = fields.Char(string="Name")
    # method_parent = fields.Char(string="Class",
    #                             readonly=True,
    #                             states={'custom': [('invisible', False)]}
    #                             )
    method_doc = fields.Text(string="Doc",readonly=True)
    method_source = fields.Text(string="Source",readonly=True)
    method_source_map = {}
    # method_source_file = fields.Char(string="Source File",
    #                             readonly=True)
    # method_source_line = fields.Char(string="Source Line",
    #                             readonly=True)

    state = fields.Selection(
        selection=lambda self: self._get_selection_state(),
        string="Method")
    # rewrite_custom_method = fields.Selection(
    #     lambda self: self._get_class_methods(),
    #     states={'custom': [('invisible', False)]},
    #     string="Custom Method")

    def _get_selection_state(self):
        # data = set([
        #     'create',
        #     'write',
        #     'unlink',
        #     'search',
        # ])   
        self.method_source_map = {key:value for key,value in OVERRIDE_METHODS.items()}
        # if not self: return []
        # for record in self: 
        # record = self       
        builder_model_id = self._default_model_id()
        if not builder_model_id:
            return []
            
        # ir_model_methods = set()
        # for n,value in inspect.getmembers(self.env['ir.model']):
        #     try:
        #         if  callable(value):
        #             ir_model_methods.add(n)
        #     except Exception as e :
        #         pass
        # _logger.debug(ir_model_methods)
        for i in builder_model_id.inherit_model_ids:
            # _logger.debug(i) 
            model = i.model_display
            model_id = self.env['ir.model'].search([
                ('model','=',model)])
            # _logger.debug(model)
            for n, value in inspect.getmembers(model_id):
                try:
                    _logger.debug(n)
                    m = inspect.getmodule(value)
                    _logger.debug(m.__name__)
                    # _logger.debug(value.self)
                    # _logger.debug(callable(value))
                    if  m.__name__.startswith('odoo.addons.'
                        ) and callable(value):
                        src,doc = get_parent_source(
                            self.env[model], n)
                        decorators = []
                        for line in inspect.getsourcelines(value)[0]:
                            if line.startswith('@'):
                                decorators.append(line[1:])
                            elif line.startswith('def'):
                                break
                        arg = str(inspect.signature(value))[1:-1]                       
                        if src:
                            self.method_source_map[n]=(decorators,arg,doc,src)
                            # data.add(n)
                except Exception as e :
                    pass
        ret =  [(x,x) for x in sorted(list(self.method_source_map.keys()))]
        _logger.debug(ret)
        return ret

    def _default_model_id(self):
        # _logger.debug(self.env.context)
        model_id = self.env.context.get('default_model_id')
        model_id = self.env['builder.ir.model'].browse([model_id])
        # _logger.debug(model_id)
        # _logger.debug(self.model_id)
        # raise UserWarning('No inherits methods')
        # if not model_id.inherit_model_ids:
        # raise UserWarning('No inherits methods')
        return model_id

    # def _get_class_methods(self):
    #     ret = []
    #     _logger.debug("-------OONDEO-----------")
    #     m = self.env.context.get('default_class_methods')
    #     _logger.debug(m)
    #     if m:
    #         return m
    #     model_id = self._default_model_id()
    #     for model in model_id.inherit_model_ids:
    #         name = model.get_model_name()
    #         m = model.compute_methods()
    #         _logger.debug(name)
    #         _logger.debug(m)
    #         ret += [(str(name) + '/' + str(i),
    #                     str(i)) for i in m]
    #     _logger.debug("-------OONDEO-----------")
    #     _logger.debug(ret)
    #     return ret

    @api.onchange('state')
    def _on_change_state(self):
        builder_model_id = self._default_model_id()
        if self.state == 'custom':
            return {}
        if not self.state:
            # if self.method_id:
            #     self.method_id.unlink()
            return {}
        
        # self.method_source = get_parent_source(
        #     self.env[builder_model_id.model], self.state)
        src = self.method_source_map.get(
            self.state,['','','',''])
        self.method_source = src[3]
        self.method_doc = src[2]


    # @api.onchange('rewrite_custom_method')
    # def _on_change_rewrite_custom_method(self):
    #     model_id = self._default_model_id()
    #     if not self.rewrite_custom_method:
    #         self.method_source = ''
    #         return False
    #     model, method = self.rewrite_custom_method.split('/')
    #     model_id = self.env[model]
    #     _logger.debug(model)
    #     _logger.debug(model_id)
    #     # self.method_doc = getattr(model_id, method).__doc__
    #     self.method_parent = model
    #     self.method_source = get_source_code(model_id,method)
    #     # m = getattr(model_id, method)
    #     # self.method_source += "\n# " + inspect.getsourcefile(
    #     #     m) + ':'  + inspect.getsourcelines(m)[0]
    #     # self.method_source += "\n# " + model.model_id.name
    #     # self.method_source = "\n# " + model
    #     # self.method_source += "\n" + inspect.getsource(m)
    #     self.name = method


    @api.multi
    def do_ok(self):

        model_id = self._default_model_id()
        if not self.state:
            return False
        method = self.state
        args = ''

        inherit_model_name = False
        # if self.state == 'custom':
        # model, method = self.rewrite_custom_method.split('/')
        m = self.env[model_id.model]
        value = getattr(m,self.state)
        args = str(inspect.signature(value))[1:-1]
        inherit_model_name = model_id.model
        decorators = []
        for line in inspect.getsourcelines(value)[0]:
            if line.startswith('@'):
                decorators.append(line[1:])
            elif line.startswith('def'):
                break
        # if self.state == 'create':
        #     args = 'vals'
        # if self.state == 'write':
        #     args = 'vals'
        # if self.state == 'search':
        #     args = 'vals'
        m = self.env['builder.ir.model.method'].create({
            'module_id': model_id.module_id.id,
            'model_id': model_id.id,
            'name': method,
            'define': True,
            'arguments': args,
            'type': 'simple_model',
            'inherit_model_name': inherit_model_name
        })
        for d in decorators:
            m.decorator_ids.create({
                'method_id': m.id,
                'name': d,
            })        


class PythonFileLine(models.Model):
    _inherit = 'builder.python.file.line'

    model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade')

    @api.model
    def create(self,vals):
        # PythonFile
        name = vals.get('name')
        field = 'model_id'
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
