# LAS Shared Whiteboard (GitHub prototype)

A small, coordinate-based whiteboard for asynchronous collaboration using GitHub Pages and ChatGPT with its GitHub connection.

**Website:** https://lastechnion.com/whiteboard/
**Shared JSON:** [board.json](board.json)

## How to use

1. Open the website. Draw using a mouse or stylus or choose **Load beam example**.
2. Write a question in **Discuss this drawing**; optionally use browser dictation if available.
3. Click **Publish drawing**. GitHub opens a prefilled issue. Sign in as the repository owner **LAStechnion**, review its content, and click **Submit new issue**.
4. GitHub Actions validates the owner-submitted issue and commits its shapes to whiteboard/board.json.
5. In ChatGPT, ask: **"Read the latest whiteboard in LAStechnion/lastechnion.github.io/whiteboard/board.json and draw the answer."** ChatGPT can read the shared JSON through GitHub, append new vector shapes with author set to ai, and write a textual reply.
6. Return to the website and click **Load GitHub board** to see the updated drawing. Optionally click **Speak response**.

**This is asynchronous collaboration**, not continuous AI voice or synchronized real-time drawing. GitHub issues and commits are not a live streaming protocol. No GitHub token or OpenAI API key is stored in the page.

## Features

- Freehand pen, line, arrow, rectangle, text and object eraser
- Color and stroke width, undo and redo
- Local draft autosave and JSON import/export
- Built-in cantilever beam example
- GitHub issue submission and guarded GitHub Actions importer
- Load the latest published drawing, including AI-created annotations
- Optional browser-native speech dictation and read-aloud

## Data format

~~~json
{
  "version": 1,
  "width": 1200,
  "height": 720,
  "revision": "initial",
  "updated_at": "2026-11-19T00:00:00Z",
  "question": "Draw the approximate beam deflection.",
  "reply": "The deflection grows toward the free end.",
  "shapes": [
    {
      "id": "beam-1", "author": "user", "type": "line",
      "color": "#185cba", "width": 3,
      "points": [[160, 352], [820, 352]]
    },
    {
      "id": "ai-curve-1", "author": "ai", "type": "pen",
      "color": "#da703e", "width": 3,
      "points": [[160, 352], [320, 356], [490, 379], [660, 419], [820, 462]]
    }
  ]
}
~~~

Supported shape types: pen, line, arrow, rect and text (the latter has a text field). Coordinates are in the logical 1200 x 720 canvas.

**AI drawing convention:** Draw in warm orange (#da703e), preserve the user's existing objects, and explain the change in reply. Do not overwrite newer user contributions.

## GitHub transport and security

- **Public:** The site, drawing, questions and AI answers are publicly readable. Do not include confidential or unpublished material.
- GitHub Pages hosts static files. Browser code never contains write credentials.
- Only a GitHub issue opened by the repository owner, with the expected title and valid JSON, can trigger the whiteboard importer. The importer does not execute any submitted code.
- Importer workflow: [whiteboard-issues.yml](../.github/workflows/whiteboard-issues.yml). Validator: [import_whiteboard_issue.py](../.github/scripts/import_whiteboard_issue.py).
- GitHub Actions might need to be enabled and permitted to write repository contents under Settings > Actions > General.
- Commits made by GitHub Actions using GITHUB_TOKEN may not rebuild Pages. The **Load GitHub board** button therefore fetches the raw source JSON directly from GitHub.
- The Publish button has a URL-length cap and is intended for small drawings. For a larger board, export JSON and attach it to a ChatGPT conversation or commit it to the repository manually.
- Locally modified drawings are preserved unless you choose to replace them from GitHub.

## Next iteration

For genuinely live voice and near-real-time collaborative strokes, add a dedicated realtime server; keep this GitHub project for hosting and versioned snapshots.
