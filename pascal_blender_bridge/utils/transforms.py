"""
Coordinate system transformations between Blender and Pascal.

Blender: Right-handed, Z-up
  - X: right
  - Y: forward (depth)
  - Z: up (height)

Pascal/Three.js: Right-handed, Y-up
  - X: right
  - Y: up (height)
  - Z: forward (towards viewer, opposite of Blender Y)

Conversion:
  Pascal X = Blender X
  Pascal Y = Blender Z (height)
  Pascal Z = -Blender Y (depth, negated)
"""

import math
from mathutils import Vector, Euler


def blender_to_pascal_position_2d(location):
    """
    Convert Blender location to Pascal 2D position [x, z].

    Used for: Sites, Buildings, Levels, Walls, floor Items, Groups

    Args:
        location: Blender Vector or tuple (x, y, z)

    Returns:
        list: [x, z] in Pascal coordinates
    """
    return [round(location[0], 4), round(-location[1], 4)]


def blender_to_pascal_position_3d(location):
    """
    Convert Blender location to Pascal 3D position [x, y, z].

    Used for: Scans, Images, attached Items

    Args:
        location: Blender Vector or tuple (x, y, z)

    Returns:
        list: [x, y, z] in Pascal coordinates
    """
    return [
        round(location[0], 4),
        round(location[2], 4),  # Blender Z -> Pascal Y
        round(-location[1], 4),  # Blender Y -> Pascal -Z
    ]


def blender_to_pascal_rotation_y(euler):
    """
    Convert Blender Euler rotation to Pascal Y rotation (radians).

    Pascal typically uses single Y-axis rotation for floor objects.
    Blender's Z rotation maps to Pascal's Y rotation.

    Args:
        euler: Blender Euler or tuple (x, y, z) in radians

    Returns:
        float: Rotation around Y axis in radians
    """
    # Blender Z rotation = Pascal Y rotation
    return round(euler[2], 4)


def blender_to_pascal_rotation_3d(euler):
    """
    Convert Blender Euler rotation to Pascal 3D rotation [x, y, z].

    Used for: Scans, Images

    Args:
        euler: Blender Euler or tuple (x, y, z) in radians

    Returns:
        list: [x, y, z] Euler angles in Pascal coordinates
    """
    # Blender XYZ -> Pascal with coordinate swap
    return [
        round(euler[0], 4),
        round(euler[2], 4),  # Blender Z -> Pascal Y
        round(-euler[1], 4),  # Blender Y -> Pascal -Z
    ]


def pascal_to_blender_position_2d(position):
    """
    Convert Pascal 2D position [x, z] to Blender location.

    Args:
        position: list [x, z] in Pascal coordinates

    Returns:
        Vector: Blender location (x, y, z)
    """
    return Vector((position[0], -position[1], 0))


def pascal_to_blender_position_3d(position):
    """
    Convert Pascal 3D position [x, y, z] to Blender location.

    Args:
        position: list [x, y, z] in Pascal coordinates

    Returns:
        Vector: Blender location (x, y, z)
    """
    return Vector((
        position[0],
        -position[2],  # Pascal Z -> Blender -Y
        position[1],   # Pascal Y -> Blender Z
    ))


def pascal_to_blender_rotation_y(rotation):
    """
    Convert Pascal Y rotation to Blender Euler.

    Args:
        rotation: float, rotation around Y in radians

    Returns:
        Euler: Blender Euler rotation
    """
    return Euler((0, 0, rotation), 'XYZ')


def pascal_to_blender_rotation_3d(rotation):
    """
    Convert Pascal 3D rotation [x, y, z] to Blender Euler.

    Args:
        rotation: list [x, y, z] Euler angles in radians

    Returns:
        Euler: Blender Euler rotation
    """
    return Euler((
        rotation[0],
        -rotation[2],  # Pascal Z -> Blender -Y
        rotation[1],   # Pascal Y -> Blender Z
    ), 'XYZ')


def blender_to_pascal_scale(scale):
    """
    Convert Blender scale to Pascal scale.

    Args:
        scale: Blender Vector or tuple (x, y, z)

    Returns:
        list: [x, y, z] scale in Pascal coordinates
    """
    return [
        round(scale[0], 4),
        round(scale[2], 4),  # Blender Z -> Pascal Y
        round(scale[1], 4),  # Blender Y -> Pascal Z
    ]


def pascal_to_blender_scale(scale):
    """
    Convert Pascal scale to Blender scale.

    Args:
        scale: list [x, y, z] or single number

    Returns:
        Vector: Blender scale (x, y, z)
    """
    if isinstance(scale, (int, float)):
        return Vector((scale, scale, scale))
    return Vector((
        scale[0],
        scale[2],  # Pascal Z -> Blender Y
        scale[1],  # Pascal Y -> Blender Z
    ))


def blender_dimensions_to_pascal_size(dimensions):
    """
    Convert Blender object dimensions to Pascal size [width, depth].

    Args:
        dimensions: Blender Vector or tuple (x, y, z)

    Returns:
        list: [width, depth] in Pascal coordinates
    """
    return [
        round(dimensions[0], 4),  # X = width
        round(dimensions[1], 4),  # Y = depth (Blender Y)
    ]


def wall_cube_to_pascal_wall(obj):
    """
    Convert a Blender cube representing a wall to Pascal wall format.

    Pascal walls are defined by start/end points, not center position.

    Args:
        obj: Blender mesh object (cube)

    Returns:
        dict: {start: [x, z], end: [x, z], size: [thickness, height]}
    """
    loc = obj.location
    dim = obj.dimensions
    rot_z = obj.rotation_euler[2]

    # Calculate half-length along the wall's local X axis
    half_length = dim[0] / 2

    # Calculate start and end points based on rotation
    cos_r = math.cos(rot_z)
    sin_r = math.sin(rot_z)

    # Start point (negative direction from center)
    start_x = loc[0] - half_length * cos_r
    start_y = loc[1] - half_length * sin_r

    # End point (positive direction from center)
    end_x = loc[0] + half_length * cos_r
    end_y = loc[1] + half_length * sin_r

    return {
        'start': [round(start_x, 4), round(-start_y, 4)],
        'end': [round(end_x, 4), round(-end_y, 4)],
        'size': [round(dim[1], 4), round(dim[2], 4)],  # thickness, height
        'rotation': round(rot_z, 4),
    }


def pascal_wall_to_blender_cube(wall_data):
    """
    Convert Pascal wall data to Blender cube parameters.

    Args:
        wall_data: dict with start, end, size keys

    Returns:
        dict: {location: Vector, dimensions: Vector, rotation: Euler}
    """
    start = wall_data['start']
    end = wall_data['end']
    size = wall_data.get('size', [0.15, 2.8])

    # Calculate center point
    center_x = (start[0] + end[0]) / 2
    center_z = (start[1] + end[1]) / 2  # Pascal Z

    # Calculate length and rotation
    dx = end[0] - start[0]
    dz = end[1] - start[1]
    length = math.sqrt(dx * dx + dz * dz)
    rotation = math.atan2(-dz, dx)  # Negate because Pascal Z = -Blender Y

    return {
        'location': Vector((center_x, -center_z, size[1] / 2)),
        'dimensions': Vector((length, size[0], size[1])),
        'rotation': Euler((0, 0, rotation), 'XYZ'),
    }
