bl_info = {
    "name": "dy Pack Master",
    "author": "Carlos Dordelly - @cdordelly",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > UI > dy Pack Master",
    "description": "Make Blender projects portable for render farms by localizing assets, addons, and dependencies.",
    "warning": "",
    "doc_url": "https://github.com/cdordelly/dy_pack_master",
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
