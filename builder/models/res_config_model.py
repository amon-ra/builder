import re

from odoo import models, fields, api, _


class SettingModel(models.Model):
    _name = 'builder.res.config.settings'
    _description = "Configuration Model"
    _order = 'sequence asc, model asc'

    _rec_name = 'model'

    module_id = fields.Many2one('builder.ir.module.module', 'Module', required=True, index=1, ondelete='cascade')
    sequence = fields.Integer('Sequence')
    model = fields.Char('Model', required=True, index=1)
    name = fields.Char('Description', required=True)

    field_ids = fields.One2many('builder.res.config.settings.field', 'model_id', 'Fields', required=True, copy=True)

    
    def action_fields(self):
        return {
            'name': _('Fields'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': self.field_ids._name,
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('model_id', '=', self.id)],
            # 'target': 'current',
            'context': {
                'default_module_id': self.module_id.id,
                'default_model_id': self.id,
            },
        }


class SettingModelField(models.Model):
    _name = 'builder.res.config.settings.field'
    _inherit = ['builder.ir.model.fields']

    model_id = fields.Many2one('builder.res.config.settings', 'Model', ondelete='cascade')
    group_ids = fields.Many2many('builder.res.groups', 
        'builder_res_config_settings_field_group_rel', 'field_id', 'group_id', 
        string='Groups')    
    special_states_field_id = fields.Many2one('builder.ir.model.fields', related=False,
                                              string='States Field')
    ttype = fields.Selection(required=False)

    setting_field_type = fields.Selection(
        [
            ('module', 'Module Toggle Field'),
            ('default', 'Default Value Field'),
            ('group', 'Group Field'),
            ('other', 'Normal Field'),
        ], 'Setting Type', default='other', required=True)

    toggle_module_id = fields.Many2one('ir.module.module', 'Module', store=False, search=True)
    toggle_module_name = fields.Char('Module Name')

    default_type = fields.Selection([('module', 'Module'), ('system', 'System')], 'Default Type')
    default_system_model_id = fields.Many2one('ir.model', 'System Model', store=False, search=True)
    default_model_id = fields.Many2one('builder.ir.model', 'Builder Model')
    default_model = fields.Char('Model')
    default_field_name = fields.Char('Field Name')
    default_system_model_field_id = fields.Many2one('ir.model.fields', 'System Field', store=False, search=True,
                                                    domain="[('model_id', '=', default_system_model_id)]",
                                                    change_default=True)
    default_model_field_id = fields.Many2one('builder.ir.model.fields', 'Builder Field',
                                             domain="[('model_id', '=', default_model_id)]", change_default=True)

    group_type = fields.Selection([('module', 'Module'), ('system', 'System')], 'Group Type')
    group_system_group_id = fields.Many2one('res.groups', 'System Group', store=False, search=True)
    group_group_id = fields.Many2one('builder.res.groups', 'Builder Group')
    group_name = fields.Char('Implied Group')

    @api.onchange('default_type', 'default_model_id', 'default_system_model_id')
    def onchange_default_model_id(self):
        self.default_model = False
        if self.default_type == 'module' and self.default_model_id:
            self.default_model = self.default_model_id.model
        elif self.default_type == 'system' and self.default_system_model_id:
            self.default_model = self.default_system_model_id.model

    @api.onchange('default_type', 'default_model_field_id', 'default_system_model_field_id')
    def onchange_default_model_field_id(self):
        self.default_field_name = False
        if self.default_type == 'module' and self.default_model_field_id:
            self.default_field_name = self.default_model_field_id.name
            self.ttype = self.default_model_field_id.ttype
        elif self.default_type == 'system' and self.default_system_model_field_id:
            self.default_field_name = self.default_system_model_field_id.name
            self.ttype = self.default_system_model_field_id.ttype

    @api.onchange('relation_model_id')
    def onchange_relation_model_id(self):
        self.relation = self.relation_model_id.model if self.relation_model_id else False

    @api.onchange('setting_field_type', 'toggle_module_name', 'default_field_name', 'group_name')
    @api.depends('setting_field_type', 'toggle_module_name', 'default_field_name', 'group_name')
    def _compute_field_name(self):
        for obj in self:
            if obj.setting_field_type == 'module' and obj.toggle_module_name:
                obj.name = "module_{}".format(obj.toggle_module_name)
                obj.ttype = 'boolean'
            elif obj.setting_field_type == 'default' and obj.default_field_name:
                obj.name = "default_{}".format(obj.default_field_name)
            elif obj.setting_field_type == 'group' and obj.group_name:
                obj.name = "group_{}".format(re.sub('\.', '_', obj.group_name))
                obj.ttype = 'boolean'

    @api.onchange('toggle_module_id')
    def onchange_toggle_module_id(self):
        if self.setting_field_type == 'module' and self.toggle_module_id:
            self.toggle_module_name = self.toggle_module_id.name

    @api.onchange('default_type', 'default_system_model_id', 'default_model_id')
    def onchange_default_system(self):
        if self.default_type == 'module' and self.default_model_id:
            self.default_model = self.default_model_id.model
        elif self.default_type == 'system' and self.default_system_model_id:
            self.default_model = self.default_system_model_id.model

    @api.onchange('group_type', 'group_system_group_id', 'group_group_id')
    def onchange_default_system(self):
        if self.group_type == 'module' and self.group_group_id:
            self.group_name = "{module}.{id}".format(module=self.module_id.name, id=self.group_group_id.name)
        elif self.group_type == 'system' and self.group_system_group_id:
            data = self.env['ir.model.data'].search(
                [('model', '=', 'res.groups'), ('res_id', '=', self.group_system_group_id.id)])
            if data:
                self.group_name = "{module}.{id}".format(module=data.module, id=data.name)


class Module(models.Model):
    _name = 'builder.ir.module.module'
    _inherit = ['builder.ir.module.module']

    setting_ids = fields.One2many(
        comodel_name='builder.res.config.settings',
        inverse_name='module_id',
        string='Settings',
        copy=True
    )
