#!/usr/bin/env python3
"""Safely import a whiteboard document from a GitHub issue opened by the repository owner."""
import json
import math
import os
from pathlib import Path
import re
import secrets

body = os.environ.get("ISSUE_BODY", "")
if len(body) > 100000:
    raise SystemExit("Issue body is too large.")
marker = "<!-- LAS_WHITEBOARD_V1 -->"
if marker not in body:
    raise SystemExit("Not a whiteboard submission.")
after = body.split(marker, 1)[1]
match = re.search(r"[\x60]{3}json\s*", after, flags=re.I)
if not match:
    raise SystemExit("Missing JSON code fence.")
try:
    document, consumed = json.JSONDecoder().raw_decode(after[match.end():].lstrip())
except json.JSONDecodeError as exc:
    raise SystemExit(f"Invalid whiteboard JSON: {exc}") from exc

if not isinstance(document, dict) or document.get("version") != 1:
    raise SystemExit("Unsupported whiteboard format.")
if document.get("width") != 1200 or document.get("height") != 720:
    raise SystemExit("Unexpected canvas dimensions.")
shapes = document.get("shapes")
if not isinstance(shapes, list) or len(shapes) > 1500:
    raise SystemExit("Too many shapes.")
allowed = {"pen", "line", "arrow", "rect", "text"}
clean = []
total_points = 0
for raw in shapes:
    if not isinstance(raw, dict) or raw.get("type") not in allowed:
        raise SystemExit("Unrecognized shape.")
    pts = raw.get("points")
    if not isinstance(pts, list) or not (1 <= len(pts) <= 12000):
        raise SystemExit("Invalid point count.")
    points = []
    for p in pts:
        if not isinstance(p, list) or len(p) != 2:
            raise SystemExit("Invalid coordinate pair.")
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in p):
            raise SystemExit("Coordinate must be a finite number.")
        if not (0 <= p[0] <= 1200 and 0 <= p[1] <= 720):
            raise SystemExit("Coordinates outside the canvas.")
        points.append([round(v, 2) for v in p])
    total_points += len(points)
    if total_points > 50000:
        raise SystemExit("Too many points in board.")
    color = raw.get("color", "#185cba")
    if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise SystemExit("Invalid stroke color.")
    width = raw.get("width", 3)
    if type(width) not in (int, float) or not math.isfinite(width) or not (1 <= width <= 12):
        raise SystemExit("Invalid line width.")
    item = {
        "id": str(raw.get("id", ""))[:70],
        "author": raw.get("author") if raw.get("author") in ("user", "ai") else "user",
        "type": raw["type"],
        "color": color,
        "width": width,
        "points": points,
    }
    if raw["type"] == "text":
        item["text"] = str(raw.get("text", ""))[:120]
    clean.append(item)
question = document.get("question", "")
if not isinstance(question, str):
    raise SystemExit("Question must be text.")
out = {
    "version": 1,
    "width": 1200,
    "height": 720,
    "revision": secrets.token_hex(10),
    "updated_at": document.get("updated_at") if isinstance(document.get("updated_at"), str) else "",
    "question": question[:1000],
    "reply": "",
    "shapes": clean,
}
destination = Path("whiteboard/board.json")
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Accepted {len(clean)} shapes ({total_points} points).")
