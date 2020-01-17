# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError
from odoo import models
import sys
import os 

class PythonFile(models.Model):
    _name = 'builder.python.file'


    parent = fields.Char('Path')
    name = fields.Char('Name', required=True)
    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    custom_code_line_ids = fields.One2many('builder.python.file.line','python_file_id', 'Code', copy=True)
    import_ids = fields.One2many('builder.ir.model.import', 'python_file_id', 'Imports', copy=True)

    @api.model
    def create(self,vals):
        # PythonFile
        name = vals.get('name')
        module = vals.get('module_id')
        if name and module:
            record_id = self.search([
                    ('module_id','=',module),
                    ('name','=',name),
                ])
            if record_id:
                record_id.write(vals)
                return record_id
        return super().create(self,vals)

class PythonFileLine(models.Model):
    _name = 'builder.python.file.line'
    _order = 'sequence,id'

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name',required=True)
    # module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    custom_code = fields.Text('Custom code')
    docs = fields.Text('Custom code')
    comments = fields.Text('Custom code')
    
    python_file_id = fields.Many2one('builder.python.file', 
                                string="Custom Code",ondelete='cascade')    

    model_id = fields.Many2one('builder.ir.model', 'Model', ondelete='cascade')
    class_code = fields.Boolean('Inside Class',default=False)

    @api.model
    def create(self,vals):
        # PythonFile
        name = vals.get('name')
        field = 'python_file_id'
        model = vals.get(field)
        if not model:
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
        return super().create(self,vals)
