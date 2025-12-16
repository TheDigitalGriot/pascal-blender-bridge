# Pascal Blender Bridge

A Blender addon enabling two-way synchronization between Blender and [Pascal](https://github.com/wawa-sensei/pascal) — use Blender as a powerful level editor for your React Three Fiber scenes.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Blender](https://img.shields.io/badge/Blender-4.0%2B-orange)

## Overview

Pascal Blender Bridge creates a live connection between Blender and Pascal's scene graph, allowing you to:

- **Design in Blender** → Export rooms, walls, and layouts to Pascal's JSON scene format
- **Edit in Pascal** → Sync changes back to Blender for further refinement
- **Iterate freely** → Work in whichever tool suits the task, with both staying in sync

Since Pascal's scene graph is pure JSON under the hood, and Blender excels at spatial/architectural modeling, this bridge lets you leverage the strengths of both tools.

## Why?

Pascal provides excellent in-browser tools for item placement, wall snapping, and scene management. But sometimes you want to:

- Rough out complex room layouts with Blender's modeling tools
- Use Blender's snapping, measurement, and precision features
- Import existing architectural models and convert them to Pascal scenes
- Make bulk edits across many objects quickly

This addon makes that workflow seamless.

## Features

- **Scene Export** — Convert Blender scenes to Pascal-compatible JSON
  - Meshes, walls, rooms, and levels
  - Proper hierarchy preservation (parent/child relationships)
  - Transform data (position, rotation, scale)

- **Scene Import** — Load Pascal JSON back into Blender
  - Reconstruct scene hierarchy
  - Maintain object metadata and Pascal-specific properties

- **Live Sync** (Planned) — Real-time two-way updates via WebSocket
  - Edit in Blender, see changes in Pascal instantly
  - Place items in Pascal, update Blender scene automatically

- **Catalog Integration** (Planned) — Access Pascal's item catalog from within Blender

## Installation

### From Release (Recommended)
1. Download the latest release from the [Releases](../../releases) page
2. In Blender, go to **Edit → Preferences → Add-ons**
3. Click **Install** and select the downloaded `.zip` file
4. Enable "Pascal Blender Bridge" in the addon list

### From Source
1. Clone this repository
2. Create a zip of the `pascal_blender_bridge/` folder:
   ```bash
   cd pascal-blender-bridge
   zip -r pascal_blender_bridge.zip pascal_blender_bridge/
   ```
3. In Blender, go to **Edit → Preferences → Add-ons**
4. Click **Install** and select `pascal_blender_bridge.zip`
5. Enable "Pascal Blender Bridge"

### Development Setup
For development, symlink the addon folder to Blender's addons directory:
```bash
# Linux/macOS
ln -s /path/to/pascal-blender-bridge/pascal_blender_bridge ~/.config/blender/4.2/scripts/addons/

# Windows (run as admin)
mklink /D "%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\pascal_blender_bridge" "C:\path\to\pascal_blender_bridge"
```

## Usage

### Exporting to Pascal

1. Set up your scene in Blender using the Pascal conventions:
   - Use collections to define levels
   - Name objects according to their Pascal node type (walls, rooms, items)
2. Open the Pascal Bridge panel in the 3D Viewport sidebar (N-panel)
3. Configure export settings
4. Click **Export to Pascal**

### Importing from Pascal

1. In the Pascal Bridge panel, click **Import from Pascal**
2. Select your Pascal scene JSON file
3. The scene hierarchy will be reconstructed in Blender

### Object Mapping

| Blender Object | Pascal Node Type | Detection |
|----------------|------------------|-----------|
| Collection | Level | Name contains "level" or "floor" |
| Cube mesh | Wall | Name contains "wall" or `pascal_type: WALL` |
| Cube mesh | Door | Name contains "door" or `pascal_type: DOOR` |
| Cube mesh | Window | Name contains "window" or `pascal_type: WINDOW` |
| Cylinder mesh | Column | Name contains "column" or `pascal_type: COLUMN` |
| Plane mesh | Slab/Ceiling/Roof | Based on name or pascal_type |
| Empty | Group | `pascal_type: GROUP` |
| Any mesh | Item | Default for unmatched meshes |

### Custom Properties

Select an object and open the **Pascal Properties** panel to set:
- **Pascal Type**: Override auto-detection
- **Pascal ID**: Preserved during round-trips
- **Attach To**: For items (floor, wall, wall-side, ceiling)
- **Materials**: Front/back material for walls
- **Model URL**: GLB model path for items

## Configuration

Settings are stored in the scene via the N-panel:
- **Export Path**: Directory for exported JSON files
- **File Name**: Name of the export file
- **Default Wall Height/Thickness**: For new walls

## Roadmap

- [x] Basic JSON export (scene → Pascal format)
- [x] JSON import (Pascal → Blender)
- [ ] WebSocket live sync
- [ ] Pascal item catalog browser in Blender
- [ ] Collision/blocker data export
- [ ] Wall snapping preview in Blender
- [ ] Multi-user sync support

## Acknowledgments

- Built for [Pascal](https://github.com/wawa-sensei/pascal) 

## Contributing

Contributions welcome! This project is in early development. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas where help is especially appreciated:
- WebSocket sync implementation
- Testing with complex scenes
- Documentation and examples

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**Note:** This addon is a community project and is not officially affiliated with Pascal.
