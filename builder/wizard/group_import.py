__author__ = 'one'

from odoo import models, api, fields, _
import logging

_logger = logging.getLogger(__name__)

class GroupImport(models.TransientModel):
    _name = 'builder.res.groups.import.wizard'

    group_ids = fields.Many2many('res.groups', 'builder_res_groups_import_wizard_group_rel', 'wizard_id', 'group_id', 'Groups')
    set_inherited = fields.Boolean('Set as Inherit', default=False)

    def action_import(self):
        _logger.debug("--IMPORT GROUP--")
        group_obj = self.env['builder.res.groups']
        _logger.debug(self.env.context.get('active_model'))
        module = self.env[self.env.context.get('active_model')].search([('id', '=', self.env.context.get('active_id'))])

        for obj in self:
            for group in obj.group_ids:
                data = self.env['ir.model.data'].search([('model', '=', group._name), ('res_id', '=', group.id)])
                xml_id = "{module}.{id}".format(module=data.module, id=data.name)
                _logger.debug(xml_id)
                module_group = self.env['builder.res.groups'].search(
                    [('module_id', '=', module.id), ('xml_id', '=', xml_id)])
                _logger.debug(module_group)
                if not module_group:
                    vals = {
                        'module_id': self.env.context.get('active_id'),
                        'name': group.name,
                        'inherited': obj.set_inherited,
                        'xml_id': xml_id,
                    }
                    _logger.debug(vals)
                    new_group = group_obj.create(vals)

        return {'type': 'ir.actions.act_window_close'}
