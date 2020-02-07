from collections import defaultdict
import inspect


from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

BASE_METHODS = ['env','id','ids']


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


class IrModel(models.Model):
    _name = 'builder.report'
    _description = "Report"
    _order = 'sequence, model'

    # _rec_name = 'model'

    sequence = fields.Integer('Sequence')
    module_id = fields.Many2one('builder.ir.module.module', 'Module', required=True, index=True, ondelete='cascade')
    name = fields.Char('Description', required=True)
    model = fields.Char('Model', required=True, index=True)
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
    import_ids = fields.One2many('builder.python.file.import', 'model_id', 'Imports', copy=True)

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

    @property
    def define(self):
        return len(self.inherit_model_ids) > 1 or len(self.method_ids) or len(
            self.status_bar_button_ids) or len(self.button_ids) or any(
                not field.is_inherited or field.redefine
                for field in self.field_ids) or (
                self.inherit_model_ids and self.model != self.inherit_model_ids[0].model_id.name)

    def _compute_rec_name_field_id(self):
      for record_id in self:
        record_id.rec_name_field_id = self.env['builder.ir.model.fields'].search([
            ('model_id', '=', record_id.id),
            ('is_rec_name', '=', True)
        ])

    def _inverse_rec_name_field_id(self):
      for record_id in self:
        record_id.rec_name_field_id.write({
            'is_rec_name': True
        })

    @api.depends('inherit_model_ids', 'inherits_model_ids')
    def _compute_inherited(self):
      for record_id in self:
        record_id.is_inherited = len(record_id.inherit_model_ids) > 0

        record_id.inherit_type = False
        if len(record_id.inherit_model_ids):
            if (len(record_id.inherit_model_ids) == 1) and (record_id.inherit_model_ids[0].model_display == record_id.model):
                record_id.inherit_type = 'class'
            else:
                record_id.inherit_type = 'prototype'
        else:
            if len(record_id.inherits_model_ids):
                record_id.inherit_type = 'delegation'

        if len(record_id.inherit_model_ids) and len(record_id.inherits_model_ids):
            record_id.inherit_type = 'mixed'

    @api.onchange('model')
    def on_model_change(self):
        if not self.name:
            self.name = self.model

    
    def find_field_by_name(self, name):
        field_obj = self.env['builder.ir.model.fields']
        return field_obj.search([('model_id', '=', self.id), ('name', '=', name)])

    
    def find_field_by_type(self, types):
        field_obj = self.env['builder.ir.model.fields']
        return field_obj.search([('model_id', '=', self.id), ('ttype', 'in', types)])

    @api.depends('field_ids', 'field_ids.name')
    def _compute_special_fields(self):
      for record_id in self:
        record_id.special_states_field_id = record_id.find_field_by_name('state')
        record_id.special_active_field_id = record_id.find_field_by_name('active')
        record_id.special_sequence_field_id = record_id.find_field_by_name('sequence')
        record_id.special_parent_id_field_id = record_id.find_field_by_name('parent')

    @api.depends('field_ids', 'field_ids.ttype')
    def _compute_field_groups(self):
      for record_id in self:
        record_id.groups_date_field_ids = record_id.find_field_by_type(['date', 'datetime'])
        record_id.groups_numeric_field_ids = record_id.find_field_by_type(['integer', 'float'])
        record_id.groups_boolean_field_ids = record_id.find_field_by_type(['boolean'])
        record_id.groups_relation_field_ids = record_id.find_field_by_type(['one2many', 'many2many', 'many2one'])
        record_id.groups_o2m_field_ids = record_id.find_field_by_type(['one2many'])
        record_id.groups_m2m_field_ids = record_id.find_field_by_type(['many2many'])
        record_id.groups_m2o_field_ids = record_id.find_field_by_type(['many2one'])
        record_id.groups_binary_field_ids = record_id.find_field_by_type(['binary'])
        record_id.groups_inherited_field_ids = self.env['builder.ir.model.fields'].search(
            [('model_id', '=', record_id.id), ('is_inherited', '=', True)])

    
    def compute_methods(self):
        """ Return a list of str with method names, if is installed localy """
        ret = []
        for record in self:
            name = record.model
            try:
                model = self.env[name]
                for i in model._inherit:
                    ret += compute_methods(model, i)
            except:
                pass

        return ret

    
    def create(self,vals):
        create = vals.get('wizard')
        if create:
            pass
        return super().create(vals)


    
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

    
    def action_parent_methods(self):
        Method = self.env['builder.ir.model.method.inherit']
        model_list = []
        for model in self.inherit_model_ids:
            name = model.get_model_name()
            model_list.append(name)
        Method.search([('method_parent', 'in', model_list)]).unlink()
        for model in model_list:
            m = self.env[name]
            _logger.debug(dir(m))
            for inherit_name in m._inherit:
                l = compute_methods(m,inherit_name)
                for i in l:
                    Method.with_context({
                        'default_class_methods': [(name + '/' + i, i)]
                    }).create({
                        'method_parent': name,
                        'method_source': get_source_code(m,i),
                        'state': 'custom',
                        'rewrite_custom_method': name + '/' + i,
                        'name': i
                    })


            # l = list(set(dir(m)) - set(dir(models.Model)))
            # _logger.debug(l)
            # for i in list(dict.fromkeys(l)):
            #     _logger.debug(name)
            #     _logger.debug(i)
            #     try:
            #         obj = getattr(m, i)
            #         if callable(obj) and (
            #             i not in BASE_METHODS) and (
            #             not hasattr(obj,"id")
            #             ):
            #             Method.with_context({
            #                 'default_class_methods': [(name + '/' + i, i)]
            #             }).create({
            #                 'method_parent': name,
            #                 'method_source': get_source_code(m,i),
            #                 'state': 'custom',
            #                 'rewrite_custom_method': name + '/' + i,
            #                 'name': i
            #             })
            #     except Exception as e:
            #         _logger.debug(e)
            #         pass

        return {
            'name': _('Methods'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'builder.ir.model.method.inherit',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('method_parent', 'in', model_list)],
            # 'target': 'current',
            'context': {
                'default_module_id': self.module_id.id,
                'default_model_id': self.id,
            },
        }


