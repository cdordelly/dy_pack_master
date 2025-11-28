from . import alembic
from . import vdb
from . import references
from . import ocio
from . import addons
from . import report
from . import render_settings

modules = (
    alembic,
    vdb,
    references,
    ocio,
    addons,
    report,
    render_settings,
)

def register():
    for mod in modules:
        mod.register()

def unregister():
    for mod in reversed(modules):
        mod.unregister()
