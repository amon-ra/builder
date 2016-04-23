from openerp import models, api, fields, _


class ModuleGenerate(models.TransientModel):
    _name = 'builder.ir.module.module.generate.wizard'

    @api.model
    def _get_generators(self):
        return self.env['builder.generator.base'].get_generators()

    generator = fields.Selection(_get_generators, 'Version', required=True)

    @api.model
    def _get_default_exporter(self):
        generators = self.env['builder.generator.base'].get_generators()
        if generators:
            return generators[0][0]

    _defaults = {
        'generator': _get_default_exporter
    }

    @api.multi
    def action_generate(self):
        ids = self.env.context.get('active_ids') or ([self.env.context.get('active_id')] if self.env.context.get('active_id') else [])

        return {
            'type': 'ir.actions.act_url',
            'url': '/builder/generate/{generator}/{ids}'.format(ids=','.join([str(i) for i in ids]), generator=self.generator),
            'target': 'self'
        }

    @api.multi
    def action_create(self):
        ids = self.env.context.get('active_ids') or ([self.env.context.get('active_id')] if self.env.context.get('active_id') else [])
        modules = self.search([
            ('id', 'in', ids)
        ])
        #filename = "{name}.{ext}".format(name=modules[0].name if len(modules) == 1 else 'modules', ext="zip")

        self.env[self.generator].create_modules(modules)

        return {'type': 'ir.actions.act_window_close'}