class ModelImports(models.Model):
    _name = 'builder.python.file.import'

    model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade')
    module_id = fields.Many2one('builder.ir.module.module', string='Module', related='model_id.module_id',
                                ondelete='cascade')

    name = fields.Char(string='Name', required=True)

    def create(self, vals):
        if not vals.get('module_id',False):
            model = vals.get('model_id',self.model_id.id)
            model_id = self.env['builder.ir.model'].browse([model])
            vals['module_id'] = model_id.module_id.id
        return super().create(vals)

    
    def write(self, vals):
        if not vals.get('module_id',False):
            model = vals.get('model_id',self.model_id.id)
            model_id = self.env['builder.ir.model'].browse([model])
            vals['module_id'] = model_id.module_id.id
        return  super().write(vals)

class ModelMethod(models.Model):
    _name = 'builder.ir.model.method'

    inherit_model_mame = fields.Char('Parent Model')
    model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade')
    module_id = fields.Many2one('builder.ir.module.module', string='Module', related='model_id.module_id',
                                ondelete='cascade')

    name = fields.Char(string='Name', required=True)
    arguments = fields.Char(string='Arguments', default='')

    use_cache = fields.Boolean('Use Cache', default=False)
    field_ids = fields.Many2many('builder.ir.model.fields',
                                 'builder_ir_model_method_fields_rel', 'model_method_id',
                                 'field_id', string='Fields')

    custom_code = fields.Text('Custom Code')

    parent_code = fields.Text('Parent Code',compute='get_parent_code')

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

    # @api.model
    # def default_get(self, fields):
    #     res = super().default_get(fields)
    #     if not res.get('module_id',False):
    #         _logger.debug(res)
    #         _logger.debug(self.model_id)
    #         model_id = self.env['builder.ir.model'].browse(res['model_id'])
    #         res['module_id']=model_id.module_id
    #     return res

    # def create(self, vals):
    #     if not vals.get('model_id',False):
    #         model = vals.get('model_id',self.model_id.id)
    #         model_id = self.env['builder.ir.model'].browse([model])
    #         vals['module_id'] = model_id.module_id.id
    #     return super().create(vals)

    # 
    # def write(self, vals):
    #     if not vals.get('model_id',False):
    #         model = vals.get('model_id',self.model_id.id)
    #         model_id = self.env['builder.ir.model'].browse([model])
    #         vals['module_id'] = model_id.module_id.id
    #     return  super().write(vals)

    def get_parent_code(self):
        if not self.inherit_model_mame:
            return False
        model_id = self.env[self.inherit_model_mame]
        return inspect.getsource(getattr(
                        model_id, self.name))

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
        if vals.get('module_id',True) == False:
            model_id = self.env['builder.ir.model'].browse([vals['model_id']])
            vals['module_id'] = model_id.module_id.id
        return super().create(vals)

    
    def write(self, vals):
        if not vals.get('module_id',False):
            model = vals.get('model_id',self.model_id.id)
            model_id = self.env['builder.ir.model'].browse([model])
            vals['module_id'] = model_id.module_id.id
        return  super().write(vals)

    @api.depends('model_source', 'module_model_id', 'system_model_id', 'system_model_name')
    def _compute_model_display(self):
      for record_id in self:
        record_id.model_display = record_id.system_model_name if record_id.model_source == 'system' else record_id.module_model_id.name

    @api.onchange('model_source', 'module_model_id', 'system_model_id', 'system_model_name')
    def onchange_system_model_id(self):
        self.system_model_name = self.system_model_id.name if self.model_source == 'system' else False
        self.model_display = self.system_model_name if self.model_source == 'system' else self.module_model_id.name

    def get_model_name(self):
        if self.module_model_id:
            return self.module_model_id.model
        if self.system_model_id:
            return self.system_model_id.model

    
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

    @api.depends('model_source', 'module_model_id', 'system_model_id', 'system_model_name')
    def _compute_field_display(self):
      for record_id in self:
        record_id.field_display = record_id.field_name if record_id.model_source == 'system' else record_id.field_id.name


