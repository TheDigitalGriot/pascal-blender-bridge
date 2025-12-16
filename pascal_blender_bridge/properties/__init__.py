import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import PropertyGroup


class PascalBridgeSettings(PropertyGroup):
    """Addon-level settings stored on the scene."""

    export_path: StringProperty(
        name="Export Path",
        description="Directory to export Pascal JSON files",
        default="//",
        subtype='DIR_PATH',
    )

    file_name: StringProperty(
        name="File Name",
        description="Name for the exported file (without extension)",
        default="scene",
        maxlen=255,
    )

    pascal_endpoint: StringProperty(
        name="Pascal Endpoint",
        description="WebSocket URL for live sync (future feature)",
        default="ws://localhost:3000",
    )

    auto_sync: BoolProperty(
        name="Auto Sync",
        description="Automatically sync changes to Pascal (future feature)",
        default=False,
    )

    default_wall_height: FloatProperty(
        name="Default Wall Height",
        description="Default height for new walls (in meters)",
        default=2.8,
        min=0.1,
        max=100.0,
        unit='LENGTH',
    )

    default_wall_thickness: FloatProperty(
        name="Default Wall Thickness",
        description="Default thickness for new walls (in meters)",
        default=0.15,
        min=0.01,
        max=10.0,
        unit='LENGTH',
    )


class PascalObjectSettings(PropertyGroup):
    """Per-object Pascal properties."""

    pascal_type: EnumProperty(
        name="Pascal Type",
        description="Type of Pascal node this object represents",
        items=[
            ('NONE', "None", "Not a Pascal object"),
            ('SITE', "Site", "Site container"),
            ('BUILDING', "Building", "Building container"),
            ('LEVEL', "Level", "Level/floor"),
            ('WALL', "Wall", "Wall segment"),
            ('DOOR', "Door", "Door opening"),
            ('WINDOW', "Window", "Window opening"),
            ('ITEM', "Item", "Furniture/object"),
            ('COLUMN', "Column", "Structural column"),
            ('SLAB', "Slab", "Floor slab"),
            ('CEILING', "Ceiling", "Ceiling surface"),
            ('ROOF', "Roof", "Roof structure"),
            ('GROUP', "Group", "Grouping container"),
        ],
        default='NONE',
    )

    pascal_id: StringProperty(
        name="Pascal ID",
        description="Unique Pascal node ID (preserved on round-trip)",
        default="",
    )

    attach_to: EnumProperty(
        name="Attach To",
        description="What surface this item attaches to",
        items=[
            ('FLOOR', "Floor", "Free-standing on floor"),
            ('WALL', "Wall", "Attached to both wall sides"),
            ('WALL_SIDE', "Wall Side", "Attached to one wall side"),
            ('CEILING', "Ceiling", "Attached to ceiling"),
        ],
        default='FLOOR',
    )

    material_front: StringProperty(
        name="Material Front",
        description="Pascal material preset for front face",
        default="white",
    )

    material_back: StringProperty(
        name="Material Back",
        description="Pascal material preset for back face",
        default="white",
    )

    model_url: StringProperty(
        name="Model URL",
        description="Path to GLB model for items",
        default="",
    )


classes = (
    PascalBridgeSettings,
    PascalObjectSettings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.pascal_bridge = bpy.props.PointerProperty(type=PascalBridgeSettings)
    bpy.types.Object.pascal = bpy.props.PointerProperty(type=PascalObjectSettings)


def unregister():
    del bpy.types.Object.pascal
    del bpy.types.Scene.pascal_bridge

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
