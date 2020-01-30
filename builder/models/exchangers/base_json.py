from collections import defaultdict
import json
import base64
from psycopg2._psycopg import IntegrityError
from odoo.exceptions import except_orm
from odoo import models, api

import logging
_logger = logging.getLogger(__name__)

class OdooBuilderTranslator(object):
    def __init__(self):
        self.seen_models = set()
        self.data_files = set()

    def get_files(self):
        return self.data_files

    def translate(self, obj):
        if isinstance(obj, models.Model):
            instance = {'@model': obj._name, '@id': obj.id}
            obj_id = obj._name, obj.id
            if obj.id and obj_id not in self.seen_models:
                # if obj._name.startswith('builder.data.file'):
                #     self.data_files.add(obj)
                if obj._name.startswith('builder.'):
                    self.seen_models.add(obj_id)
                    for name, column in list(obj._fields.items()):
                        _logger.debug(name)
                        _logger.debug(column)
                        _logger.debug(column.type)
                        if name in ['id', 'write_uid', 'write_date', 'create_date', 'create_uid']:
                            continue
                        if column.type in ['function'] or getattr(column, '_fnct', False) or not getattr(column, 'store', True):
                            continue
                        if column.type in ['char', 'boolean', 'integer', 'text', 'html', 'float', 'date', 'datetime', 'selection' ]:
                            instance[name] = getattr(obj, name)
                        elif column.type in ['binary']:
                            value = getattr(obj, name)
                            if value:
                                value = '#__BINARY__'+base64.encodebytes(value).decode('ascii')
                                #base64.decodebytes(data2['body'].encode('ascii'))                     
                                instance[name] = value
                        else:
                            instance[name] = getattr(self, 'handle_model_{type}'.format(type=column.type))(obj, name)
            return instance if obj.id else False
        return obj

    def handle_model_one2many(self, obj, name):
        return [
            self.translate(item)
            for item in getattr(obj, name)
        ]

    def handle_model_many2many(self, obj, name):
        return [
            self.translate(item)
            for item in getattr(obj, name)
        ]

    def handle_model_many2one(self, obj, name):
        return self.translate(getattr(obj, name))

    def handle_model_reference(self, obj, name):
        return self.translate(getattr(obj, name))


def model_required_attributes(model):
    columns = model._fields
    return {
        name
        for name, column in list(columns.items())
        if getattr(column, 'required', False) and getattr(column, 'store', True) and not getattr(column, 'compute', False)
    }

    # oondeo returns a set (FIX)
    # _logger.debug(model.name)
    # return { record.name for record in model if record and record.required and not record.allow_compute}


class OdooBuilderLoader(object):
    def __init__(self, env=None):
        self.seen_models = {}
        self.env = env

    def get_objects(self, data, pack=None):
        pack = pack or defaultdict(dict)
        if isinstance(data, dict):
            if '@model' in data and '@id' in data:
                model_str = data['@model']
                id_str = data['@id']
                pack[model_str, id_str].update({
                    key: value if not isinstance(value, dict) else {
                        '@model': value.get('@model'),
                        '@id': value.get('@id'),
                    }
                    for key, value in list(data.items())
                    if key not in ['@model', '@id']
                })
            [
                self.get_objects(data[attr], pack)
                for attr in data
            ]
        elif isinstance(data, list):
            [
                self.get_objects(item, pack)
                for item in data
            ]
        return pack

    def create_objects(self, objects):
        changes = True

        while objects and changes:
            changes = False
            for obj_key in list(objects.keys()):
                model_str, id_str = obj_key
                model = self.env[model_str]
                data = objects[obj_key]
                missing = [
                    key for key, value in list(data.items()) if isinstance(value, dict) and value['@model'].startswith('builder.') and not self.seen_models.get((value['@model'], value['@id']))
                ]

                required_attributes = model_required_attributes(model)
                #_logger.debug(required_attributes)
                if required_attributes.issubset(set(data.keys())) and not missing:
                    d= {}
                    for key, value in list(data.items()):
                        if isinstance(value, list):
                            continue
                        if isinstance(value, dict):
                            # if model._fields[key].related:
                            #     value = '{model},{id}'.format(model=value['@model'],
                            #                     id=self.seen_models.get(
                            #                         (value['@model'],
                            #                         value['@id'])))
                            # else:
                            value = self.seen_models.get((value['@model'], value['@id']))
                        if isinstance(value,str) and value.startswith('#__BINARY__'):
                            value=base64.decodebytes(value[11:].encode('ascii'))
                        d[key]=value

                    _logger.debug(d)
                    if d:
                        obj = model.create(d)
                    if obj:
                        self.seen_models[obj_key] = obj.id
                        changes = True
                        objects.pop(obj_key)

    def get_object(self, data):
        return self.seen_models[data['@model'], data['@id']]

    def build_relations(self, data):
        if data and isinstance(data, dict):
            if '@model' in data and '@id' in data:
                model_str = data['@model']
                id_str = data['@id']
                model = self.env[model_str]
                obj = self.seen_models[model_str, id_str]
                columns = model._fields
                for attr in list(data.keys()):
                    if attr in columns:
                        #_logger.debug(dir(columns[attr]))
                        if columns[attr].type == 'many2many':
                            obj.write({
                                attr: [[6, False, [self.get_object(item).id for item in data[attr]]]]
                            })

    def load(self, data):
        objects = self.get_objects(data)
        self.create_objects(objects)
        self.build_relations(data)


class JSONExchanger(models.Model):
    _name = 'builder.exchanger.json'
    _inherit = ['builder.exchanger.base']
    _description = 'Odoo Builder JSON'

    @api.model
    def get_extension(self):
        return 'builder'

    @api.model
    def get_export_module_filename(self, module):
        return '{name}.json'.format(name=module.name)

    @api.model
    def export_module(self, module):
        translator = OdooBuilderTranslator()
        ret = translator.translate(module)
        _logger.debug(ret)
        return json.dumps(ret, sort_keys=True, indent=4)

    @api.model
    def load_module(self, module):
        try:
            module = str(module,'utf-8')
        except:
            pass
        data = json.loads(module)
        translator = OdooBuilderLoader(self.env)
        translator.load(data)
