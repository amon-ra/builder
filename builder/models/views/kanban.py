from ..fields import snake_case
from odoo import models, fields, api
from odoo.exceptions import ValidationError

__author__ = 'one'


class KanbanView(models.Model):
    _name = 'builder.views.kanban'

    _inherit = ['ir.mixin.polymorphism.subclass']

    _inherits = {
        'builder.ir.ui.view': 'view_id'
    }

    view_id = fields.Many2one('builder.ir.ui.view', string='View', required=True, ondelete='cascade')
    attr_create = fields.Boolean('Allow Create', default=True)
    attr_edit = fields.Boolean('Allow Edit', default=True)
    attr_delete = fields.Boolean('Allow Delete', default=True)
    attr_default_group_by_field_id = fields.Many2one('builder.ir.model.fields', 'Default Group By Field',
                                                     ondelete='set null')
    attr_template = fields.Text('Template')
    attr_quick_create = fields.Boolean('Quick Create', default=True)
    # attr_quick_create = fields.Selection([(1, 'Quick Create'), (2, 'No Quick Create')], 'Quick Create')
    field_ids = fields.Many2many('builder.ir.model.fields', 'builder_view_views_kanban_field_rel', 'view_id',
                                 'field_id', 'Items')
    # field_ids = fields.One2many('builder.views.kanban.field', 'view_id', 'Items')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['type']='kanban'
        res['subclass_model']=self._name
        return res  

    @api.model
    def create_instance(self, id):
        self.create({
            'view_id': id,
        })

    
    def action_save(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.name = self.model_id.name
        self.xml_id = "view_{snake}_kanban".format(snake=snake_case(self.model_id.model))
        self.model_inherit_type = self.model_id.inherit_type  # shouldn`t be doing that
        self.model_name = self.model_id.model  # shouldn`t be doing that

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
        if self.inherit_view and self.model_id:
            views = self.env['ir.ui.view'].search([('type', '=', 'kanban'), ('model', '=', self.model_id.model)])
            if views:
                self.inherit_view_id = views[0].id

    @api.constrains('inherit_view_ref')
    def _check_view_ref(self):
      for record_id in self:
        exists = self.env['ir.model.data'].xmlid_lookup(record_id.inherit_view_ref)
        if exists:
            view = self.env['ir.model.data'].get_object(*record_id.inherit_view_ref.split('.'))
            if not view.model == record_id.model_id.model:
                raise ValidationError("View Ref is not a valid view reference")


class KanbanField(models.Model):
    _name = 'builder.views.kanban.field'
    _inherit = 'builder.views.abstract.field'

    view_id = fields.Many2one('builder.views.kanban', string='View', ondelete='cascade')
    invisible = fields.Boolean('Invisible')
