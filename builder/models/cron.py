import logging
# from odoo.addons.base.ir.ir_cron import str2tuple
from odoo.tools.safe_eval import safe_eval
import psycopg2
from datetime import datetime

from odoo import models, api, fields
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.safe_eval import safe_eval as eval
from odoo.tools.translate import _
from odoo.modules import load_information_from_description_file

from odoo import fields

_logger = logging.getLogger(__name__)

def str2tuple(s):
    return safe_eval('tuple(%s)' % (s or ''))

class ir_cron(models.Model):
    """ Model describing cron jobs (also called actions or tasks).
    """

    # TODO: perhaps in the future we could consider a flag on ir.cron jobs
    # that would cause database wake-up even if the database has not been
    # loaded yet or was already unloaded (e.g. 'force_db_wakeup' or something)
    # See also openerp.cron

    _name = "builder.ir.cron"
    _order = 'name'
    module_id=fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    name=fields.Char('Name', default=1,required=True)
    active=fields.Boolean('Active')
    interval_number=fields.Integer('Interval Number',default=1,help="Repeat every x.")
    interval_type=fields.Selection( [('minutes', 'Minutes'),
        ('hours', 'Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Interval Unit',default='months')
    numbercall=fields.Integer('Number of Calls', default=1,help='How many times the method is called,\na negative number indicates no limit.')
    doall= fields.Boolean('Repeat Missed', help="Specify if missed occurrences should be executed when the server restarts.")
    nextcall= fields.Datetime('Next Execution Date', help="Next planned execution date for this job.")
    model_id=fields.Many2one('builder.ir.model', 'Object', help="Model name on which the method to be called is located, e.g. 'res.partner'.")
    model_method_id=fields.Many2one('builder.ir.model.method', 'Method', help="Name of the method to be called when this job is processed.")
    args=fields.Text('Arguments', help="Arguments to be passed to the method, e.g. (uid,).")
    priority=fields.Integer('Priority', default=5,help='The priority of the job, as an integer: 0 means higher priority, 10 means lower priority.')

    @api.constrains('args')
    def _check_args(self, ids):
        try:
            for this in self.browse(ids):
                str2tuple(this.args)
        except Exception:
            return False
        return True

    @api.model
    def toggle(self,  model, domain):
        active = bool(self.env[model].search_count(domain))

        return self.try_write({'active': active})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: