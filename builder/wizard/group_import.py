__author__ = 'one'

from odoo import models, api, fields, _


class GroupImport(models.TransientModel):
    _name = 'builder.res.groups.import.wizard'

    group_ids = fields.Many2many('res.groups', 'builder_res_groups_import_wizard_group_rel', 'wizard_id', 'group_id', 'Groups')
    set_inherited = fields.Boolean('Set as Inherit', default=True)

    def action_import(self):
        for obj in self:
            group_obj = obj.env['builder.res.groups']
            module = obj.env[obj.env.context.get('active_model')].search([('id', '=', obj.env.context.get('active_id'))])

            for group in obj.group_ids:
                data = obj.env['ir.model.data'].search([('model', '=', group._name), ('res_id', '=', group.id)])
                xml_id = "{module}.{id}".format(module=data.module, id=data.name)

                module_group = obj.env['builder.res.groups'].search([('module_id', '=', module.id), ('xml_id', '=', xml_id)])

                if not module_group.id:
                    new_group = group_obj.create({
                        'module_id': obj.env.context.get('active_id'),
                        'name': group.name,
                        'inherited': obj.set_inherited,
                        'xml_id': xml_id,
                    })

        return {'type': 'ir.actions.act_window_close'}