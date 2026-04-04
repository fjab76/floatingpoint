# Notes page design

**Date:** 2026-04-04

## Goal

Render `docs/floating-point-distribution-and-precision.md` as a proper `/notes` route in the Flask app, with client-side markdown rendering, syntax-highlighted code blocks, and LaTeX math via KaTeX.

## Routes

Two new routes added to `app.py`:

| Route | Method | Purpose |
|-------|--------|---------|
| `/notes` | GET | Renders `notes.html` shell template with `nav_active="notes"` |
| `/notes/content` | GET | Serves `docs/floating-point-distribution-and-precision.md` as `text/plain` via `send_from_directory` |

`base.html` nav gets a "Notes" link alongside the existing Home / Exact value / Segment / ULP links.

## Client-side rendering pipeline

Three CDN libraries loaded in `notes.html`:

- **marked.js** — parses markdown to HTML. A custom `code` renderer is wired in to call highlight.js at parse time.
- **highlight.js** — syntax highlights fenced code blocks (Python, Java, JSON, text).
- **KaTeX** + **KaTeX auto-render extension** — after HTML is injected into the DOM, `renderMathInElement()` scans for `$$...$$` (display math) and `$...$` (inline math) and renders them. Code elements are skipped automatically.

Page load sequence:

1. Fetch `/notes/content`
2. `marked.parse(text)` → HTML string
3. Inject into `<div id="notes-content">`
4. `renderMathInElement(container, { delimiters: [$$, $] })`

## Layout and typography

- Outer body and nav remain at 900px (unchanged from `base.html`).
- Inside `.container`, a `.notes-body` div is constrained to `max-width: 680px`, centered with `margin: 0 auto`.
- Typography scoped to `.notes-body`:
  - `font-size: 17px`, `line-height: 1.75`
  - `h2` / `h3` with a left border in the site's green (`#2e7d32`)
  - Code blocks: dark background (`#1e1e1e`), monospace, highlight.js theme
  - KaTeX display math: centered, with vertical margin
- The doc's outline at the top is an anchor-linked list; marked generates matching `id` attributes on headings by default, so in-page anchor links work without extra code.

## Files changed

| File | Change |
|------|--------|
| `app.py` | Add `/notes` and `/notes/content` routes; import `send_from_directory` |
| `templates/base.html` | Add "Notes" nav link |
| `templates/notes.html` | New file — shell template with CDN scripts and render logic |

No changes to `fp.py`, `fputil.py`, or the existing tool templates (`exact_decimal.html`, `segment.html`, `index.html`).
