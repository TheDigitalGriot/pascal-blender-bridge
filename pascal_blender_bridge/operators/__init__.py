import bpy

from .export_operator import PASCAL_OT_export
from .import_operator import PASCAL_OT_import


classes = (
    PASCAL_OT_export,
    PASCAL_OT_import,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
