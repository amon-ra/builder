from odoo import models, fields, api
from odoo.api import Environment

__author__ = 'deimos'

import logging
_logger = logging.getLogger(__name__)


class Superclass(models.AbstractModel):
    _name = 'ir.mixin.polymorphism.superclass'

    subclass_id = fields.Integer('Subclass ID', compute='_compute_res_id')
    subclass_model = fields.Char("Subclass Model", required=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['subclass_model']= self._name
        return res  

    def _compute_res_id(self):
      for record_id in self:
        _logger.debug(record_id.subclass_model)
        _logger.debug(record_id._name)
        _logger.debug(record_id.name)
        if record_id.subclass_model == record_id._name:
            record_id.subclass_id = record_id.id
        else:
            subclass_model = record_id.env[record_id.subclass_model]
            attr = subclass_model._inherits.get(record_id._name)
            if attr:
                record_id.subclass_id = subclass_model.search([
                    (attr, '=', record_id.id)
                ]).id
            else:
                record_id.subclass_id = record_id.id

    # def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
    #     record = self.browse(cr, uid, 2, context=context)
    #     if self._name == record.subclass_model:
    #         view = super(Superclass, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
    #     else:
    #         view = self.pool.get(record.subclass_model).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
    #     return view

    def get_formview_action(self, access_uid=None):
        """
        @return <ir.actions.act_window>
        """
        id = access_uid[0] if isinstance(access_uid, list) else access_uid
        record = self.browse([id])[0]
        if not record.subclass_model:
            return super(Superclass, self).get_formview_action( id)

        create_instance = False
        instance = False
        # try:
        if not record.subclass_id:
            create_instance = True
        # except:
        #     create_instance = True

        if create_instance:
            # env = Environment(cr, uid, context)
            # env[record.subclass_model].create_instance(id[0] if isinstance(id, list) else id)
            # env = self.env[record.subclass_model].with_env()
            # env.create_instance(id[0] if isinstance(id, list) else id)
            instance = self.env[record.subclass_model].create(record.copy_data()[0])
            # instance.save()

        if self._name == record.subclass_model:
            view = super(Superclass, self).get_formview_action( id)
        else:
            if not instance:
                instance = self.env[record.subclass_model].browse([record.subclass_id])
            view = instance.get_formview_action(instance.id)
            # view = instance.get_formview_action( record.subclass_id)

        return view

    def get_instance(self):
      for record_id in self:
        return self.env[record_id.subclass_model].browse(record_id.subclass_id)

    @property
    def instance(self):
        return self.env[self.subclass_model].browse(self.subclass_id)

    @api.model
    def create_instance(self, id):
        raise NotImplementedError

    
    def action_edit(self):
        cr, uid, cxt = self.env.args
        data = self.get_formview_action(self.id)
        return data


class Subclass(models.AbstractModel):
    _name = 'ir.mixin.polymorphism.subclass'

    def get_formview_id(self,access_uid=None):
        view = self.env.get('ir.ui.view').search([
            ('type', '=', 'form'),
            ('model', '=', self._name)
        ])
        return view[0].id if len(view) else False

    def unlink(self):
        records = self
        parent_ids = {
            model: [rec[field].id for rec in records] for model, field in list(self._inherits.items())
        }

        res = super(Subclass, self).unlink()
        if res:
            for model in parent_ids:
                self.pool.get(model).browse(parent_ids.get(model, [])).unlink()
        return res
