# Notes Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/notes` route that renders `docs/floating-point-distribution-and-precision.md` as a readable page with syntax-highlighted code and KaTeX math.

**Architecture:** Flask serves a shell template at `/notes` and the raw markdown at `/notes/content`. The browser fetches the markdown, parses it with marked.js, highlights code with highlight.js, and renders LaTeX with KaTeX auto-render — all client-side, no Python dependencies added.

**Tech Stack:** Flask (existing), marked.js 12 (CDN), highlight.js 11.9 (CDN), KaTeX 0.16.10 + auto-render (CDN)

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `test_app.py` | Modify | Add route tests for `/notes` and `/notes/content` |
| `app.py` | Modify | Add `send_from_directory` import; add `/notes` and `/notes/content` routes |
| `templates/base.html` | Modify | Add "Notes" nav link |
| `templates/notes.html` | Create | Shell template: CDN links, CSS, JS fetch+render pipeline |

---

### Task 1: Add route tests and implement Flask routes

**Files:**
- Modify: `test_app.py`
- Modify: `app.py`

- [ ] **Step 1: Write failing tests**

Add these two test methods to the `FloatingpointAppTestCase` class in `test_app.py`, after the existing `test_segment_empty` method:

```python
def test_notes_page(self) -> None:
    response = self.client.get("/notes")
    self.assertEqual(response.status_code, 200)
    self.assertIn(b"notes-content", response.data)

def test_notes_content(self) -> None:
    response = self.client.get("/notes/content")
    self.assertEqual(response.status_code, 200)
    self.assertIn("text/plain", response.content_type)
    self.assertIn(b"Floating-point numbers", response.data)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest test_app.py::FloatingpointAppTestCase::test_notes_page test_app.py::FloatingpointAppTestCase::test_notes_content -v
```

Expected: both tests FAIL with 404 (routes don't exist yet).

- [ ] **Step 3: Add routes to app.py**

Change the import line at the top of `app.py` from:

```python
from flask import Flask, jsonify, render_template, request
```

to:

```python
from flask import Flask, jsonify, render_template, request, send_from_directory
```

Then add these two routes after the `segment_process` function, before `if __name__ == "__main__":`:

```python
@app.route("/notes")
def notes():
    """Serve the floating-point notes page."""
    return render_template("notes.html", nav_active="notes")


@app.route("/notes/content")
def notes_content():
    """Serve the raw markdown notes file for client-side rendering."""
    return send_from_directory(
        "docs",
        "floating-point-distribution-and-precision.md",
        mimetype="text/plain",
    )
```

- [ ] **Step 4: Create a minimal notes.html to unblock the tests**

Create `templates/notes.html` with just enough to satisfy `test_notes_page` (the full template comes in Task 3):

```html
{% extends "base.html" %}
{% block title %}Notes{% endblock %}
{% block content %}
<div class="notes-body">
    <div id="notes-loading">Loading…</div>
    <div id="notes-content"></div>
</div>
{% endblock %}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest test_app.py::FloatingpointAppTestCase::test_notes_page test_app.py::FloatingpointAppTestCase::test_notes_content -v
```

Expected: both PASS.

- [ ] **Step 6: Run the full test suite to check for regressions**

```bash
python -m pytest test_app.py -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit**

```bash
git add test_app.py app.py templates/notes.html
git commit -m "feat: add /notes and /notes/content routes"
```

---

### Task 2: Add Notes link to the nav

**Files:**
- Modify: `templates/base.html`

- [ ] **Step 1: Add the nav link**

In `templates/base.html`, find the nav block (around line 163–168):

```html
        <a href="{{ url_for('segment_form') }}" {% if nav_active == 'segment' %}class="active"{% endif %}>Segment / ULP</a>
    </nav>
```

Replace it with:

```html
        <a href="{{ url_for('segment_form') }}" {% if nav_active == 'segment' %}class="active"{% endif %}>Segment / ULP</a>
        <a href="{{ url_for('notes') }}" {% if nav_active == 'notes' %}class="active"{% endif %}>Notes</a>
    </nav>
```

- [ ] **Step 2: Run the full test suite**

```bash
python -m pytest test_app.py -v
```

Expected: all tests PASS.

- [ ] **Step 3: Commit**

```bash
git add templates/base.html
git commit -m "feat: add Notes link to nav"
```

---

### Task 3: Build the full notes.html template

**Files:**
- Modify: `templates/notes.html`

- [ ] **Step 1: Replace notes.html with the full template**

Overwrite `templates/notes.html` with:

```html
{% extends "base.html" %}
{% block title %}Notes{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css">
<style>
.notes-body {
    max-width: 680px;
    margin: 0 auto;
    font-size: 17px;
    line-height: 1.75;
    color: #333;
}
.notes-body h1 {
    text-align: left;
}
.notes-body h2 {
    border-left: 4px solid #2e7d32;
    padding-left: 12px;
    color: #1b5e20;
    margin-top: 2em;
}
.notes-body h3 {
    border-left: 3px solid #4CAF50;
    padding-left: 10px;
    color: #2e7d32;
    margin-top: 1.5em;
}
.notes-body h4 {
    color: #333;
    margin-top: 1.25em;
}
.notes-body pre {
    background: #1e1e1e;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    font-size: 14px;
    line-height: 1.5;
}
.notes-body code:not(.hljs) {
    background: #e9ecef;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 15px;
    font-family: 'Courier New', monospace;
}
.notes-body blockquote {
    border-left: 4px solid #ddd;
    margin: 0;
    padding-left: 16px;
    color: #666;
}
.notes-body table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 15px;
}
.notes-body th,
.notes-body td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}
.notes-body th {
    background: #f5f5f5;
    font-weight: bold;
}
.notes-body .katex-display {
    overflow-x: auto;
    padding: 8px 0;
    margin: 1em 0;
}
#notes-loading {
    color: #666;
    text-align: center;
    padding: 40px 0;
}
</style>
{% endblock %}

