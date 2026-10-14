# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A coding-agent **skill** (not an application) that generates `.excalidraw` JSON diagrams from natural language. It is distributed with the [`skills` CLI](https://github.com/vercel-labs/skills) (`npx skills add zamonia500/excalidraw-diagram-skill`), which installs it as `excalidraw-diagram` into whatever agent skills directory the user picks. Most of the "code" is Markdown instructions consumed by an agent; the only executable part is a small Python render pipeline used for visual self-validation.

## Structure and how the pieces relate

The installable skill lives in `skills/excalidraw-diagram/` (`SKILL.md` + `references/`). `npx skills` copies the entire skill directory (everything except `.git`, `__pycache__`, `metadata.json`), so anything at the repo root — `README.md`, this file, `.gitignore` — is deliberately kept outside it and never reaches users. Don't add repo-maintenance files inside `skills/excalidraw-diagram/`. Paths below are relative to that directory.

- `SKILL.md` — the skill entry point (YAML frontmatter `name`/`description` controls when agents trigger it). Holds the design methodology, the design-process steps, the visual pattern library, and the mandatory render → view → fix loop. It delegates details to the files in `references/` rather than duplicating them.
- `references/color-palette.md` — the **single source of truth for all colors** (fills, strokes, text, evidence-artifact backgrounds). Brand customization should only touch this file; keep colors out of `SKILL.md` and `element-templates.md`.
- `references/element-templates.md` / `references/json-schema.md` — copy-paste JSON templates per element type and the Excalidraw format reference that `SKILL.md` points to.
- `references/render_excalidraw.py` + `references/render_template.html` — renderer. The Python script validates the JSON (`type == "excalidraw"`, non-empty `elements`), computes a viewport from the element bounding box, loads the HTML template in headless Chromium via Playwright (falling back to a system `chromium`/`chrome` channel if the bundled browser is missing), calls `window.renderDiagram(...)`, and screenshots the resulting SVG to PNG. It then embeds the scene into the PNG as a `tEXt` chunk (keyword `application/vnd.excalidraw+json`, zlib-deflated JSON as a byte string — the format of Excalidraw's `encodePngMetadata`), so the default output `<name>.excalidraw.png` can be reopened by Excalidraw's `loadFromBlob` (excalidraw.com, VS Code extensions). The embedded scene is the post-auto-correction one. Verify changes to this by loading the PNG with `loadFromBlob` in a browser, not just by viewing it.
  - The template loads `@excalidraw/excalidraw` from a CDN at render time — **requires network access**. The version is pinned (`EXCALIDRAW_VERSION`, currently 0.18.0); never import it unpinned (an unpinned esm.sh import is what originally made the renderer hang). It tries esm.sh then jsDelivr with a per-source timeout and reports failures via `window.__moduleError`; browser console output is printed if loading times out.
  - `renderDiagram` renders twice when bound text overflows its container: it expands the container (and parent containers/frames, and bound arrow endpoints), then expands the viewBox to measured bounds after `document.fonts.ready`. **When it auto-corrects, it rewrites the input `.excalidraw` file.**
- `references/validate_excalidraw.py` — dependency-free structural validator (types, duplicate IDs, dangling binding/container/boundElements references, NaN geometry). It only checks that references exist, not that bindings are bidirectional — a text with `containerId` whose container lacks it in `boundElements` passes validation but the label won't render.
- `references/measure-text.js` — optional text measurement helper; needs `npm install canvas --prefix references`.

**Never hard-code an install path.** Depending on agent and scope the skill ends up in `.claude/skills/`, `~/.claude/skills/`, `.agents/skills/`, etc. (often as a symlink to `.agents/skills/`). `SKILL.md` refers to its own location as `<skill-dir>` and uses commands that work from any cwd (`uv run --project <skill-dir>/references python <skill-dir>/references/render_excalidraw.py …`); scripts derive their location from `Path(__file__).resolve().parent` (`REFS_DIR` in the renderer).

## Commands

All run from `skills/excalidraw-diagram/references/` (uses `uv`; Python ≥ 3.11, dependency is only `playwright`):

```bash
cd skills/excalidraw-diagram/references
uv sync
uv run playwright install chromium

# Render a diagram to PNG (default output: <name>.excalidraw.png, scene embedded)
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

## Testing installation

To check what users actually get, install from a **clean clone** (a local-path install copies ignored files like `references/.venv` too) into a throwaway project, and use a temp `HOME` for `-g` so your real `~/.claude` is untouched:

```bash
git clone -q . /tmp/src && cd /tmp/proj
DO_NOT_TRACK=1 npx -y skills add /tmp/src --list
DO_NOT_TRACK=1 npx -y skills add /tmp/src -a codex -y --copy          # -> .agents/skills/excalidraw-diagram
HOME=/tmp/home DO_NOT_TRACK=1 npx -y skills add /tmp/src -g -a claude-code -y --copy
```

Then run SKILL.md's validate/render commands with `<skill-dir>` replaced by the installed path, from the project root.

## Fork / upstream

This is a fork of `coleam00/excalidraw-diagram-skill` (remote `upstream`). Upstream PRs were brought in via fork PRs that keep the original authors' commits (merge commits; cherry-picks where only part of a PR applied). Upstream still has the skill at the repo root, so upstream changes to `SKILL.md`/`references/` map to `skills/excalidraw-diagram/…` here (git rename detection usually handles cherry-picks/merges). Fetch upstream PR heads with `git fetch upstream '+refs/pull/*/head:refs/remotes/upstream/pr/*'`.
