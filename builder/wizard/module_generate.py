from odoo import models, api, fields, _


class ModuleGenerate(models.TransientModel):
    _name = 'builder.ir.module.module.generate.wizard'

    @api.model
    def _get_generators(self):
        return self.env['builder.generator.base'].get_generators()

    @api.model
    def _get_default_exporter(self):
        generators = self.env['builder.generator.base'].get_generators()
        if generators:
            return generators[0][0]
            
    generator = fields.Selection(_get_generators, 'Version',default=_get_default_exporter, required=True)



    
    def action_generate(self):
        ids = self.env.context.get('active_ids') or ([self.env.context.get('active_id')] if self.env.context.get('active_id') else [])

        return {
            'type': 'ir.actions.act_url',
            'url': '/builder/generate/{generator}/{ids}'.format(ids=','.join([str(i) for i in ids]), generator=self.generator),
            'target': 'self'
        }
