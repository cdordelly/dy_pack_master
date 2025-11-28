bl_info = {
    "name": "dy Pack Master",
    "author": "Dyne",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > UI > dy Pack Master",
    "description": "Make Blender projects portable for render farms by localizing assets, addons, and dependencies.",
    "warning": "",
    "doc_url": "",
    "category": "System",
}

from . import ui
from . import modules

def register():
    modules.register()
    ui.register()

def unregister():
    ui.unregister()
    modules.unregister()
