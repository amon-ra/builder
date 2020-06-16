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
import inspect
import sys
import os 

class PythonFile(models.Model):
    _name = 'builder.python.file'


    parent = fields.Char('Path')
    name = fields.Char('Name', required=True)
    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    custom_code_line_ids = fields.One2many('builder.python.file.line','python_file_id', 'Code', copy=True)
    import_ids = fields.One2many('builder.python.file.import', 'python_file_id', 'Imports', copy=True)

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

    
    class_code = fields.Boolean('Inside Class',default=False)

    @api.model
    def create(self,vals):
        # PythonFile
        name = vals.get('name')
        field = 'python_file_id'
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


class PythonImports(models.Model):
    _name = 'builder.python.file.import'
    _order = 'sequence,id'
    
    sequence = fields.Integer('Sequence')
    parent = fields.Char(string='Parent')
    name = fields.Char(string='Name', required=True)
    python_file_id = fields.Many2one('builder.python.file', 
                                string="Custom Code",ondelete='cascade')

    @api.model
    def create(self, vals):
        #Return record if exists: Singleton
        name = vals.get('name')
        # module = vals.get('module_id')
        import_ref = 'python_file_id'
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

class PythonFileDecorator(models.Model):
    _name = 'builder.python.file.decorator'

    name = fields.Char(string='Name', required=True)
    # arguments = fields.Char(string='Arguments', default='')
    method_id = fields.Many2one('builder.python.file.method',ondelete='cascade')

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


class PythonFileMethod(models.Model):
    _name = 'builder.python.file.method'

    _order = 'sequence, id'
    # define = fields.Boolean("Redefined",default=True)
    # inherit_model_mame = fields.Char('Parent Model')

    sequence = fields.Integer('Sequence', default=60)
    decorator_ids = fields.One2many('builder.python.file.decorator','method_id',string='Decorators')
    name = fields.Char(string='Name', required=True)
    arguments = fields.Char(string='Arguments', default='')

    use_cache = fields.Boolean('Use Cache', default=False)
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

    # @api.model
    # def create(self, vals):
    #     #Return record if exists
    #     name = vals.get('name')
    #     module = vals.get('module_id',False)
    #     model = vals.get('model_id')
    #     if not module:
    #         model_id = self.env['builder.ir.model'].browse([model])
    #         module = model_id.module_id.id
    #         vals['module_id'] = module                     
    #     if module and model and name:
    #         record_id = self.search([
    #             ('module_id','=', module),
    #             ('model_id','=', model),
    #             ('name','=', name)
    #         ])
    #         if record_id:
    #             record_id.write(vals)
    #             return record_id
    #     return super().create(vals)

    @api.depends('name')
    def _get_parent_code(self):
        for record in self:
            if record.model_id and record.name:
                obj = self.env.get(record.model_id.model)
                if obj:
                    record.parent_code,_ = get_parent_source(
                        self.env[record.model_id.model],
                        record.name
                    )

    @api.depends('name')
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