{% block content %}
<div class="notes-body">
    <div id="notes-loading">Loading…</div>
    <div id="notes-content"></div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/contrib/auto-render.min.js"></script>
<script>
  marked.use({
    renderer: {
      code({ text, lang }) {
        const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext';
        const highlighted = hljs.highlight(text, { language }).value;
        return `<pre><code class="hljs">${highlighted}</code></pre>`;
      }
    }
  });

  (async () => {
    const loading = document.getElementById('notes-loading');
    const content = document.getElementById('notes-content');
    try {
      const res = await fetch('/notes/content');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const text = await res.text();
      content.innerHTML = marked.parse(text);
      renderMathInElement(content, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$',  right: '$',  display: false }
        ],
        throwOnError: false
      });
    } catch (err) {
      content.innerHTML = `<p style="color:#721c24">Failed to load notes: ${err.message}</p>`;
    } finally {
      loading.style.display = 'none';
    }
  })();
</script>
{% endblock %}
```

- [ ] **Step 2: Run the full test suite**

```bash
python -m pytest test_app.py -v
```

Expected: all tests PASS (the template change doesn't affect route tests).

- [ ] **Step 3: Smoke-test in the browser**

Start the app:

```bash
python app.py
```

Open `http://localhost:8080/notes` and verify:
- The page loads with nav showing "Notes" as active
- Content renders (headings, paragraphs visible within a few seconds)
- Code blocks have syntax highlighting (dark background, colored tokens)
- A math formula like the `N = (-1)^s \cdot ...` block renders as typeset math, not raw LaTeX
- Anchor links in the outline at the top (e.g. "Intuition: floats vs reals") scroll to the correct section

- [ ] **Step 4: Commit**

```bash
git add templates/notes.html
git commit -m "feat: render floating-point notes with markdown, syntax highlight, and KaTeX"
```
