"""
Pascal scene graph schema definitions.

Mirrors the TypeScript schema from pascal-editor/lib/scenegraph/schema/
"""

import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union


def generate_id(node_type: str) -> str:
    """Generate a Pascal-style node ID."""
    return f"{node_type}_{uuid.uuid4().hex[:8]}"


# Material preset names available in Pascal
PASCAL_MATERIALS = [
    # Special states
    'preview-valid', 'preview-invalid', 'delete', 'ghost', 'glass',
    # Solid colors
    'white', 'black', 'gray', 'pink', 'green', 'blue', 'red', 'orange', 'yellow', 'purple',
    # Textured
    'brick', 'wood', 'concrete', 'tile', 'marble',
]

# Attachment types for items
ATTACH_TYPES = ['wall', 'wall-side', 'ceiling']  # None/undefined = floor


@dataclass
class BaseNode:
    """Base properties shared by all Pascal nodes."""
    object: str = "node"
    id: str = ""
    type: str = ""
    name: str = ""
    parentId: Optional[str] = None
    visible: bool = True
    opacity: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id(self.type)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        d = {
            'object': self.object,
            'id': self.id,
            'type': self.type,
        }
        if self.name:
            d['name'] = self.name
        if self.parentId is not None:
            d['parentId'] = self.parentId
        if not self.visible:
            d['visible'] = False
        if self.opacity != 100:
            d['opacity'] = self.opacity
        if self.metadata:
            d['metadata'] = self.metadata
        return d


@dataclass
class EnvironmentNode:
    """Environment settings (lighting, sky, etc.)."""

    def to_dict(self) -> Dict[str, Any]:
        return {}


