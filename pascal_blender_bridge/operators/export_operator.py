"""
Export Blender scene to Pascal JSON format.
"""

import bpy
import json
import os
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper

from ..utils.pascal_schema import (
    Scene, RootNode, SiteNode, BuildingNode, LevelNode,
    WallNode, DoorNode, WindowNode, ItemNode, ColumnNode,
    SlabNode, CeilingNode, RoofNode, GroupNode, Collection,
    generate_id,
)
from ..utils.transforms import (
    blender_to_pascal_position_2d,
    blender_to_pascal_position_3d,
    blender_to_pascal_rotation_y,
    blender_to_pascal_scale,
    blender_dimensions_to_pascal_size,
    wall_cube_to_pascal_wall,
)


class PASCAL_OT_export(Operator, ExportHelper):
    """Export scene to Pascal JSON format"""
    bl_idname = "pascal.export"
    bl_label = "Export to Pascal"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        return self.export_scene(context, self.filepath)

    def export_scene(self, context, filepath):
        """Main export function."""
        scene_data = self.build_scene_graph(context)

        # Write JSON
        try:
            with open(filepath, 'w') as f:
                json.dump(scene_data.to_dict(), f, indent=2)
            self.report({'INFO'}, f"Exported to {filepath}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            return {'CANCELLED'}

    def build_scene_graph(self, context):
        """Build Pascal scene graph from Blender scene."""
        scene = Scene()

        # Create default site and building
        site = SiteNode(name="Site")
        building = BuildingNode(name="Building", parentId=site.id)
        site.children.append(building)

        # Process collections as levels
        level_index = 0
        for collection in bpy.data.collections:
            # Skip hidden collections
            if collection.hide_viewport:
                continue

            # Check if this collection represents a level
            if self.is_level_collection(collection):
                level = self.process_level_collection(collection, building.id, level_index)
                building.children.append(level)
                level_index += 1

        # If no level collections found, create a default level from scene objects
        if not building.children:
            level = self.process_scene_objects(context, building.id)
            building.children.append(level)

        scene.root.children.append(site)
        return scene

    def is_level_collection(self, collection):
        """Check if a collection represents a Pascal level."""
        # Check for explicit level naming
        name_lower = collection.name.lower()
        if 'level' in name_lower or 'floor' in name_lower or 'story' in name_lower:
            return True

        # Check if collection has any Pascal-typed objects
        for obj in collection.objects:
            if hasattr(obj, 'pascal') and obj.pascal.pascal_type != 'NONE':
                return True

        return False

    def process_level_collection(self, collection, parent_id, level_index):
        """Convert a Blender collection to a Pascal LevelNode."""
        level = LevelNode(
            name=collection.name,
            parentId=parent_id,
            height=level_index * 3.0,  # Default 3m per level
        )

        # Process objects in this collection
        for obj in collection.objects:
            node = self.convert_object(obj, level.id)
            if node:
                level.children.append(node)

        return level

    def process_scene_objects(self, context, parent_id):
        """Process all scene objects into a default level."""
        level = LevelNode(
            name="Level 1",
            parentId=parent_id,
            height=0,
        )

        # Process all mesh objects not in special collections
        for obj in context.scene.objects:
            # Skip objects in collections we've already processed
            if any(self.is_level_collection(c) for c in obj.users_collection):
                continue

            node = self.convert_object(obj, level.id)
            if node:
                level.children.append(node)

        return level

    def convert_object(self, obj, parent_id):
        """Convert a Blender object to a Pascal node."""
        # Get Pascal type from custom properties
        pascal_type = 'NONE'
        if hasattr(obj, 'pascal'):
            pascal_type = obj.pascal.pascal_type

        # Auto-detect type if not set
        if pascal_type == 'NONE':
            pascal_type = self.auto_detect_type(obj)

        if pascal_type == 'NONE':
            return None

        # Convert based on type
        converters = {
            'WALL': self.convert_wall,
            'DOOR': self.convert_door,
            'WINDOW': self.convert_window,
            'ITEM': self.convert_item,
            'COLUMN': self.convert_column,
            'SLAB': self.convert_slab,
            'CEILING': self.convert_ceiling,
            'ROOF': self.convert_roof,
            'GROUP': self.convert_group,
        }

        converter = converters.get(pascal_type)
        if converter:
            return converter(obj, parent_id)

        return None

    def auto_detect_type(self, obj):
        """Auto-detect Pascal type based on object characteristics."""
        if obj.type != 'MESH':
            if obj.type == 'EMPTY':
                return 'GROUP'
            return 'NONE'

        name_lower = obj.name.lower()

        # Check name patterns
        if 'wall' in name_lower:
            return 'WALL'
        if 'door' in name_lower:
            return 'DOOR'
        if 'window' in name_lower:
            return 'WINDOW'
        if 'column' in name_lower or 'pillar' in name_lower:
            return 'COLUMN'
        if 'floor' in name_lower or 'slab' in name_lower:
            return 'SLAB'
        if 'ceiling' in name_lower:
            return 'CEILING'
        if 'roof' in name_lower:
            return 'ROOF'

        # Default mesh objects to items
        return 'ITEM'

    def convert_wall(self, obj, parent_id):
        """Convert Blender object to WallNode."""
        wall_data = wall_cube_to_pascal_wall(obj)

        # Get or generate ID
        pascal_id = ""
        if hasattr(obj, 'pascal') and obj.pascal.pascal_id:
            pascal_id = obj.pascal.pascal_id

        node = WallNode(
            id=pascal_id or generate_id('wall'),
            name=obj.name,
            parentId=parent_id,
            start=wall_data['start'],
            end=wall_data['end'],
            rotation=wall_data['rotation'],
            size=wall_data['size'],
        )

        # Get materials from custom properties
        if hasattr(obj, 'pascal'):
            if obj.pascal.material_front:
                node.materialFront = obj.pascal.material_front
            if obj.pascal.material_back:
                node.materialBack = obj.pascal.material_back

        # Process children (doors, windows)
        for child in obj.children:
            child_node = self.convert_object(child, node.id)
            if child_node:
                node.children.append(child_node)

        return node

    def convert_door(self, obj, parent_id):
        """Convert Blender object to DoorNode."""
        pascal_id = ""
        if hasattr(obj, 'pascal') and obj.pascal.pascal_id:
            pascal_id = obj.pascal.pascal_id

        # For doors, position is relative to wall
        # This is simplified - real implementation would calculate wall-local coords
        pos = blender_to_pascal_position_2d(obj.location)

        return DoorNode(
            id=pascal_id or generate_id('door'),
            name=obj.name,
            parentId=parent_id,
            position=[pos[0], obj.location[2]],  # [x along wall, height]
            rotation=blender_to_pascal_rotation_y(obj.rotation_euler),
            size=[obj.dimensions[0], obj.dimensions[2]],
        )

    def convert_window(self, obj, parent_id):
        """Convert Blender object to WindowNode."""
        pascal_id = ""
        if hasattr(obj, 'pascal') and obj.pascal.pascal_id:
            pascal_id = obj.pascal.pascal_id

        pos = blender_to_pascal_position_2d(obj.location)

        return WindowNode(
            id=pascal_id or generate_id('window'),
            name=obj.name,
            parentId=parent_id,
            position=[pos[0], obj.location[2]],
            rotation=blender_to_pascal_rotation_y(obj.rotation_euler),
            size=[obj.dimensions[0], obj.dimensions[2]],
        )

    def convert_item(self, obj, parent_id):
        """Convert Blender object to ItemNode."""
        pascal_id = ""
        model_url = ""
        attach_to = None

        if hasattr(obj, 'pascal'):
            if obj.pascal.pascal_id:
                pascal_id = obj.pascal.pascal_id
            if obj.pascal.model_url:
                model_url = obj.pascal.model_url
            if obj.pascal.attach_to != 'FLOOR':
                attach_map = {
                    'WALL': 'wall',
                    'WALL_SIDE': 'wall-side',
                    'CEILING': 'ceiling',
                }
                attach_to = attach_map.get(obj.pascal.attach_to)

        return ItemNode(
            id=pascal_id or generate_id('item'),
            name=obj.name,
            parentId=parent_id,
            position=blender_to_pascal_position_2d(obj.location),
            rotation=blender_to_pascal_rotation_y(obj.rotation_euler),
            size=blender_dimensions_to_pascal_size(obj.dimensions),
            modelUrl=model_url,
            scale=blender_to_pascal_scale(obj.scale),
            attachTo=attach_to,
        )

    def convert_column(self, obj, parent_id):
        """Convert Blender object to ColumnNode."""
        pascal_id = ""
        if hasattr(obj, 'pascal') and obj.pascal.pascal_id:
            pascal_id = obj.pascal.pascal_id

        # Calculate diameter from dimensions
        diameter = max(obj.dimensions[0], obj.dimensions[1])

        return ColumnNode(
            id=pascal_id or generate_id('column'),
            name=obj.name,
            parentId=parent_id,
            position=blender_to_pascal_position_2d(obj.location),
            diameter=round(diameter, 4),
        )

    def convert_slab(self, obj, parent_id):
        """Convert Blender object to SlabNode."""
        pascal_id = ""
        if hasattr(obj, 'pascal') and obj.pascal.pascal_id:
            pascal_id = obj.pascal.pascal_id

        return SlabNode(
            id=pascal_id or generate_id('slab'),
            name=obj.name,
            parentId=parent_id,
            position=blender_to_pascal_position_2d(obj.location),
            rotation=blender_to_pascal_rotation_y(obj.rotation_euler),
            size=blender_dimensions_to_pascal_size(obj.dimensions),
        )

    def convert_ceiling(self, obj, parent_id):
        """Convert Blender object to CeilingNode."""
        pascal_id = ""
        if hasattr(obj, 'pascal') and obj.pascal.pascal_id:
            pascal_id = obj.pascal.pascal_id

        return CeilingNode(
            id=pascal_id or generate_id('ceiling'),
            name=obj.name,
            parentId=parent_id,
            position=blender_to_pascal_position_2d(obj.location),
            rotation=blender_to_pascal_rotation_y(obj.rotation_euler),
            size=blender_dimensions_to_pascal_size(obj.dimensions),
        )

    def convert_roof(self, obj, parent_id):
        """Convert Blender object to RoofNode."""
        pascal_id = ""
        if hasattr(obj, 'pascal') and obj.pascal.pascal_id:
            pascal_id = obj.pascal.pascal_id

        return RoofNode(
            id=pascal_id or generate_id('roof'),
            name=obj.name,
            parentId=parent_id,
            position=blender_to_pascal_position_2d(obj.location),
            rotation=blender_to_pascal_rotation_y(obj.rotation_euler),
            size=blender_dimensions_to_pascal_size(obj.dimensions),
        )

    def convert_group(self, obj, parent_id):
        """Convert Blender empty to GroupNode."""
        pascal_id = ""
        if hasattr(obj, 'pascal') and obj.pascal.pascal_id:
            pascal_id = obj.pascal.pascal_id

        node = GroupNode(
            id=pascal_id or generate_id('group'),
            name=obj.name,
            parentId=parent_id,
            position=blender_to_pascal_position_2d(obj.location),
            rotation=blender_to_pascal_rotation_y(obj.rotation_euler),
        )

        # Process children
        for child in obj.children:
            child_node = self.convert_object(child, node.id)
            if child_node:
                node.children.append(child_node)

        return node
