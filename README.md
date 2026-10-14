# Excalidraw Diagram Skill

A coding agent skill that generates beautiful and practical Excalidraw diagrams from natural language descriptions. Not just boxes-and-arrows - diagrams that **argue visually**.

Compatible with any coding agent that supports skills — Claude Code, Codex, Cursor, OpenCode, and the [other agents supported by `npx skills`](https://github.com/vercel-labs/skills#supported-agents).

## What Makes This Different

- **Diagrams that argue, not display.** Every shape/group of shapes mirrors the concept it represents — fan-outs for one-to-many, timelines for sequences, convergence for aggregation. No uniform card grids.
- **Evidence artifacts.** As an example, technical diagrams include real code snippets and actual JSON payloads.
- **Built-in visual validation.** A Playwright-based render pipeline lets the agent see its own output, catch layout issues (overlapping text, misaligned arrows, unbalanced spacing), and fix them in a loop before delivering.
- **Brand-customizable.** All colors and brand styles live in a single file (`skills/excalidraw-diagram/references/color-palette.md`). Swap it out and every diagram follows your palette.

## Installation

Install with the [`skills` CLI](https://github.com/vercel-labs/skills):

```bash
# Current project (prompts for which agents to install to)
npx skills add zamonia500/excalidraw-diagram-skill

# Globally, for Claude Code only, without prompts
npx skills add zamonia500/excalidraw-diagram-skill -g -a claude-code -y
```

The skill is installed as `excalidraw-diagram` into each agent's skills directory (e.g. `.claude/skills/excalidraw-diagram/` for Claude Code, `.agents/skills/excalidraw-diagram/` for Codex/Cursor; `-g` installs under your home directory instead). Update later with `npx skills update excalidraw-diagram`.

**Manual install:** copy the `skills/excalidraw-diagram/` folder into your agent's skills directory:

```bash
git clone https://github.com/zamonia500/excalidraw-diagram-skill.git
cp -r excalidraw-diagram-skill/skills/excalidraw-diagram ~/.claude/skills/
```

## Setup

The skill includes a render pipeline that lets the agent visually validate its diagrams. It needs [uv](https://docs.astral.sh/uv/) and network access at render time (Excalidraw is loaded from a CDN). There are two ways to set it up:

**Option A: Ask your coding agent (easiest)**

Just tell your agent: *"Set up the Excalidraw diagram skill renderer by following the instructions in SKILL.md."* It will run the commands for you.

**Option B: Manual**

Replace `<skill-dir>` with the installed skill directory (e.g. `.claude/skills/excalidraw-diagram`):

```bash
uv sync --project <skill-dir>/references
uv run --project <skill-dir>/references playwright install chromium
```

If Playwright's bundled Chromium isn't available for your OS, the renderer falls back to a system Chrome/Chromium.

## Usage

Ask your coding agent to create a diagram:

> "Create an Excalidraw diagram showing how the AG-UI protocol streams events from an AI agent to a frontend UI"

The skill handles the rest — concept mapping, layout, JSON generation, rendering, and visual validation.

## Customize Colors

Edit `references/color-palette.md` inside the skill directory to match your brand. Everything else in the skill is universal design methodology. Note that `npx skills update` replaces the installed files, so keep a copy of your palette (or maintain it in your own fork).

## Repository Structure

Only `skills/excalidraw-diagram/` is installed; the files at the repo root are for maintaining this repository.

```
skills/excalidraw-diagram/
  SKILL.md                          # Design methodology + workflow
  references/
    color-palette.md                # Brand colors (edit this to customize)
    element-templates.md            # JSON templates for each element type
    json-schema.md                  # Excalidraw JSON format reference
    render_excalidraw.py            # Render .excalidraw to PNG
    render_template.html            # Browser template for rendering
    validate_excalidraw.py          # Pre-render structural validator
    measure-text.js                 # Optional text measurement (needs `canvas`)
    pyproject.toml                  # Python dependencies (playwright)
```
