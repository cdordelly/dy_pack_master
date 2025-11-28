bl_info = {
    "name": "dy Pack Master",
    "author": "Carlos Dordelly - @cdordelly",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > UI > dy Pack Master",
    "description": "Make Blender project files portable for render farms by localizing assets, addons, and dependencies.",
    "warning": "",
    "doc_url": "https://github.com/cdordelly/dy_pack_master",
    "category": "System",
}

from .scripts import ui
from .scripts import modules
from .scripts import pack_project

def register():
    modules.register()
    pack_project.register()
    ui.register()

def unregister():
    ui.unregister()
    pack_project.unregister()
    modules.unregister()
