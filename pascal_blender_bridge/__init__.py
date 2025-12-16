bl_info = {
    "name": "Pascal Blender Bridge",
    "author": "Community",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Pascal",
    "description": "Two-way sync between Blender and Pascal scene editor",
    "doc_url": "https://github.com/wawa-sensei/pascal",
    "category": "Import-Export",
}

import bpy

from . import operators
from . import panels
from . import properties


def register():
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()
