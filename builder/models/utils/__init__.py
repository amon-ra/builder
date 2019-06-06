import types,inspect
from odoo import api
from odoo import fields as fields_old

import logging
_logger = logging.getLogger(__name__)

def simple_selection(model, value_field, label_field=None, domain=None):
    domain = domain or []
    label_field = label_field or value_field

    @api.model
    def _selection_function(self):
        return [(getattr(c, value_field), getattr(c, label_field)) for c in self.env[model].search(domain)]
    return _selection_function


def get_field_types(model):
    context = {}
    # Avoid too many nested `if`s below, as RedHat's Python 2.6
    # break on it. See bug 939653.
    # for k, v in fields_old.__dict__.items():
    #     _logger.debug(k)
    #     _logger.debug(v)
    #     _logger.debug(inspect.isclass(v) and issubclass(v, fields_old.Field))

    # raise "dd"
    r =  sorted([
        (k.lower(), k.lower()) for k, v in fields_old.__dict__.items()
        if k != "Field" and \
        inspect.isclass(v) and issubclass(v, fields_old.Field) \
        # and not v._deprecated 
        # and not issubclass(v, fields_old.function)])
        # and not issubclass(v, fields_old.function)
        and (not context.get('from_diagram', False) or (
            context.get('from_diagram', False) and (k in ['One2many', 'Many2one', 'Many2many'])))
    ])
    _logger.debug(r)
    return r
