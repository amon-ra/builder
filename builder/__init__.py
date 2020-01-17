__author__ = 'one'

from . import graph; graph.monkey_patch()
from . import models
from . import wizard
from . import controllers
from . import tests
from odoo.api import Environment, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env['builder.ir.module.module'].create({
        'id': 1,
        'name': 'builder_system',
        'shortdesc': 'builder_system',
        'author': 'builder'
    })
