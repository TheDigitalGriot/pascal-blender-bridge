"""
Import Pascal JSON into Blender.
"""

import bpy
import json
import math
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector, Euler

from ..utils.transforms import (
    pascal_to_blender_position_2d,
    pascal_to_blender_position_3d,
    pascal_to_blender_rotation_y,
    pascal_to_blender_rotation_3d,
    pascal_to_blender_scale,
    pascal_wall_to_blender_cube,
)


class PASCAL_OT_import(Operator, ImportHelper):
    """Import Pascal JSON scene"""
    bl_idname = "pascal.import"
    bl_label = "Import from Pascal"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        return self.import_scene(context, self.filepath)

    def import_scene(self, context, filepath):
        """Main import function."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to read file: {str(e)}")
            return {'CANCELLED'}

        try:
            self.process_scene(context, data)
            self.report({'INFO'}, f"Imported from {filepath}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {str(e)}")
            return {'CANCELLED'}

    def process_scene(self, context, data):
        """Process Pascal scene data."""
        root = data.get('root', {})
        children = root.get('children', [])

        # Process sites
        for site_data in children:
            self.process_site(context, site_data)

    def process_site(self, context, site_data):
        """Process a site node."""
        # Create site empty
        site_obj = self.create_empty(site_data, 'PLAIN_AXES')

        # Process buildings
        for building_data in site_data.get('children', []):
            self.process_building(context, building_data, site_obj)

    def process_building(self, context, building_data, parent):
        """Process a building node."""
        # Create building empty
        building_obj = self.create_empty(building_data, 'CUBE')
        building_obj.parent = parent

        # Process levels
        for level_data in building_data.get('children', []):
            self.process_level(context, level_data, building_obj)

    def process_level(self, context, level_data, parent):
        """Process a level node and create a collection."""
        level_name = level_data.get('name', f"Level_{level_data.get('id', 'unknown')}")

        # Create collection for the level
        collection = bpy.data.collections.new(level_name)
        context.scene.collection.children.link(collection)

        # Store level metadata on a level empty
        level_empty = bpy.data.objects.new(level_name + "_root", None)
        level_empty.empty_display_type = 'PLAIN_AXES'
        level_empty.parent = parent
        collection.objects.link(level_empty)

        # Store Pascal properties
        self.store_pascal_properties(level_empty, level_data, 'LEVEL')

        # Calculate level height offset
        level_height = level_data.get('height', 0)

        # Process children
        for child_data in level_data.get('children', []):
            self.process_node(context, child_data, collection, level_empty, level_height)

    def process_node(self, context, node_data, collection, parent, level_height=0):
        """Process a generic node and create appropriate Blender object."""
        node_type = node_data.get('type', 'unknown')

        processors = {
            'wall': self.create_wall,
            'door': self.create_door,
            'window': self.create_window,
            'item': self.create_item,
            'column': self.create_column,
            'slab': self.create_slab,
            'ceiling': self.create_ceiling,
            'roof': self.create_roof,
            'group': self.create_group,
        }

        processor = processors.get(node_type)
        if processor:
            obj = processor(context, node_data, level_height)
            if obj:
                # Link to collection
                collection.objects.link(obj)

                # Set parent if provided
                if parent:
                    obj.parent = parent

                # Store Pascal properties
                pascal_type = node_type.upper()
                self.store_pascal_properties(obj, node_data, pascal_type)

                # Process children if any
                for child_data in node_data.get('children', []):
                    self.process_node(context, child_data, collection, obj, level_height)

    def create_empty(self, node_data, display_type='PLAIN_AXES'):
        """Create an empty object from node data."""
        name = node_data.get('name', node_data.get('type', 'Empty'))
        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = display_type

        # Set position
        position = node_data.get('position', [0, 0])
        if len(position) == 2:
            obj.location = pascal_to_blender_position_2d(position)
        else:
            obj.location = pascal_to_blender_position_3d(position)

        # Set rotation
        rotation = node_data.get('rotation', 0)
        if isinstance(rotation, (int, float)):
            obj.rotation_euler = pascal_to_blender_rotation_y(rotation)
        else:
            obj.rotation_euler = pascal_to_blender_rotation_3d(rotation)

        # Store Pascal properties
        pascal_type = node_data.get('type', 'unknown').upper()
        if pascal_type in ['SITE', 'BUILDING', 'GROUP']:
            self.store_pascal_properties(obj, node_data, pascal_type)

        # Link to scene
        bpy.context.scene.collection.objects.link(obj)

        return obj

    def create_wall(self, context, node_data, level_height):
        """Create a wall mesh from Pascal wall data."""
        cube_params = pascal_wall_to_blender_cube(node_data)

        # Create mesh
        bpy.ops.mesh.primitive_cube_add()
        obj = context.active_object
        obj.name = node_data.get('name', f"Wall_{node_data.get('id', 'unknown')}")

        # Apply transforms
        obj.location = cube_params['location']
        obj.location.z += level_height
        obj.dimensions = cube_params['dimensions']
        obj.rotation_euler = cube_params['rotation']

        # Unlink from default collection (will be linked to level collection)
        context.scene.collection.objects.unlink(obj)

        return obj

    def create_door(self, context, node_data, level_height):
        """Create a door mesh."""
        position = node_data.get('position', [0, 0])
        size = node_data.get('size', [0.9, 2.1])

        bpy.ops.mesh.primitive_cube_add()
        obj = context.active_object
        obj.name = node_data.get('name', f"Door_{node_data.get('id', 'unknown')}")

        # Position (x along wall, y height from floor)
        obj.location = Vector((position[0], 0, position[1] + size[1] / 2 + level_height))
        obj.dimensions = Vector((size[0], 0.1, size[1]))

        rotation = node_data.get('rotation', 0)
        obj.rotation_euler = pascal_to_blender_rotation_y(rotation)

        context.scene.collection.objects.unlink(obj)
        return obj

    def create_window(self, context, node_data, level_height):
        """Create a window mesh."""
        position = node_data.get('position', [0, 1.0])
        size = node_data.get('size', [1.2, 1.2])

        bpy.ops.mesh.primitive_cube_add()
        obj = context.active_object
        obj.name = node_data.get('name', f"Window_{node_data.get('id', 'unknown')}")

        obj.location = Vector((position[0], 0, position[1] + size[1] / 2 + level_height))
        obj.dimensions = Vector((size[0], 0.1, size[1]))

        rotation = node_data.get('rotation', 0)
        obj.rotation_euler = pascal_to_blender_rotation_y(rotation)

        context.scene.collection.objects.unlink(obj)
        return obj

    def create_item(self, context, node_data, level_height):
        """Create an item (empty or mesh placeholder)."""
        position = node_data.get('position', [0, 0])
        size = node_data.get('size', [1, 1])
        scale = node_data.get('scale', [1, 1, 1])

        # Create a cube as placeholder
        bpy.ops.mesh.primitive_cube_add()
        obj = context.active_object
        obj.name = node_data.get('name', f"Item_{node_data.get('id', 'unknown')}")

        # Set position
        if len(position) == 2:
            obj.location = pascal_to_blender_position_2d(position)
            obj.location.z = level_height
        else:
            obj.location = pascal_to_blender_position_3d(position)
            obj.location.z += level_height

        # Set rotation
        rotation = node_data.get('rotation', 0)
        if isinstance(rotation, (int, float)):
            obj.rotation_euler = pascal_to_blender_rotation_y(rotation)
        else:
            obj.rotation_euler = pascal_to_blender_rotation_3d(rotation)

        # Set scale
        obj.scale = pascal_to_blender_scale(scale)

        # Set dimensions based on size
        obj.dimensions = Vector((size[0], size[1], 1.0))

        context.scene.collection.objects.unlink(obj)
        return obj

    def create_column(self, context, node_data, level_height):
        """Create a column mesh."""
        position = node_data.get('position', [0, 0])
        diameter = node_data.get('diameter', 0.3)

        bpy.ops.mesh.primitive_cylinder_add(radius=diameter / 2, depth=2.8)
        obj = context.active_object
        obj.name = node_data.get('name', f"Column_{node_data.get('id', 'unknown')}")

        obj.location = pascal_to_blender_position_2d(position)
        obj.location.z = 1.4 + level_height  # Center at half height

        context.scene.collection.objects.unlink(obj)
        return obj

    def create_slab(self, context, node_data, level_height):
        """Create a floor slab mesh."""
        position = node_data.get('position', [0, 0])
        size = node_data.get('size', [4, 4])

        bpy.ops.mesh.primitive_plane_add()
        obj = context.active_object
        obj.name = node_data.get('name', f"Slab_{node_data.get('id', 'unknown')}")

        obj.location = pascal_to_blender_position_2d(position)
        obj.location.z = level_height
        obj.dimensions = Vector((size[0], size[1], 0))

        rotation = node_data.get('rotation', 0)
        obj.rotation_euler = pascal_to_blender_rotation_y(rotation)

        context.scene.collection.objects.unlink(obj)
        return obj

    def create_ceiling(self, context, node_data, level_height):
        """Create a ceiling mesh."""
        position = node_data.get('position', [0, 0])
        size = node_data.get('size', [4, 4])

        bpy.ops.mesh.primitive_plane_add()
        obj = context.active_object
        obj.name = node_data.get('name', f"Ceiling_{node_data.get('id', 'unknown')}")

        obj.location = pascal_to_blender_position_2d(position)
        obj.location.z = level_height + 2.8  # Wall height
        obj.dimensions = Vector((size[0], size[1], 0))

        rotation = node_data.get('rotation', 0)
        obj.rotation_euler = pascal_to_blender_rotation_y(rotation)

        context.scene.collection.objects.unlink(obj)
        return obj

    def create_roof(self, context, node_data, level_height):
        """Create a roof mesh."""
        position = node_data.get('position', [0, 0])
        size = node_data.get('size', [4, 4])

        bpy.ops.mesh.primitive_plane_add()
        obj = context.active_object
        obj.name = node_data.get('name', f"Roof_{node_data.get('id', 'unknown')}")

        obj.location = pascal_to_blender_position_2d(position)
        obj.location.z = level_height + 3.0
        obj.dimensions = Vector((size[0], size[1], 0))

        rotation = node_data.get('rotation', 0)
        obj.rotation_euler = pascal_to_blender_rotation_y(rotation)

        context.scene.collection.objects.unlink(obj)
        return obj

    def create_group(self, context, node_data, level_height):
        """Create a group (empty)."""
        position = node_data.get('position', [0, 0])

        obj = bpy.data.objects.new(
            node_data.get('name', f"Group_{node_data.get('id', 'unknown')}"),
            None
        )
        obj.empty_display_type = 'PLAIN_AXES'

        obj.location = pascal_to_blender_position_2d(position)
        obj.location.z = level_height

        rotation = node_data.get('rotation', 0)
        obj.rotation_euler = pascal_to_blender_rotation_y(rotation)

        return obj

    def store_pascal_properties(self, obj, node_data, pascal_type):
        """Store Pascal metadata as custom properties on the object."""
        if not hasattr(obj, 'pascal'):
            return

        # Set type
        if pascal_type in ['SITE', 'BUILDING', 'LEVEL', 'WALL', 'DOOR', 'WINDOW',
                          'ITEM', 'COLUMN', 'SLAB', 'CEILING', 'ROOF', 'GROUP']:
            obj.pascal.pascal_type = pascal_type

        # Store ID
        if 'id' in node_data:
            obj.pascal.pascal_id = node_data['id']

        # Store materials for walls
        if pascal_type == 'WALL':
            if 'materialFront' in node_data:
                obj.pascal.material_front = node_data['materialFront']
            if 'materialBack' in node_data:
                obj.pascal.material_back = node_data['materialBack']

        # Store item-specific properties
        if pascal_type == 'ITEM':
            if 'modelUrl' in node_data:
                obj.pascal.model_url = node_data['modelUrl']
            if 'attachTo' in node_data:
                attach_map = {
                    'wall': 'WALL',
                    'wall-side': 'WALL_SIDE',
                    'ceiling': 'CEILING',
                }
                obj.pascal.attach_to = attach_map.get(node_data['attachTo'], 'FLOOR')
