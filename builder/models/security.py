import logging
_logger = logging.getLogger(__name__)
__author__ = 'one'

# from odoo import models, api, fields, _
from odoo import models, fields
from odoo import SUPERUSER_ID
from odoo import _, api
from odoo.exceptions import ValidationError





class Groups(models.Model):
    _name = "builder.res.groups"
    _description = "Access Groups"
    _rec_name = 'full_name'
    _order = 'sequence, name'



    define = fields.Boolean('Defined',default=False)
    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    xml_id = fields.Char('XML ID', required=True)
    name = fields.Char('Name', required=True, translate=True,default='Default')
    # 'users=fields.Many2many('res.users', 'res_groups_users_rel', 'gid', 'uid', 'Users'),
    inherited = fields.Boolean('Inherited', default=False)
    is_portal = fields.Boolean('Portal',default=False)
    share = fields.Boolean('Share',default=False)
    sequence = fields.Integer('Sequence')
    model_access = fields.One2many('builder.ir.model.access', 'group_id', 'Access Controls', copy=True)
    rule_groups = fields.Many2many('builder.ir.rule', 'builder_rule_group_rel', 'group_id', 'rule_group_id', 'Rules',
                                   domain=[('global_', '=', False)])
    menu_access = fields.Many2many('builder.ir.ui.menu', 'builder_ir_ui_menu_group_rel', 'gid', 'menu_id',
                                   'Access Menu')
    view_access = fields.Many2many('builder.ir.ui.view', 'builder_ir_ui_view_group_rel', 'group_id', 'view_id', 'Views')
    comment = fields.Text('Comment', size=250, translate=True)
    category_type = fields.Selection([('custom', 'Custom'), ('module', 'Module'), ('system', 'System')],
                                     'Application Type')
    category_id = fields.Many2one('ir.module.category', 'System Application', index=True, ondelete='set null')
    category_ref = fields.Char('System Application Ref')
    full_name = fields.Char(compute='_get_full_name', string='Group Name',store=True)
    implied_ids = fields.Many2many('builder.res.groups', 'builder_res_groups_implied_rel', 'gid', 'hid',
                                   string='Inherits', help='Users of this group automatically inherit those groups')
    trans_implied_ids = fields.Many2many('builder.res.groups',compute='_get_trans_implied', type='many2many', relation='builder.res.groups',
                                         string='Transitively inherits')

    _sql_constraints = [
        ('name_uniq', 'unique (module_id, category_type, category_id, category_ref, name)',
         'The name of the group must be unique within an application!')
    ]

    @api.depends('category_id','category_type','category_ref','name')
    def _get_full_name(self):
        res = {}
        for g in self:
            if (g.category_type == 'system') and g.category_id:
                res[g.id] = '%s / %s' % (g.category_id.name, g.name)
            elif (g.category_type == 'system') and g.category_ref:
                res[g.id] = '%s / %s' % (g.category_ref, g.name)
            elif g.category_type == 'module':
                res[g.id] = "{module} / {group}".format(module=g.module_id.shortdesc, group=g.name)
            else:
                res[g.id] = g.name
            g.full_name = res[g.id]
        # return res
    
    @api.depends('implied_ids')
    def _get_trans_implied(self):
        "computes the transitive closure of relation implied_ids"
        memo = {}  # use a memo for performance and cycle avoidance

        def computed_set(g):
            if g not in memo:
                # raise
                memo[g] = set(g.implied_ids)
                for h in g.implied_ids:
                    computed_set(h).subsetof(memo[g])
            return memo[g]

        res = {}
        for g in self:
            g.trans_implied_ids = (6, 0, list(map(int, computed_set(g))))
        # return res

    @api.model
    def create(self,vals):
        vals2= {}
        try:
            group = vals.pop('id',False)
            if group and issubclass(type(group),models.Model):
                group_obj = self.env['builder.res.groups']
                # module = self.env[self.env.context.get('active_model')].search([('id', '=', self.env.context.get('active_id'))])
                module = vals.get('module_id')
                data = self.env['ir.model.data'].search([('model', '=', group._name), ('res_id', '=', group.id)])
                xml_id = "{module}.{id}".format(module=data.module, id=data.name)
                vals2 ={
                        'xml_id': xml_id,
                        'name': data.name,
                        'category_id': group.category_id.id,
                        # 'category_ref': m.category_id.id,
                        'comment': group.comment,
                        'is_portal': group.is_portal,
                        'share': group.share,
                        'sequence': group.sequence
                }                
        except:
            pass
        _logger.debug(vals2)
        _logger.debug(vals)
        vals2.update(vals) 
        _logger.debug(vals2)
        return super().create(vals2)

    def copy(self, default=None):
        # group_name = self.read(cr, uid, [id], ['name'])[0]['name']
        group_name = self.name
        default.update({'name': _('%s (copy)') % group_name})
        return super(Groups, self).copy(default)

    def write(self, vals):
        if 'name' in vals:
            if vals['name'].startswith('-'):
                raise osv.except_osv(_('Error'),
                                     _('The name of the group can not start with "-"'))
        res = super(Groups, self).write( vals)
        return res

    @api.onchange('category_ref')
    def onchange_category_ref(self):
        self.category_id = False
        if self.category_ref:
            self.category_id = self.env['ir.model.data'].xmlid_to_res_id(self.category_ref)

    @api.onchange('category_id')
    def onchange_category_id(self):
        if self.category_id:
            data = self.env['ir.model.data'].search(
                [('model', '=', 'ir.module.category'), ('res_id', '=', self.category_id.id)])
            self.category_ref = "{module}.{id}".format(module=data.module, id=data.name) if data.id else False

    @property
    def real_xml_id(self):
        return self.xml_id if self.inherited else '{module}.{xml_id}'.format(module=self.module_id.name,
                                                                             xml_id=self.xml_id)



