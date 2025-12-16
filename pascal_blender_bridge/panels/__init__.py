import bpy

from .main_panel import (
    PASCAL_PT_main_panel,
    PASCAL_PT_object_panel,
    PASCAL_PT_settings_panel,
)


classes = (
    PASCAL_PT_main_panel,
    PASCAL_PT_object_panel,
    PASCAL_PT_settings_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
