# Neighbours Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/neighbours` page that accepts a seed float and count `n`, then lists the next `n` consecutive representable IEEE-754 doubles in ascending order.

**Architecture:** Two new Flask routes (GET renders form, POST returns JSON) in `app.py`, one new Jinja2 template extending `base.html`, and a nav link. Backend uses `FP.from_float()` + `fp_gen()` (skipping the seed) to generate neighbours. All work is done on a feature branch — never commit to `main`.

**Tech Stack:** Python 3.11, Flask, Jinja2, `fp.py` (`FP`, `fp_gen`), vanilla JS fetch API, `unittest`/pytest.

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `app.py` | Modify | Add `GET /neighbours` and `POST /neighbours` routes |
| `templates/base.html` | Modify | Add "Neighbours" nav link |
| `templates/neighbours.html` | Create | Form, AJAX fetch, result list rendering |
| `test_app.py` | Modify | Integration tests for both routes |

---

### Task 1: Create feature branch

**Files:**
- (git only)

- [ ] **Step 1: Create and switch to feature branch**

```bash
git checkout -b feat/neighbours
```

Expected: `Switched to a new branch 'feat/neighbours'`

---

### Task 2: Failing tests for GET /neighbours

**Files:**
- Modify: `test_app.py`

- [ ] **Step 1: Add GET test to `test_app.py`**

Add this method inside `FloatingpointAppTestCase`:

```python
def test_neighbours_page(self) -> None:
    response = self.client.get("/neighbours")
    self.assertEqual(response.status_code, 200)
    self.assertIn(b"Neighbours", response.data)
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
pytest test_app.py::FloatingpointAppTestCase::test_neighbours_page -v
```

Expected: FAIL — `404 != 200` (route does not exist yet)

---

### Task 3: Implement GET /neighbours + minimal template + nav link

**Files:**
- Modify: `app.py`
- Create: `templates/neighbours.html`
- Modify: `templates/base.html`

- [ ] **Step 1: Add the GET route to `app.py`**

Add after the `/segment` routes (before `/notes`):

```python
@app.route("/neighbours")
def neighbours_form():
    """Serve the consecutive-neighbours explorer page."""
    return render_template("neighbours.html", nav_active="neighbours")
```

- [ ] **Step 2: Create `templates/neighbours.html`**

```html
{% extends "base.html" %}
{% block title %}Neighbours{% endblock %}
{% block content %}
<h1>Neighbours</h1>
<p>Given a non-negative float and a count <strong>n</strong> (1–1000), lists the next
   <em>n</em> consecutive representable IEEE-754 double-precision floats in ascending
   order. Each step is one ULP in the current binade.</p>

<form id="neighboursForm">
    <div class="form-group">
        <label for="decimal">Number (must be ≥ 0):</label>
        <input type="text" id="decimal" name="decimal" required placeholder="e.g., 0.1, 1.0, 1024">
    </div>
    <div class="form-group">
        <label for="n">Count (n, 1–1000):</label>
        <input type="number" id="n" name="n" required min="1" max="1000" placeholder="e.g., 10">
    </div>
    <button type="submit">Show neighbours</button>
</form>

<div class="loading" id="loading">Processing your request...</div>
<div class="result" id="result"></div>
{% endblock %}

{% block extra_js %}
<script>
    document.getElementById('neighboursForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const decimal = document.getElementById('decimal').value.trim();
        const n = document.getElementById('n').value.trim();
        const button = document.querySelector('#neighboursForm button[type="submit"]');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');
        result.style.display = 'none';
        result.className = 'result';
        loading.style.display = 'block';
        button.disabled = true;
        const formData = new FormData();
        formData.append('decimal', decimal);
        formData.append('n', n);
        fetch('/neighbours', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                loading.style.display = 'none';
                button.disabled = false;
                if (data.error) {
                    result.className = 'result error';
                    result.textContent = data.error;
                } else {
                    result.className = 'result success';
                    const items = data.neighbours.map(v => `<li>${v}</li>`).join('');
                    result.innerHTML = `
                        <div class="result-content">
                            <strong>Input:</strong> ${data.input}<br>
                            <strong>Float (Python):</strong> ${data.fp}<br>
                            <strong>Next ${data.neighbours.length} neighbour(s):</strong>
                            <ol style="margin-top:8px; padding-left:24px;">${items}</ol>
                        </div>`;
                }
                result.style.display = 'block';
            })
            .catch(() => {
                loading.style.display = 'none';
                button.disabled = false;
                result.className = 'result error';
                result.textContent = 'An error occurred. Please try again.';
                result.style.display = 'block';
            });
    });
</script>
{% endblock %}
```

- [ ] **Step 3: Add nav link to `templates/base.html`**

Find the existing notes nav link:
```html
        <a href="{{ url_for('notes') }}" {% if nav_active == 'notes' %}class="active"{% endif %}>Notes</a>
```

Add the neighbours link before it:
```html
        <a href="{{ url_for('neighbours_form') }}" {% if nav_active == 'neighbours' %}class="active"{% endif %}>Neighbours</a>
        <a href="{{ url_for('notes') }}" {% if nav_active == 'notes' %}class="active"{% endif %}>Notes</a>
```

- [ ] **Step 4: Run the GET test to verify it passes**

```bash
pytest test_app.py::FloatingpointAppTestCase::test_neighbours_page -v
```

Expected: PASS

- [ ] **Step 5: Run the full test suite to check for regressions**

```bash
pytest test_app.py -v
```

