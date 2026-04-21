#!/usr/bin/env python3
"""
validate_excalidraw.py — Pre-render structural validator for .excalidraw files.

Catches JSON errors that the visual render loop cannot detect:
  - Invalid element types (typos like "rectange")
  - Duplicate element IDs
  - Arrow points in wrong format (flat list instead of [[x,y], ...])
  - Missing startArrowhead / endArrowhead on arrows
  - startBinding / endBinding referencing non-existent IDs
  - Text containerId referencing a non-existent ID
  - boundElements entries referencing non-existent IDs
  - NaN or Infinity in x, y, width, height
  - Missing or non-string index on every element

Usage:
    uv run python references/validate_excalidraw.py <path-to-file.excalidraw>
"""

import json
import math
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Inline test cases (run automatically when invoked without file arguments)
# ---------------------------------------------------------------------------

def _make_base_element(id_, type_, **extra):
    base = {
        "id": id_,
        "type": type_,
        "x": 0, "y": 0, "width": 100, "height": 50,
        "strokeColor": "#000000",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": 1,
        "version": 1,
        "versionNonce": 1,
        "isDeleted": False,
        "groupIds": [],
        "boundElements": [],
        "link": None,
        "locked": False,
        "index": "a1",
    }
    base.update(extra)
    return base


def _make_arrow(id_, start_id, end_id, points=None, **extra):
    arrow = _make_base_element(id_, "arrow",
        points=points or [[0, 0], [100, 0]],
        startBinding={"elementId": start_id, "focus": 0, "gap": 2} if start_id else None,
        endBinding={"elementId": end_id, "focus": 0, "gap": 2} if end_id else None,
        startArrowhead=None,
        endArrowhead="arrow",
    )
    arrow.update(extra)
    return arrow


def _wrap(elements):
    return {"type": "excalidraw", "version": 2, "elements": elements, "appState": {}, "files": {}}


def _run_tests():
    passed = 0
    failed = 0

    def check(name, diagram, expected_errors):
        nonlocal passed, failed
        errors = validate_elements(diagram["elements"])
        missing = [e for e in expected_errors if not any(e.lower() in err.lower() for err in errors)]
        unexpected = [err for err in errors if not any(exp.lower() in err.lower() for exp in expected_errors)]
        if missing:
            print(f"  FAIL [{name}]: expected errors not raised: {missing}")
            failed += 1
        elif unexpected and not expected_errors:
            print(f"  FAIL [{name}]: unexpected errors: {unexpected}")
            failed += 1
        else:
            print(f"  PASS [{name}]")
            passed += 1

    print("Running inline test cases...\n")

    # ------------------------------------------------------------------
    # Test 1: Arrow whose startBinding.elementId points to a non-existent ID
    # ------------------------------------------------------------------
    rect = _make_base_element("real_rect", "rectangle")
    bad_arrow = _make_arrow("arr1", start_id="ghost_id", end_id="real_rect")
    check(
        "arrow startBinding references non-existent elementId",
        _wrap([rect, bad_arrow]),
        expected_errors=["ghost_id"],
    )

    # ------------------------------------------------------------------
    # Test 2: Element with a typo in `type` ("rectange" instead of "rectangle")
    # ------------------------------------------------------------------
    typo_elem = _make_base_element("elem_typo", "rectange")  # deliberate typo
    check(
        "element with typo in type ('rectange')",
        _wrap([typo_elem]),
        expected_errors=["rectange"],
    )

    # ------------------------------------------------------------------
    # Test 3: Duplicate element `id` values in the array
    # ------------------------------------------------------------------
    dup_a = _make_base_element("dup_id", "rectangle")
    dup_b = _make_base_element("dup_id", "ellipse")
    check(
        "duplicate element id values",
        _wrap([dup_a, dup_b]),
        expected_errors=["dup_id"],
    )

    # ------------------------------------------------------------------
    # Extra sanity: valid diagram should produce no errors
    # ------------------------------------------------------------------
    valid_rect = _make_base_element("r1", "rectangle")
    valid_arrow = _make_arrow("a1", start_id="r1", end_id=None)
    valid_arrow["endBinding"] = None
    errors = validate_elements(_wrap([valid_rect, valid_arrow])["elements"])
    if errors:
        print(f"  FAIL [valid diagram should pass]: {errors}")
        failed += 1
    else:
        print("  PASS [valid diagram produces no errors]")
        passed += 1

    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

