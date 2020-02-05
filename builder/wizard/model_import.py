__author__ = 'one'

from odoo import models, api, fields, _
import logging
_logger = logging.getLogger(__name__)

AUTO_FIELDS = ['id', 'write_date', 'create_date','__last_update', 'write_uid', 'create_uid']
class ModelLine(models.TransientModel):
    _name = 'builder.ir.model.import.line'

    import_id = fields.Many2one('builder.ir.model.import.wizard', 'Wizard', required=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    create_fields = fields.Boolean('Include Fields')
    set_inherited = fields.Boolean('Set as Inherit', default=True)


class ModelImport(models.TransientModel):
    _name = 'builder.ir.model.import.wizard'

    model_ids = fields.Many2many('ir.model', 'builder_ir_model_import_wizard_model_rel', 'wizard_id', 'model_id', 'Models')
    exclude_fields = fields.Boolean('Exclude Fields',default=True)
    create_fields = fields.Boolean('Include Fields',default=True)
    relations_only = fields.Boolean('Relations Only',default=False)
    set_inherited = fields.Boolean('Set as Inherit', default=True)
    exclude_auto_fields = fields.Boolean('Exclude Auto Fields', default=True)

    def _create_model_fields(self, module, model_items, model_map, relations_only=True):
      for record_id in self:
        return record_id.create_model_fields(
            module, model_items, model_map, 
            relations_only,record_id.set_inherited,record_id.exclude_auto_fields
            )

    def create_model_fields(self,  module, model_items, model_map, field_list=None, relations_only=True, set_inherited=False, exclude_auto_fields=True):
      for record_id in self:
        _review_models = []

        for model in model_items:
            module_model = self.env['builder.ir.model'].search([('module_id', '=', module.id), ('model', '=', model.model)])

            for field in model.field_id:
                if not set_inherited and exclude_auto_fields and field.name in AUTO_FIELDS:
                    continue
                if field_list and field.name not in field_list:
                    continue
                if not self.env['builder.ir.model.fields'].search([('model_id', '=', module_model.id), ('name', '=', field.name)]):
                    _logger.debug(field.name)
                    values = {
                        'module_id': model_map[model.model].module_id.id,
                        'model_id': model_map[model.model].id,
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
                            new_model = record_id.create_model(
                                model_map[model.model].module_id.id,m,False)
                            model_map[field.relation] = new_model
                            record_id.create_model_fields(
                                module, [m], model_map, None, 
                                False,False,exclude_auto_fields)                            
                        values.update({
                            'relation': field.relation,
                            'relation_model_id': model_map[field.relation].id,
                            'relation_field': field.relation_field,
                            'domain': field.domain,
                        })
                        _review_models.append(model)

                    if not relations_only or (relations_only and field.ttype in ['one2many', 'many2many', 'many2one']):
                        _logger.debug(values)
                        model_map[model.model].field_ids.create(values)
                        # if not field.name.startswith('_'):
                        #     model_map[model.model].update({'field_ids': [(0,0,values)]})

        if len(_review_models):
            record_id.create_model_fields(module, _review_models, model_map, field_list, relations_only,set_inherited,exclude_auto_fields)

    def create_model(self,module_id,model,set_inherited):
        model_obj = self.env['builder.ir.model']
        vals = {
            'module_id': module_id,
            'name': model.name,
            'model': model.model,
            'transient': model._transient == True,
            # 'inherit_model': self.set_inherited and model.model or False
        }
        _logger.debug(vals)
        new_model = model_obj.create(vals)
        if set_inherited:
            new_model['inherit_model_ids'] = [{'model_source': 'system', 'system_model_id': model.id, 'system_model_name': model.model}]
        return new_model

    def action_import(self):
        # model_obj = self.env['builder.ir.model']
      for record_id in self:
        model_map = {}

        module = self.env[self.env.context.get('active_model')].search([('id', '=', self.env.context.get('active_id'))])

        for model in module.model_ids:
            model_map[model.model] = model

        for model in record_id.model_ids:
            module_model = self.env['builder.ir.model'].search([('module_id', '=', module.id), ('model', '=', model.model)])

            if model.modules:
                module.add_dependency(model.modules.split(', ')[0])
            if not module_model.id:
                new_model = record_id.create_model(
                    self.env.context.get('active_id'),
                    model, record_id.set_inherited)
                model_map[model.model] = new_model

        if (record_id.set_inherited and not record_id.exclude_fields) or (not record_id.set_inherited and (record_id.create_fields or record_id.relations_only) ):
            # record_id._create_model_fields(module, record_id.model_ids, model_map, record_id.relations_only)
            for record in record_id.model_ids:
                model_map = model_map[record.model].model_fields_import(
                    record, model_map, relations_only=record_id.relations_only)
        model_src_map = {}
        for model_model,record in model_map.items():
            model_id = self.env['ir.model'].search([
                ('model','=', model_model)
            ])[0]
            if model_model not in model_src_map:
                model_src_map[model_model] = record.model_src_id = self.env['builder.ir.model'].create({
                    'module_id': 1,
                    'name': record.name,
                    'model': model_model,
                    'transient': model_id._transient == True,                    
                })
                model_src_map = model_src_map[model_model].model_fields_import(
                    model_id,model_src_map)                
        return {'type': 'ir.actions.act_window_close'}
