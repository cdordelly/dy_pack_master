from . import mesh_sequence_cache
from . import vdb
from . import references
from . import ocio
from . import addons
from . import report
from . import render_settings
from . import images
from . import movies

modules = (
    mesh_sequence_cache,
    vdb,
    references,
    ocio,
    addons,
    report,
    render_settings,
    images,
    movies,
)

def register():
    for mod in modules:
        mod.register()

def unregister():
    for mod in reversed(modules):
        mod.unregister()