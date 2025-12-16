"""
Pascal Blender Bridge UI panels.
"""

import bpy
from bpy.types import Panel


class PASCAL_PT_main_panel(Panel):
    """Main Pascal Bridge panel in the 3D View sidebar."""
    bl_label = "Pascal Bridge"
    bl_idname = "PASCAL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pascal"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.pascal_bridge

        # Export section
        box = layout.box()
        box.label(text="Export / Import", icon='IMPORT')

        row = box.row(align=True)
        row.scale_y = 1.5
        row.operator("pascal.export", text="Export to Pascal", icon='EXPORT')

        row = box.row(align=True)
        row.scale_y = 1.5
        row.operator("pascal.import", text="Import from Pascal", icon='IMPORT')

        # Quick export path
        box.separator()
        box.prop(settings, "export_path")
        box.prop(settings, "file_name")

        # Scene info
        box = layout.box()
        box.label(text="Scene Info", icon='SCENE_DATA')

        # Count Pascal objects
        wall_count = 0
        item_count = 0
        level_count = 0

        for obj in context.scene.objects:
            if hasattr(obj, 'pascal'):
                if obj.pascal.pascal_type == 'WALL':
                    wall_count += 1
                elif obj.pascal.pascal_type == 'ITEM':
                    item_count += 1
                elif obj.pascal.pascal_type == 'LEVEL':
                    level_count += 1

        # Count collections that look like levels
        for collection in bpy.data.collections:
            name_lower = collection.name.lower()
            if 'level' in name_lower or 'floor' in name_lower:
                level_count += 1

        col = box.column(align=True)
        col.label(text=f"Levels: {level_count}")
        col.label(text=f"Walls: {wall_count}")
        col.label(text=f"Items: {item_count}")


class PASCAL_PT_object_panel(Panel):
    """Per-object Pascal properties panel."""
    bl_label = "Pascal Properties"
    bl_idname = "PASCAL_PT_object_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pascal"
    bl_parent_id = "PASCAL_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if not hasattr(obj, 'pascal'):
            layout.label(text="Pascal properties not available")
            return

        pascal = obj.pascal

        # Node type
        layout.prop(pascal, "pascal_type")

        # Show relevant properties based on type
        if pascal.pascal_type != 'NONE':
            box = layout.box()
            box.label(text="Pascal ID:")
            row = box.row()
            row.prop(pascal, "pascal_id", text="")

            if pascal.pascal_type == 'WALL':
                box = layout.box()
                box.label(text="Materials", icon='MATERIAL')
                box.prop(pascal, "material_front", text="Front")
                box.prop(pascal, "material_back", text="Back")

            elif pascal.pascal_type == 'ITEM':
                box = layout.box()
                box.label(text="Item Settings", icon='OBJECT_DATA')
                box.prop(pascal, "attach_to")
                box.prop(pascal, "model_url", text="Model URL")


class PASCAL_PT_settings_panel(Panel):
    """Settings panel."""
    bl_label = "Settings"
    bl_idname = "PASCAL_PT_settings_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pascal"
    bl_parent_id = "PASCAL_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.pascal_bridge

        # Default wall settings
        box = layout.box()
        box.label(text="Default Wall Settings", icon='MOD_BUILD')
        box.prop(settings, "default_wall_height")
        box.prop(settings, "default_wall_thickness")

        # Future: Live sync settings
        box = layout.box()
        box.label(text="Live Sync (Coming Soon)", icon='UV_SYNC_SELECT')
        box.enabled = False
        box.prop(settings, "pascal_endpoint")
        box.prop(settings, "auto_sync")