VALID_TYPES = {
    "rectangle", "ellipse", "diamond", "arrow", "line",
    "text", "frame", "image", "freedraw",
}


def _is_bad_number(v):
    """Return True if v is float NaN or Infinity."""
    try:
        f = float(v)
        return math.isnan(f) or math.isinf(f)
    except (TypeError, ValueError):
        return False


def validate_elements(elements):
    """
    Validate a list of Excalidraw elements.

    Returns a list of human-readable error strings. An empty list means the
    diagram is structurally valid.
    """
    errors = []

    # Build the set of all element IDs first (used for reference checks)
    all_ids = [el.get("id") for el in elements if el.get("id")]
    id_set = set()
    duplicate_ids = set()
    for eid in all_ids:
        if eid in id_set:
            duplicate_ids.add(eid)
        id_set.add(eid)

    for eid in duplicate_ids:
        errors.append(f"Duplicate element id: '{eid}'")

    for i, el in enumerate(elements):
        label = f"Element[{i}] id={el.get('id', '<missing>')!r}"

        # --- type check ---
        etype = el.get("type")
        if etype not in VALID_TYPES:
            errors.append(f"{label}: invalid type '{etype}' (valid: {sorted(VALID_TYPES)})")

        # --- index present and is a string ---
        index = el.get("index")
        if index is None:
            errors.append(f"{label}: missing 'index' property")
        elif not isinstance(index, str):
            errors.append(f"{label}: 'index' must be a string, got {type(index).__name__}")

        # --- NaN / Infinity in geometry ---
        for prop in ("x", "y", "width", "height"):
            val = el.get(prop)
            if val is not None and _is_bad_number(val):
                errors.append(f"{label}: '{prop}' is NaN or Infinity ({val})")

        # --- arrow-specific checks ---
        if etype == "arrow":
            # points must be list of [x,y] pairs (not flat)
            points = el.get("points")
            if not isinstance(points, list) or len(points) < 2:
                errors.append(f"{label}: 'points' must be a list of at least 2 [x,y] pairs")
            else:
                for j, pt in enumerate(points):
                    if not (isinstance(pt, (list, tuple)) and len(pt) == 2):
                        errors.append(
                            f"{label}: points[{j}] is not an [x, y] pair — "
                            f"looks like a flat coordinate list"
                        )
                        break

            # startArrowhead / endArrowhead must be present (may be null)
            for prop in ("startArrowhead", "endArrowhead"):
                if prop not in el:
                    errors.append(f"{label}: missing '{prop}' (must be present, even if null)")

            # startBinding / endBinding elementId must reference an existing ID
            for binding_prop in ("startBinding", "endBinding"):
                binding = el.get(binding_prop)
                if binding is not None:
                    ref_id = binding.get("elementId")
                    if ref_id is not None and ref_id not in id_set:
                        errors.append(
                            f"{label}: {binding_prop}.elementId='{ref_id}' "
                            f"does not reference an existing element"
                        )

        # --- text-specific checks ---
        if etype == "text":
            container_id = el.get("containerId")
            if container_id is not None and container_id not in id_set:
                errors.append(
                    f"{label}: containerId='{container_id}' does not reference an existing element"
                )

        # --- boundElements reference check ---
        bound_elements = el.get("boundElements")
        if isinstance(bound_elements, list):
            for be in bound_elements:
                if isinstance(be, dict):
                    ref_id = be.get("id")
                    if ref_id is not None and ref_id not in id_set:
                        errors.append(
                            f"{label}: boundElements entry id='{ref_id}' "
                            f"does not reference an existing element"
                        )

    return errors


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-t", "--test", "test"):
        # Run built-in tests when invoked with no file or with --test
        ok = _run_tests()
        sys.exit(0 if ok else 1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(2)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(2)

    elements = data.get("elements", [])
    if not isinstance(elements, list):
        print("Error: 'elements' is not a list", file=sys.stderr)
        sys.exit(2)

    errors = validate_elements(elements)

    if not errors:
        print(f"OK — {len(elements)} elements, no structural errors found.")
        sys.exit(0)
    else:
        print(f"VALIDATION FAILED — {len(errors)} error(s) in {path.name}:\n")
        for err in errors:
            print(f"  • {err}")
        print(f"\nFix all errors above before rendering.")
        sys.exit(1)


if __name__ == "__main__":
    main()
