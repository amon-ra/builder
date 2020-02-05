__author__ = 'one'

import io
from base64 import decodestring, encodestring
import zipfile
from odoo import models, api, fields, _
import posixpath


class ModuleImport(models.TransientModel):
    _name = 'builder.data.import.wizard'

    path_prefix = fields.Char('Path Prefix')
    file = fields.Binary('File', required=True)

    def action_import(self):
      for record_id in self:
        f = io.BytesIO()
        f.write(decodestring(record_id.file))
        zfile = zipfile.ZipFile(f)
        # print(record_id.env.context)

        module = self.env[self.env.context.get('active_model')].search([('id', '=', self.env.context.get('active_id'))])

        for zitem in zfile.filelist:
            if not zitem.orig_filename.endswith('/'):
                result = module.data_file_ids.create({
                    'path': posixpath.join('/', record_id.path_prefix or '', zitem.orig_filename),
                    'content': encodestring(zfile.read(zitem)),
                    'module_id': self.env.context.get('active_id')
                })

        return {'type': 'ir.actions.act_window_close'}