Expected: all existing tests PASS

- [ ] **Step 6: Commit**

```bash
git add app.py templates/neighbours.html templates/base.html test_app.py
git commit -m "feat: add GET /neighbours route, template and nav link"
```

---

### Task 4: Failing tests for POST /neighbours

**Files:**
- Modify: `test_app.py`

- [ ] **Step 1: Add POST tests to `test_app.py`**

Add these methods inside `FloatingpointAppTestCase`:

```python
def test_neighbours_valid(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "0.1", "n": "3"})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    self.assertEqual(data["input"], "0.1")
    self.assertEqual(data["fp"], 0.1)
    self.assertEqual(len(data["neighbours"]), 3)
    self.assertEqual(data["neighbours"][0], 0.10000000000000002)
    self.assertEqual(data["neighbours"][1], 0.10000000000000003)
    self.assertEqual(data["neighbours"][2], 0.10000000000000005)

def test_neighbours_empty_decimal(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "", "n": "5"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)

def test_neighbours_invalid_decimal(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "abc", "n": "5"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)

def test_neighbours_negative_float(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "-1.0", "n": "5"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)

def test_neighbours_non_finite(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "inf", "n": "5"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)

def test_neighbours_missing_n(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "1.0"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)

def test_neighbours_n_zero(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "1.0", "n": "0"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)

def test_neighbours_n_exceeds_cap(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "1.0", "n": "1001"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)

def test_neighbours_n_not_integer(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "1.0", "n": "abc"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)
```

- [ ] **Step 2: Run the new tests to verify they all fail**

```bash
pytest test_app.py -k "neighbours" -v
```

Expected: `test_neighbours_page` PASSES, all new POST tests FAIL with 405 (method not allowed)

---

### Task 5: Implement POST /neighbours route

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Add the POST route to `app.py`**

Add directly after the `neighbours_form` GET route:

```python
@app.route("/neighbours", methods=["POST"])
def neighbours_process():
    """Return the next n consecutive floats after the given seed float."""
    decimal_input = request.form.get("decimal", "").strip()
    n_input = request.form.get("n", "").strip()

    if not decimal_input:
        return jsonify({"error": "Please enter a number"}), 400

    if not n_input:
        return jsonify({"error": "Please enter a count n"}), 400

    try:
        float_value = float(decimal_input)
    except ValueError:
        return jsonify({"error": "Invalid number. Please enter a valid floating-point literal."}), 400

    if not math.isfinite(float_value):
        return jsonify({"error": "Please enter a finite number (not infinity or NaN)."}), 400

    if float_value < 0:
        return jsonify({"error": "Please enter a non-negative number (≥ 0)."}), 400

    try:
        n = int(n_input)
    except ValueError:
        return jsonify({"error": "Count n must be a positive integer."}), 400

    if n < 1 or n > 1000:
        return jsonify({"error": "Count n must be between 1 and 1000."}), 400

    seed = FP.from_float(float_value)
    neighbours = []
    try:
        gen = seed.fp_gen()
        next(gen)  # skip the seed itself
        for fp_obj in gen:
            neighbours.append(fp_obj.fp)
            if len(neighbours) == n:
                break
    except OverflowError:
        return jsonify({"error": "Reached infinity before collecting enough neighbours."}), 400

    return jsonify({
        "input": decimal_input,
        "fp": seed.fp,
        "neighbours": neighbours,
    })
```

- [ ] **Step 2: Run all neighbours tests**

```bash
pytest test_app.py -k "neighbours" -v
```

Expected: all 10 neighbours tests PASS

- [ ] **Step 3: Run the full test suite**

```bash
pytest test_app.py -v
```

Expected: all tests PASS

- [ ] **Step 4: Run linter**

```bash
pylint app.py
```

Expected: no new errors or warnings (score should remain at 10.00 or match previous score)

- [ ] **Step 5: Commit**

```bash
git add app.py test_app.py
git commit -m "feat: add POST /neighbours route with validation and fp_gen integration"
```

---

### Task 6: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read the current README**

```bash
cat README.md
```

- [ ] **Step 2: Add Neighbours tool to the tools section**

Find the existing tool list (the section describing Exact value, Segment/ULP, etc.) and add an entry for Neighbours. The entry should describe: input (non-negative float + count n, 1–1000), output (ordered list of the next n consecutive representable doubles).

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document /neighbours tool in README"
```

---

### Task 7: Open pull request

**Files:**
- (git/GitHub only)

- [ ] **Step 1: Push feature branch**

```bash
git push -u origin feat/neighbours
```

- [ ] **Step 2: Open PR**

```bash
gh pr create \
  --title "feat: add /neighbours page" \
  --body "$(cat <<'EOF'
## Summary
- Adds GET/POST `/neighbours` route to `app.py`
- New `templates/neighbours.html` with form and AJAX result list
- Nav link in `base.html`
- Integration tests in `test_app.py` (GET, valid POST, 8 invalid-input cases)

## Test plan
- [ ] `pytest test_app.py -v` passes with no failures
- [ ] Visit http://localhost:8080/neighbours — form renders, nav link is active
- [ ] Submit `0.1` / `3` — list shows `0.10000000000000002`, `0.10000000000000003`, `0.10000000000000005`
- [ ] Submit `-1.0` — error shown
- [ ] Submit `inf` — error shown
- [ ] Submit `n=1001` — error shown

🤖 Generated with [Claude Code](https://claude.ai/claude-code)
EOF
)"
```
