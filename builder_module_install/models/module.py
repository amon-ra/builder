from io import BytesIO
from openerp.release import version_info

__author__ = 'one'
from openerp import models, fields, api, _


class Module(models.Model):
    _inherit = 'builder.ir.module.module'

    system_module_state = fields.Char('Module State', compute='_compute_system_module_state')

    @api.one
    def _compute_system_module_state(self):
        module = self.env['ir.module.module'].search([('name', '=', self.name)])
        if module.id:
            self.system_module_state = module.state
        else:
            self.system_module_state = 'missing'

    @api.multi
    def button_install(self, force=False):
        try:

            generator = self.env['builder.generator.v{v}'.format(v=version_info[0])]
            module_obj = self.env['ir.module.module']
            zfileIO = generator.get_zipped_modules([self])

            fp = BytesIO()
            fp.write(zfileIO.getvalue())
            res = module_obj.import_zipfile(fp, force=force)

            return {'type': 'ir.actions.act_window_close'}
        except KeyError, e:
            raise UserWarning(_('Module Builder does not provide a generator for your current odoo version.'))

    @api.multi
    def button_upgrade(self):
        self.button_install(True)

    @api.multi
    def button_uninstall(self):
        module = self.env['ir.module.module'].search([('name', '=', self.name)])
        if module.id:
            return module.button_uninstall()

        return {'type': 'ir.actions.act_window_close'}