# class InheritMethodList(models.TransientModel):
#     _name = 'builder.ir.model.method.inherit'

#     name = fields.Char("Method")

class InheritMethod(models.TransientModel):
    _name = 'builder.ir.model.method.inherit'

    # model_id = fields.Many2one('builder.ir.model',
    #                            'Model',
    #                            ondelete='cascade',
    #                            compute=lambda self: self._default_model_id())

    # method_doc = fields.Text(string="Documentation",readonly=True)
    name = fields.Char(string="Name")
    method_parent = fields.Char(string="Class",
                                readonly=True,
                                states={'custom': [('invisible', False)]}
                                )
    method_source = fields.Text(string="Source",readonly=True)
    # method_source_file = fields.Char(string="Source File",
    #                             readonly=True)
    # method_source_line = fields.Char(string="Source Line",
    #                             readonly=True)

    state = fields.Selection([
        ('create','create'),
        ('write','write'),
        ('unlink','unlink'),
        ('search','search'),
        ('custom','custom'),
        ],string="Method")
    rewrite_custom_method = fields.Selection(
        lambda self: self._get_class_methods(),
        states={'custom': [('invisible', False)]},
        string="Custom Method")

    def _default_model_id(self):
        _logger.debug(self.env.context)
        model_id = self.env.context.get('default_model_id')
        model_id = self.env['builder.ir.model'].browse([model_id])
        _logger.debug(model_id)
        # raise UserWarning('No inherits methods')
        # if not model_id.inherit_model_ids:
        # raise UserWarning('No inherits methods')
        return model_id

    def _get_class_methods(self):
        ret = []
        _logger.debug("-------OONDEO-----------")
        m = self.env.context.get('default_class_methods')
        _logger.debug(m)
        if m:
            return m
        model_id = self._default_model_id()
        for model in model_id.inherit_model_ids:
            name = model.get_model_name()
            m = model.compute_methods()
            _logger.debug(name)
            _logger.debug(m)
            ret += [(str(name) + '/' + str(i),
                        str(i)) for i in m]
        _logger.debug("-------OONDEO-----------")
        _logger.debug(ret)
        return ret

    @api.onchange('state')
    def _on_change_state(self):
        model_id = self._default_model_id()
        if self.state == 'custom':
            return {}
        if not self.state:
            self.method_source = ''
            return {}
        self.method_source = ''
        for model in model_id.inherit_model_ids:
            model_id = self.env[model.model_id.name]
            self.method_source = get_source_code(model_id,self.state)
            # m = getattr(model_id, self.state)
            # # self.method_doc = getattr(model_id, method).__doc__
            # self.method_source += "\n# " + inspect.getsourcefile(
            #     m) + ':' + inspect.getsourcelines(m)[0]
            # self.method_source += "\n# " + model.model_id.name
            # self.method_source += "\n" + inspect.getsource(m)

    @api.onchange('rewrite_custom_method')
    def _on_change_rewrite_custom_method(self):
        model_id = self._default_model_id()
        if not self.rewrite_custom_method:
            self.method_source = ''
            return False
        model, method = self.rewrite_custom_method.split('/')
        model_id = self.env[model]
        _logger.debug(model)
        _logger.debug(model_id)
        # self.method_doc = getattr(model_id, method).__doc__
        self.method_parent = model
        self.method_source = get_source_code(model_id,method)
        # m = getattr(model_id, method)
        # self.method_source += "\n# " + inspect.getsourcefile(
        #     m) + ':'  + inspect.getsourcelines(m)[0]
        # self.method_source += "\n# " + model.model_id.name
        # self.method_source = "\n# " + model
        # self.method_source += "\n" + inspect.getsource(m)
        self.name = method


    
    def do_ok(self):
        model_id = self._default_model_id()
        if not self.state:
            return False
        method = self.state
        args = ''

        inherit_model_name = False
        if self.state == 'custom':
            model, method = self.rewrite_custom_method.split('/')
            record = self.env[model]
            args = str(inspect.signature(getattr(record,method)))[1:-1]
            inherit_model_name = model

        if self.state == 'create':
            args = 'vals'
        if self.state == 'write':
            args = 'vals'
        if self.state == 'search':
            args = 'vals'
        self.env['builder.ir.model.method'].create({
            'model_id': model_id.id,
            'name': method,
            'arguments': args,
            'type': 'simple_model',
            'inherit_model_name': inherit_model_name
        })


class ReportPythonImports(models.Model):
    _inherit = 'builder.python.file.import'
