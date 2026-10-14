# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A coding-agent **skill** (not an application) that generates `.excalidraw` JSON diagrams from natural language. It is meant to be copied into a project's `.claude/skills/excalidraw-diagram/` directory. Most of the "code" is Markdown instructions consumed by an agent; the only executable part is a small Python render pipeline used for visual self-validation.

## Structure and how the pieces relate

- `SKILL.md` — the skill entry point (YAML frontmatter `name`/`description` controls when agents trigger it). Holds the design methodology, the design-process steps, the visual pattern library, and the mandatory render → view → fix loop. It delegates details to the files in `references/` rather than duplicating them.
- `references/color-palette.md` — the **single source of truth for all colors** (fills, strokes, text, evidence-artifact backgrounds). Brand customization should only touch this file; keep colors out of `SKILL.md` and `element-templates.md`.
- `references/element-templates.md` / `references/json-schema.md` — copy-paste JSON templates per element type and the Excalidraw format reference that `SKILL.md` points to.
- `references/render_excalidraw.py` + `references/render_template.html` — renderer. The Python script validates the JSON (`type == "excalidraw"`, non-empty `elements`), computes a viewport from the element bounding box, loads the HTML template in headless Chromium via Playwright (falling back to a system `chromium`/`chrome` channel if the bundled browser is missing), calls `window.renderDiagram(...)`, and screenshots the resulting SVG to PNG.
  - The template loads `@excalidraw/excalidraw` from a CDN at render time — **requires network access**. The version is pinned (`EXCALIDRAW_VERSION`, currently 0.18.0); never import it unpinned (an unpinned esm.sh import is what originally made the renderer hang). It tries esm.sh then jsDelivr with a per-source timeout and reports failures via `window.__moduleError`; browser console output is printed if loading times out.
  - `renderDiagram` renders twice when bound text overflows its container: it expands the container (and parent containers/frames, and bound arrow endpoints), then expands the viewBox to measured bounds after `document.fonts.ready`. **When it auto-corrects, it rewrites the input `.excalidraw` file.**
- `references/validate_excalidraw.py` — dependency-free structural validator (types, duplicate IDs, dangling binding/container/boundElements references, NaN geometry). It only checks that references exist, not that bindings are bidirectional — a text with `containerId` whose container lacks it in `boundElements` passes validation but the label won't render.
- `references/measure-text.js` — optional text measurement helper; needs `npm install canvas` in `references/`.

Paths in `SKILL.md`, the renderer's docstring, and its error messages assume the installed location `.claude/skills/excalidraw-diagram/references`. Keep them consistent if you change the layout.

## Commands

All run from `references/` (uses `uv`; Python ≥ 3.11, dependency is only `playwright`):

```bash
cd references
uv sync
uv run playwright install chromium

# Render a diagram to PNG (output defaults to same name with .png)
uv run python render_excalidraw.py <file.excalidraw> [--output out.png] [--scale 2] [--width 1920]

# Exercise the CDN fallback path (repeatable; esm.sh | jsDelivr)
uv run python render_excalidraw.py <file.excalidraw> --break-source esm.sh

# Pre-render validation, and the validator's built-in tests
uv run python validate_excalidraw.py <file.excalidraw>
uv run python validate_excalidraw.py --test

# Optional text measurement (after `npm install canvas`)
node measure-text.js "Label text" 16 Virgil
```

There is no linter or build step; the only automated tests are `validate_excalidraw.py --test`. To verify renderer changes, render sample `.excalidraw` files (copy them first, since auto-correction may rewrite them) and inspect the PNGs. JSON examples in the docs use palette placeholders like `<stroke from palette>`, which render as black — substitute real colors when test-rendering them. `.png`, `.venv/`, and `uv.lock` are gitignored.

## Fork / upstream

This is a fork of `coleam00/excalidraw-diagram-skill` (remote `upstream`). Upstream PRs were brought in via fork PRs that keep the original authors' commits (merge commits; cherry-picks where only part of a PR applied). Fetch upstream PR heads with `git fetch upstream '+refs/pull/*/head:refs/remotes/upstream/pr/*'`.
