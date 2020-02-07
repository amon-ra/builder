import random
import string

__author__ = 'one'

from odoo import models, api, fields, _


class BinaryGenerator(models.Model):
    _name = 'builder.ir.model.demo.generator.binary'
    _description = 'Binary Generator'
    _inherits = {
        'builder.ir.model.demo.generator': 'base_id'
    }
    _inherit = ['ir.mixin.polymorphism.subclass', 'builder.ir.model.demo.generator.base']
    _target_type = 'date'

    base_id = fields.Many2one(
        comodel_name='builder.ir.model.demo.generator',
        string='Base',
        ondelete='cascade',
        required=True
    )

    file_ids = fields.Many2many('builder.data.file', 'builder_ir_model_demo_generator_binary_files_rel', 'generator_id', 'data_id', 'Files')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['subclass_model']= self._name
        return res  

    
    def get_generator(self, field):
        while True:
            if self.base_id.generate_null_values(field):
                yield False
            else:
                yield random.choice([f.path for f in self.file_ids])
