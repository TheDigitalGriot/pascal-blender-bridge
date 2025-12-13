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
