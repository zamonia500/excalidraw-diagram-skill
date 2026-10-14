# Excalidraw JSON Schema

## Element Types

| Type | Use For |
|------|---------|
| `rectangle` | Processes, actions, components |
| `ellipse` | Entry/exit points, external systems |
| `diamond` | Decisions, conditionals |
| `arrow` | Connections between shapes |
| `text` | Labels inside shapes |
| `line` | Non-arrow connections |
| `frame` | Grouping containers |

## Common Properties

All elements share these:

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Unique identifier |
| `type` | string | Element type |
| `x`, `y` | number | Position in pixels |
| `width`, `height` | number | Size in pixels |
| `strokeColor` | string | Border color (hex) |
| `backgroundColor` | string | Fill color (hex or "transparent") |
| `fillStyle` | string | "solid", "hachure", "cross-hatch" |
| `strokeWidth` | number | 1, 2, or 4 |
| `strokeStyle` | string | "solid", "dashed", "dotted" |
| `roughness` | number | 0 (smooth), 1 (default), 2 (rough) |
| `opacity` | number | 0-100 |
| `seed` | number | Random seed for roughness |

## Text-Specific Properties

| Property | Description |
|----------|-------------|
| `text` | The display text |
| `originalText` | Same as text |
| `fontSize` | Size in pixels (16-20 recommended) |
| `fontFamily` | 3 for monospace (use this) |
| `textAlign` | "left", "center", "right" |
| `verticalAlign` | "top", "middle", "bottom" |
| `containerId` | ID of parent shape |

## Arrow-Specific Properties

| Property | Description |
|----------|-------------|
| `points` | Array of [x, y] coordinates |
| `startBinding` | Connection to start shape |
| `endBinding` | Connection to end shape |
| `startArrowhead` | null, "arrow", "bar", "dot", "triangle" |
| `endArrowhead` | null, "arrow", "bar", "dot", "triangle" |

## Binding Format

The binding object used in `startBinding` and `endBinding` on an arrow:

```json
{
  "elementId": "shapeId",
  "focus": 0.0,
  "gap": 5
}
```

| Property | Type | Description |
|----------|------|-------------|
| `elementId` | string | `id` of the shape this end of the arrow is attached to |
| `focus` | number | Attachment point on the shape edge: `0.0` = centre, `-1.0` = top/left edge, `1.0` = bottom/right edge |
| `gap` | number | Pixel gap between the arrowhead and the shape border (recommended: 5) |

**Bindings are bidirectional.** Setting `startBinding`/`endBinding` on the arrow is not enough on its own — each referenced shape must also list the arrow in its own `boundElements` array, otherwise Excalidraw treats the connection as unbound and the arrow drifts when shapes move:

```json
// On the source shape
"boundElements": [{"id": "my_arrow", "type": "arrow"}]

// On the arrow
"startBinding": {"elementId": "source_shape_id", "focus": 0.0, "gap": 5},
"endBinding":   {"elementId": "target_shape_id", "focus": 0.0, "gap": 5}

// On the target shape
"boundElements": [{"id": "my_arrow", "type": "arrow"}]
```

**Never use `null` bindings for intentionally-connected arrows.** Null bindings (`"startBinding": null`) produce arrows that appear connected visually at first but drift as soon as either shape is moved. See `references/element-templates.md` for a complete wired example.

## Rectangle Roundness

Add for rounded corners:
```json
"roundness": { "type": 3 }
```