class IrModelAccess(models.Model):
    _name = 'builder.ir.model.access'

    define = fields.Boolean('Defined',default=True)
    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    name = fields.Char('Name', required=True, index=True)
    model_id = fields.Many2one('builder.ir.model', 'Object', required=True, domain=[('transient', '=', False)],
                               index=True, ondelete='cascade')
    group_id = fields.Many2one('builder.res.groups', 'Group', ondelete='cascade', index=True)
    perm_read = fields.Boolean('Read Access')
    perm_write = fields.Boolean('Write Access')
    perm_create = fields.Boolean('Create Access')
    perm_unlink = fields.Boolean('Delete Access')

    # def create(self, cr, uid, vals, context=None):
    #     if not vals['module_id']:
    #         vals['module_id'] = self.pool['builder.ir.model'].search(cr, uid, [('id', '=', vals['model_id'])])


class IrRule(models.Model):
    _name = 'builder.ir.rule'
    _order = 'model_id, name'

    def _get_value(self):
        res = {}
        for rule in self:
            if not rule.groups:
                res[rule.id] = True
            else:
                res[rule.id] = False
        return res

    @api.constrains('module_id')
    def _check_model_obj(self):
        if any(rule.model_id.transient for rule in self):
            raise  ValidationError(_('Rules can not be applied on Transient models.'))
        if any(rule.model_id.model == 'ir.rule' for rule in self):
            raise ValidationError(_('Rules can not be applied on the Record Rules model.'))
             
    # def _check_model_name(self):
        # Don't allow rules on rules records (this model).
        # return not 

    define = fields.Boolean('Defined',default=True)
    system_id = fields.Integer('System ID')
    module_id = fields.Many2one('builder.ir.module.module', 'Module', ondelete='cascade')
    name = fields.Char('Name', index=1)
    model_id = fields.Many2one('builder.ir.model', 'Object', index=1, required=True, ondelete="cascade")
    global_ = fields.Boolean(compute=_get_value, string='Global', type='boolean', store=True,
                             help="If no group is specified the rule is global and applied to everyone")
    groups = fields.Many2many('builder.res.groups', 'builder_rule_group_rel', 'rule_group_id', 'group_id', 'Groups')
    domain = fields.Text('Domain')
    perm_read = fields.Boolean('Apply for Read',default=True)
    perm_write = fields.Boolean('Apply for Write',default=True)
    perm_create = fields.Boolean('Apply for Create',default=True)
    perm_unlink = fields.Boolean('Apply for Delete',default=True)

    _sql_constraints = [
        (
            'no_access_rights',
            'CHECK (perm_read!=False or perm_write!=False or perm_create!=False or perm_unlink!=False)',
            'Rule must have at least one checked access right !'),
    ]
    # _constraints = [
    #     (_check_model_obj, 'Rules can not be applied on Transient models.', ['model_id']),
    #     (_check_model_name, 'Rules can not be applied on the Record Rules model.', ['model_id']),
    # ]
