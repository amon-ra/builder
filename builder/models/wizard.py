from collections import defaultdict
import inspect


from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class IrModelWizard(models.Model):

    _name = 'builder.ir.model.wizard'

    _inherit = 'builder.ir.model'