@dataclass
class SiteNode(BaseNode):
    """Top-level site container."""
    type: str = "site"
    position: List[float] = field(default_factory=lambda: [0, 0])
    rotation: float = 0
    children: List['BuildingNode'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['children'] = [c.to_dict() for c in self.children]
        return d


@dataclass
class BuildingNode(BaseNode):
    """Building container."""
    type: str = "building"
    position: List[float] = field(default_factory=lambda: [0, 0])
    rotation: float = 0
    children: List['LevelNode'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['children'] = [c.to_dict() for c in self.children]
        return d


@dataclass
class LevelNode(BaseNode):
    """Level/floor container."""
    type: str = "level"
    height: float = 0
    wallHeight: float = 2.8
    floorThickness: float = 0.2
    children: List[Any] = field(default_factory=list)  # Wall, Slab, Column, Item, etc.

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['height'] = self.height
        d['wallHeight'] = self.wallHeight
        d['floorThickness'] = self.floorThickness
        d['children'] = [c.to_dict() for c in self.children]
        return d


@dataclass
class WallNode(BaseNode):
    """Wall segment defined by start/end points."""
    type: str = "wall"
    start: List[float] = field(default_factory=lambda: [0, 0])
    end: List[float] = field(default_factory=lambda: [1, 0])
    rotation: float = 0
    size: List[float] = field(default_factory=lambda: [0.15, 2.8])  # thickness, height
    height: Optional[float] = None  # Override level wallHeight
    baseline: float = 0  # Offset from floor
    materialFront: str = "white"
    materialBack: str = "white"
    children: List[Any] = field(default_factory=list)  # Door, Window, Item

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['start'] = self.start
        d['end'] = self.end
        d['rotation'] = self.rotation
        d['size'] = self.size
        if self.height is not None:
            d['height'] = self.height
        if self.baseline != 0:
            d['baseline'] = self.baseline
        if self.materialFront != "white":
            d['materialFront'] = self.materialFront
        if self.materialBack != "white":
            d['materialBack'] = self.materialBack
        d['children'] = [c.to_dict() for c in self.children]
        return d


@dataclass
class DoorNode(BaseNode):
    """Door opening in a wall."""
    type: str = "door"
    position: List[float] = field(default_factory=lambda: [0, 0])  # [x, y] in wall coords
    rotation: float = 0
    size: List[float] = field(default_factory=lambda: [0.9, 2.1])  # width, height

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['size'] = self.size
        return d


@dataclass
class WindowNode(BaseNode):
    """Window opening in a wall."""
    type: str = "window"
    position: List[float] = field(default_factory=lambda: [0, 1.0])  # [x, y] in wall coords
    rotation: float = 0
    size: List[float] = field(default_factory=lambda: [1.2, 1.2])  # width, height

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['size'] = self.size
        return d


@dataclass
class ItemNode(BaseNode):
    """Furniture/object item."""
    type: str = "item"
    position: Union[List[float], List[float]] = field(default_factory=lambda: [0, 0])  # [x, z] or [x, y, z]
    rotation: Union[float, List[float]] = 0  # Y rotation or [x, y, z] euler
    size: List[float] = field(default_factory=lambda: [1, 1])  # width, depth
    modelUrl: str = ""
    scale: Union[float, List[float]] = field(default_factory=lambda: [1, 1, 1])
    attachTo: Optional[str] = None  # 'wall', 'wall-side', 'ceiling', or None (floor)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['size'] = self.size
        if self.modelUrl:
            d['modelUrl'] = self.modelUrl
        if self.scale != [1, 1, 1] and self.scale != 1:
            d['scale'] = self.scale
        if self.attachTo:
            d['attachTo'] = self.attachTo
        return d


@dataclass
class ColumnNode(BaseNode):
    """Structural column."""
    type: str = "column"
    position: List[float] = field(default_factory=lambda: [0, 0])  # [x, z]
    diameter: float = 0.3

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        if self.diameter != 0.3:
            d['diameter'] = self.diameter
        return d


@dataclass
class SlabNode(BaseNode):
    """Floor slab."""
    type: str = "slab"
    position: List[float] = field(default_factory=lambda: [0, 0])
    rotation: float = 0
    size: List[float] = field(default_factory=lambda: [4, 4])  # width, depth

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['size'] = self.size
        return d


@dataclass
class CeilingNode(BaseNode):
    """Ceiling surface."""
    type: str = "ceiling"
    position: List[float] = field(default_factory=lambda: [0, 0])
    rotation: float = 0
    size: List[float] = field(default_factory=lambda: [4, 4])  # width, depth

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['size'] = self.size
        return d


@dataclass
class RoofNode(BaseNode):
    """Roof structure."""
    type: str = "roof"
    position: List[float] = field(default_factory=lambda: [0, 0])
    rotation: float = 0
    size: List[float] = field(default_factory=lambda: [4, 4])  # length, width

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['size'] = self.size
        return d


@dataclass
class GroupNode(BaseNode):
    """Grouping container."""
    type: str = "group"
    position: List[float] = field(default_factory=lambda: [0, 0])
    rotation: float = 0
    children: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['children'] = [c.to_dict() for c in self.children]
        return d


@dataclass
class ImageNode(BaseNode):
    """Reference image (2D)."""
    type: str = "image"
    position: List[float] = field(default_factory=lambda: [0, 0])
    rotation: List[float] = field(default_factory=lambda: [0, 0, 0])  # euler [x, y, z]
    scale: float = 1.0
    url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['scale'] = self.scale
        if self.url:
            d['url'] = self.url
        return d


@dataclass
class ScanNode(BaseNode):
    """3D scan model."""
    type: str = "scan"
    position: List[float] = field(default_factory=lambda: [0, 0, 0])  # [x, y, z]
    rotation: List[float] = field(default_factory=lambda: [0, 0, 0])  # euler [x, y, z]
    scale: float = 1.0
    url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d['position'] = self.position
        d['rotation'] = self.rotation
        d['scale'] = self.scale
        if self.url:
            d['url'] = self.url
        return d


@dataclass
class RootNode:
    """Root of the scene graph."""
    environment: EnvironmentNode = field(default_factory=EnvironmentNode)
    children: List[SiteNode] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'environment': self.environment.to_dict(),
            'children': [c.to_dict() for c in self.children],
        }


@dataclass
class Collection:
    """Collection for grouping nodes (e.g., rooms)."""
    id: str = ""
    object: str = "collection"
    type: str = "room"  # 'room' or 'other'
    levelId: Optional[str] = None
    name: str = ""
    nodeIds: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = f"collection_{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> Dict[str, Any]:
        d = {
            'id': self.id,
            'object': self.object,
            'type': self.type,
            'name': self.name,
            'nodeIds': self.nodeIds,
        }
        if self.levelId:
            d['levelId'] = self.levelId
        if self.metadata:
            d['metadata'] = self.metadata
        return d


@dataclass
class Scene:
    """Complete Pascal scene."""
    root: RootNode = field(default_factory=RootNode)
    collections: List[Collection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'root': self.root.to_dict(),
            'collections': [c.to_dict() for c in self.collections],
            'metadata': self.metadata,
        }


# Node type mapping for convenience
NODE_TYPES = {
    'site': SiteNode,
    'building': BuildingNode,
    'level': LevelNode,
    'wall': WallNode,
    'door': DoorNode,
    'window': WindowNode,
    'item': ItemNode,
    'column': ColumnNode,
    'slab': SlabNode,
    'ceiling': CeilingNode,
    'roof': RoofNode,
    'group': GroupNode,
    'image': ImageNode,
    'scan': ScanNode,
}


def create_node(node_type: str, **kwargs) -> BaseNode:
    """Factory function to create a node of the specified type."""
    if node_type not in NODE_TYPES:
        raise ValueError(f"Unknown node type: {node_type}")
    return NODE_TYPES[node_type](**kwargs)
