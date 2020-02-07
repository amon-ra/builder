
from datetime import datetime

from odoo import models, api, fields, _, SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.safe_eval import safe_eval as eval
from odoo.tools.translate import _
from odoo.modules import load_information_from_description_file

__author__ = 'one'


class actions(models.Model):
    _name = 'builder.ir.actions.actions'
    _table = 'builder_ir_actions'
    _order = 'name'
    module_id=fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')

    model_id = fields.Many2one('builder.ir.model',
                               'Model',
                               ondelete='cascade')
    xml_id=fields.Char('XML ID', required=True, translate=True)
    name=fields.Char('Name', required=True)
    type=fields.Char('Action Type', required=True)
    usage=fields.Char('Action Usage',default=lambda *a: False)

    help=fields.Text('Action description',
                        help='Optional help text for the users with a description of the target view, such as its usage and purpose.',
                        translate=True)

    @property
    def real_xml_id(self):
        return self.xml_id if '.' in self.xml_id else '{module}.{xml_id}'.format(module=self.module_id.name,
                                                                                 xml_id=self.xml_id)


class ir_actions_act_url(models.Model):
    _name = 'builder.ir.actions.act_url'
    _table = 'builder_ir_act_url'
    _inherit = 'builder.ir.actions.actions'
    _sequence = 'builder_ir_actions_id_seq'
    _order = 'name'

    type = fields.Char('Action Type', required=True,
        default='builder.ir.actions.act_url')
    url=fields.Text('Action URL', required=True)
    target=fields.Selection((
        ('new', 'New Window'),
        ('self', 'This Window')),
        'Action Target', required=True, default='new'
    )



