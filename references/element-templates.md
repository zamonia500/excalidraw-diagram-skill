# Element Templates

Copy-paste JSON templates for each Excalidraw element type. The `strokeColor` and `backgroundColor` values are placeholders — always pull actual colors from `color-palette.md` based on the element's semantic purpose.

## Free-Floating Text (no container)
```json
{
  "type": "text",
  "id": "label1",
  "x": 100, "y": 100,
  "width": 200, "height": 25,
  "text": "Section Title",
  "originalText": "Section Title",
  "fontSize": 20,
  "fontFamily": 3,
  "textAlign": "left",
  "verticalAlign": "top",
  "strokeColor": "<title color from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 11111,
  "version": 1,
  "versionNonce": 22222,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": null,
  "lineHeight": 1.25
}
```

## Line (structural, not arrow)
```json
{
  "type": "line",
  "id": "line1",
  "x": 100, "y": 100,
  "width": 0, "height": 200,
  "strokeColor": "<structural line color from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 44444,
  "version": 1,
  "versionNonce": 55555,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [0, 200]]
}
```

## Small Marker Dot
```json
{
  "type": "ellipse",
  "id": "dot1",
  "x": 94, "y": 94,
  "width": 12, "height": 12,
  "strokeColor": "<marker dot color from palette>",
  "backgroundColor": "<marker dot color from palette>",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 66666,
  "version": 1,
  "versionNonce": 77777,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false
}
```

## Rectangle
```json
{
  "type": "rectangle",
  "id": "elem1",
  "x": 100, "y": 100, "width": 180, "height": 90,
  "strokeColor": "<stroke from palette based on semantic purpose>",
  "backgroundColor": "<fill from palette based on semantic purpose>",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 12345,
  "version": 1,
  "versionNonce": 67890,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{"id": "text1", "type": "text"}],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

## Text (centered in shape)
```json
{
  "type": "text",
  "id": "text1",
  "x": 130, "y": 132,
  "width": 120, "height": 25,
  "text": "Process",
  "originalText": "Process",
  "fontSize": 16,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "<text color — match parent shape's stroke or use 'on light/dark fills' from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 11111,
  "version": 1,
  "versionNonce": 22222,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": "elem1",
  "lineHeight": 1.25
}
```

## Arrow
```json
{
  "type": "arrow",
  "id": "arrow1",
  "x": 282, "y": 145, "width": 118, "height": 0,
  "strokeColor": "<arrow color — typically matches source element's stroke from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 33333,
  "version": 1,
  "versionNonce": 44444,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [118, 0]],
  "startBinding": {"elementId": "elem1", "focus": 0, "gap": 2},
  "endBinding": {"elementId": "elem2", "focus": 0, "gap": 2},
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

For curves: use 3+ points in `points` array.

## Bound Arrow (fully wired — source rect → arrow → target rect)

When arrows must stay connected to shapes as elements move, every binding reference must be
bidirectional: the arrow's `startBinding`/`endBinding` point to the shapes, AND each shape's
`boundElements` array lists the arrow back.

**Before (broken — arrow drifts):**
```python
# BROKEN pattern: null bindings cause visual drift when shapes move
arrow = {
    "type": "arrow",
    "id": "arrow1",
    "startBinding": None,   # <-- arrow is not attached to anything
    "endBinding": None,     # <-- arrow is not attached to anything
}
```

**After (correct — arrow stays connected):**
```python
# CORRECT pattern: bindings are set on the arrow AND reflected in boundElements on each shape
source_rect = {
    "type": "rectangle",
    "id": "source_rect",
    "boundElements": [{"id": "arrow1", "type": "arrow"}],  # arrow listed here
}
arrow = {
    "type": "arrow",
    "id": "arrow1",
    "startBinding": {"elementId": "source_rect", "focus": 0.0, "gap": 5},  # points to source
    "endBinding":   {"elementId": "target_rect", "focus": 0.0, "gap": 5},  # points to target
}
target_rect = {
    "type": "rectangle",
    "id": "target_rect",
    "boundElements": [{"id": "arrow1", "type": "arrow"}],  # arrow listed here too
}
```

**Full 3-element JSON example (source rect → arrow → target rect):**
```json
[
  {
    "type": "rectangle",
    "id": "source_rect",
    "x": 100, "y": 200, "width": 160, "height": 80,
    "strokeColor": "<stroke from palette>",
    "backgroundColor": "<fill from palette>",
    "fillStyle": "solid",
    "strokeWidth": 2,
    "strokeStyle": "solid",
    "roughness": 0,
    "opacity": 100,
    "angle": 0,
    "seed": 10001,
    "version": 1,
    "versionNonce": 10002,
    "isDeleted": false,
    "groupIds": [],
    "boundElements": [{"id": "conn_arrow", "type": "arrow"}],
    "link": null,
    "locked": false,
    "roundness": {"type": 3}
  },
  {
    "type": "arrow",
    "id": "conn_arrow",
    "x": 262, "y": 240, "width": 138, "height": 0,
    "strokeColor": "<arrow color from palette>",
    "backgroundColor": "transparent",
    "fillStyle": "solid",
    "strokeWidth": 2,
    "strokeStyle": "solid",
    "roughness": 0,
    "opacity": 100,
    "angle": 0,
    "seed": 20001,
    "version": 1,
    "versionNonce": 20002,
    "isDeleted": false,
    "groupIds": [],
    "boundElements": null,
    "link": null,
    "locked": false,
    "points": [[0, 0], [138, 0]],
    "startBinding": {"elementId": "source_rect", "focus": 0.0, "gap": 5},
    "endBinding":   {"elementId": "target_rect", "focus": 0.0, "gap": 5},
    "startArrowhead": null,
    "endArrowhead": "arrow"
  },
  {
    "type": "rectangle",
    "id": "target_rect",
    "x": 400, "y": 200, "width": 160, "height": 80,
    "strokeColor": "<stroke from palette>",
    "backgroundColor": "<fill from palette>",
    "fillStyle": "solid",
    "strokeWidth": 2,
    "strokeStyle": "solid",
    "roughness": 0,
    "opacity": 100,
    "angle": 0,
    "seed": 30001,
    "version": 1,
    "versionNonce": 30002,
    "isDeleted": false,
    "groupIds": [],
    "boundElements": [{"id": "conn_arrow", "type": "arrow"}],
    "link": null,
    "locked": false,
    "roundness": {"type": 3}
  }
]
```

**Key rules for bound arrows:**
- `startBinding.elementId` must equal the `id` of the shape at the arrow's start
- `endBinding.elementId` must equal the `id` of the shape at the arrow's end
- Both shapes must include `{"id": "<arrow_id>", "type": "arrow"}` in their `boundElements` array
- `focus: 0.0` centres the arrow on the shape's edge; range is `-1.0` to `1.0`
- `gap: 5` leaves a small visual gap between the arrowhead and the shape border
