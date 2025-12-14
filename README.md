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

1. Download the latest release from the [Releases](../../releases) page
2. In Blender, go to **Edit → Preferences → Add-ons**
3. Click **Install** and select the downloaded `.zip` file
4. Enable "Pascal Blender Bridge" in the addon list

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

| Blender | Pascal Node Type |
|---------|------------------|
| Collection | Level |
| Cube (tagged) | Wall |
| Empty | Room container |
| Mesh objects | Item nodes |

## Configuration

The addon stores settings in a `.pascal-bridge.json` file in your project:

```json
{
  "pascalEndpoint": "http://localhost:3000",
  "autoSync": false,
  "exportPath": "./scenes",
  "catalogPath": "./catalog"
}
```

## Roadmap

- [x] Basic JSON export (scene → Pascal format)
- [x] JSON import (Pascal → Blender)
- [ ] WebSocket live sync
- [ ] Pascal item catalog browser in Blender
- [ ] Collision/blocker data export
- [ ] Wall snapping preview in Blender
- [ ] Multi-user sync support

## Acknowledgments

- Inspired by [LvlExporter](https://superhivemarket.com/products/lvl-exporter) — a Blender addon for exporting scene data to JSON/XML for code-focused 3D frameworks
- Built for [Pascal](https://github.com/wawa-sensei/pascal) by [@wawasensei](https://twitter.com/waaborern)

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