class ir_actions_act_window(models.Model):
    _name = 'builder.ir.actions.act_window'
    _table = 'builder_ir_act_window'
    _inherit = 'builder.ir.actions.actions'
    _sequence = 'builder_ir_actions_id_seq'

    # @api.constrains('res_model','src_model')
    def _check_model(self):
        for action in self:
            if action.res_model not in self.pool:
                return False
            if action.src_model and action.src_model not in self.pool:
                return False
        return True

    def _views_get_fnc(self):
        """Returns an ordered list of the specific view modes that should be
           enabled when displaying the result of this action, along with the
           ID of the specific view to use for each mode, if any were required.

           This function hides the logic of determining the precedence between
           the view_modes string, the view_ids o2m, and the view_id m2o that can
           be set on the action.

           :rtype: dict in the form { action_id: list of pairs (tuples) }
           :return: { action_id: [(view_id, view_mode), ...], ... }, where view_mode
                    is one of the possible values for ir.ui.view.type and view_id
                    is the ID of a specific view to use for this mode, or False for
                    the default one.
        """
        res = {}
        for act in self:
            res[act.id] = [(view.view_id.id, view.view_mode) for view in act.view_ids]
            view_ids_modes = [view.view_mode for view in act.view_ids]
            modes = act.view_mode.split(',')
            missing_modes = [mode for mode in modes if mode not in view_ids_modes]
            if missing_modes:
                if act.view_id and act.view_id.type in missing_modes:
                    # reorder missing modes to put view_id first if present
                    missing_modes.remove(act.view_id.type)
                    res[act.id].append((act.view_id.id, act.view_id.type))
                res[act.id].extend([(False, mode) for mode in missing_modes])
        return res

    def _search_view(self):
        res = {}
        for act in self:
            field_get = self.pool[act.res_model].fields_view_get(
                                                                 act.search_view_id and act.search_view_id.id or False,
                                                                 'search')
            res[act.id] = str(field_get)
        return res


    view_id=fields.Many2one('builder.ir.ui.view', 'View Ref.', ondelete='set null')
    domain=fields.Char('Domain Value',
                          help="Optional domain filtering of the destination data, as a Python expression")
    context=fields.Char('Context Value', required=True,
                           help="Context dictionary as Python expression, empty by default (Default: {})")
    res_id=fields.Integer('Record ID',
                             help="Database ID of record to open in form view, when ``view_mode`` is set to 'form' only")
    model_id=fields.Many2one('builder.ir.model', 'Destination Model', required=True, ondelete='cascade',
                                help="Model name of the object to open in the view window")
    src_model=fields.Char('Source Model',
                             help="Optional model name of the objects on which this action should be visible")
    target=fields.Selection([('current', 'Current Window'), ('new', 'New Window'), ('inline', 'Inline Edit'),
                                ('inlineview', 'Inline View')], 'Target Window')
    view_mode=fields.Char('View Mode', required=True,
                             help="Comma-separated list of allowed view modes, such as 'form', 'tree', 'calendar', etc. (Default: tree,form)")
    view_type = fields.Selection(
        (('tree', 'Tree'), ('form', 'Form')),
        string='View Type',
        required=True,
        help=
        "View type: Tree type to use for the tree view, set to 'tree' for a hierarchical tree view, or 'form' for a regular list view"
    )
    usage=fields.Char('Action Usage',
                         help="Used to filter menu and home actions from the user form.")
    view_ids=fields.One2many('ir.actions.act_window.view', 'act_window_id', 'Views', copy=True)
    views=fields.Binary(compute=_views_get_fnc, type='binary', string='Views',
                             help="This function field computes the ordered list of views that should be enabled " \
                                  "when displaying the result of an action, federating view mode, views and " \
                                  "reference view. The result is returned as an ordered list of pairs (view_id,view_mode).")
    limit=fields.Integer('Limit', help='Default limit for the list view')
    auto_refresh=fields.Integer('Auto-Refresh', help='Add an auto-refresh on the view')
    # 'groups_id=fields.Many2many('res.groups', 'ir_act_window_group_rel', 'act_id', 'gid', 'Groups'),
    groups_id=fields.Many2many('builder.res.groups', 'builder_ir_act_window_group_rel',
                                  'act_id', 'gid', 'Groups')
    search_view_id=fields.Many2one('builder.ir.ui.view', 'Search View Ref.')
    filter=fields.Boolean('Filter')
    auto_search=fields.Boolean('Auto Search')
    # 'search_view' : fields.function(_search_view, type='text', string='Search View'),
    multi=fields.Boolean('Restrict to lists',
                            help="If checked and the action is bound to a model, it will only appear in the More menu on list views")
    show_help=fields.Boolean('Display Help')
    help=fields.Html('Help')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['type'] = 'builder.ir.actions.act_window'
        res['view_type'] = 'form'
        res['view_mode'] = 'tree,form'
        res['context'] = '{}'
        res['limit'] = 80
        res['target'] = 'current'
        res['auto_refresh'] = 0
        res['auto_search'] = True
        res['multi'] = False
        res['help'] = """
          <p class="oe_view_nocontent_create">
            Click to create a new model.
          </p><p>
            This is an example of help content.
          </p>
        """
        return res

    @api.onchange('model_id')
    def onchange_model_id(self):
        if not self.name and self.model_id:
            self.xml_id = "act_{model}".format(model=self.model_id.model.replace('.', '_'))
            self.name = self.model_id.name

        if self.model_id:
            available_view_types = list(set([view.type for view in self.model_id.view_ids]) - {'search'})
            self.view_mode = ','.join(available_view_types)

    def for_xml_id(self, module, xml_id):
        """ Returns the act_window object created for the provided xml_id

        :param module: the module the act_window originates in
        :param xml_id: the namespace-less id of the action (the @id
                       attribute from the XML file)
        :return: A read() view of the ir.actions.act_window
        """
        dataobj = self.pool.get('ir.model.data')
        data_id = dataobj._get_id(module, xml_id)
        res_id = dataobj.browse([data_id]).res_id
        return self.browse([res_id])[0]



class ir_actions_act_server(models.Model):
    _name = 'builder.ir.actions.server'
    _table = 'builder_ir_act_server'
    _inherit = 'builder.ir.actions.actions'
    _sequence = 'builder_ir_actions_id_seq'


class ir_actions_act_report(models.Model):
    _name = 'builder.ir.actions.report'
    _table = 'builder_ir_act_report'
    _inherit = 'builder.ir.actions.actions'
    _sequence = 'builder_ir_actions_id_seq'    

class ir_actions_act_client(models.Model):
    _name = 'builder.ir.actions.client'
    _table = 'builder_ir_act_client'
    _inherit = 'builder.ir.actions.actions'
    _sequence = 'builder_ir_actions_id_seq'       


def str2tuple(s):
    return eval('tuple(%s)' % (s or ''))

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
