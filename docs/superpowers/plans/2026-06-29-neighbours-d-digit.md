# Neighbours d-digit Count Table Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the `/neighbours` page to show results in a table including an optional count of d-digit decimal numbers that round to each neighbour.

**Architecture:** The backend route is extended to parse an optional `d` parameter, build a `rows` list that starts with the seed float (row 0) followed by the n neighbours, and optionally call `FP.get_d_digit_decimals(d)` per row. The frontend replaces the `<ol>` with a `<table>`, conditionally rendering a third column when `d` is present in the JSON response.

**Tech Stack:** Python 3.11, Flask, Jinja2, vanilla JavaScript (fetch API), `FP.get_d_digit_decimals` from `fp.py`.

## Global Constraints

- Branch off from `docs/neighbours-d-digit-spec`; create branch `feat/neighbours-d-digit`
- Never commit directly to `main`
- Angular commit message format (`feat:`, `test:`, `fix:` prefixes)
- Type hints and docstrings on all Python functions/methods
- Input validated and sanitised at route boundary before use
- `d` valid range: integer in `[1, 50]` (same as `/exact-decimal`)
- Tests use `unittest.TestCase` in `test_app.py`; run with `pytest test_app.py`

---

## File Map

| File | Change |
|---|---|
| `test_app.py` | Update 2 existing tests; add 5 new tests |
| `app.py` | Extend `neighbours_process` route |
| `templates/neighbours.html` | Add `d` field; replace `<ol>` with `<table>` |

---

### Task 1: Create feature branch and update/add tests

**Files:**
- Modify: `test_app.py` (lines 123–132, 158–162)

**Interfaces:**
- Produces: failing tests that define the new response contract consumed by Task 2

- [ ] **Step 1: Create the feature branch**

```bash
git checkout docs/neighbours-d-digit-spec
git checkout -b feat/neighbours-d-digit
```

Expected: prompt shows `feat/neighbours-d-digit`.

- [ ] **Step 2: Update `test_neighbours_valid` to match new response shape**

The response no longer has `"fp"` or `"neighbours"` keys. It now has `"rows"` (seed + neighbours) and no `"d"` key when `d` is absent.

In `test_app.py`, replace `test_neighbours_valid` (lines 123–132):

```python
def test_neighbours_valid(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "0.1", "n": "3"})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    self.assertEqual(data["input"], "0.1")
    self.assertNotIn("d", data)
    self.assertEqual(len(data["rows"]), 4)  # seed + 3 neighbours
    self.assertEqual(data["rows"][0]["fp"], 0.1)
    self.assertEqual(data["rows"][1]["fp"], 0.10000000000000002)
    self.assertEqual(data["rows"][2]["fp"], 0.10000000000000003)
    self.assertEqual(data["rows"][3]["fp"], 0.10000000000000005)
    for row in data["rows"]:
        self.assertNotIn("d_digit_count", row)
```

- [ ] **Step 3: Update `test_neighbours_n_at_cap` to match new response shape**

In `test_app.py`, replace `test_neighbours_n_at_cap` (lines 158–162):

```python
def test_neighbours_n_at_cap(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "1.0", "n": "1000"})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    self.assertEqual(len(data["rows"]), 1001)  # seed + 1000 neighbours
```

- [ ] **Step 4: Add new tests for the `d` parameter**

Append these tests inside `class AppTestCase` in `test_app.py`, after `test_neighbours_n_not_integer`:

```python
def test_neighbours_with_d(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "0.1", "n": "2", "d": "15"})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    self.assertEqual(data["d"], 15)
    self.assertEqual(len(data["rows"]), 3)  # seed + 2 neighbours
    for row in data["rows"]:
        self.assertIn("d_digit_count", row)
        self.assertTrue(row["d_digit_count"] is None or isinstance(row["d_digit_count"], int))

def test_neighbours_d_exceeds_digits_shows_null(self) -> None:
    # 1.0 has exact decimal Decimal('1') — 1 significant digit.
    # d=2 exceeds that, so get_d_digit_decimals raises ValueError → null for all rows.
    response = self.client.post("/neighbours", data={"decimal": "1.0", "n": "2", "d": "2"})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    self.assertEqual(data["d"], 2)
    for row in data["rows"]:
        self.assertIn("d_digit_count", row)
        self.assertIsNone(row["d_digit_count"])

def test_neighbours_d_out_of_range(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "0.1", "n": "3", "d": "51"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)

def test_neighbours_d_zero(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "0.1", "n": "3", "d": "0"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)

def test_neighbours_d_not_integer(self) -> None:
    response = self.client.post("/neighbours", data={"decimal": "0.1", "n": "3", "d": "abc"})
    self.assertEqual(response.status_code, 400)
    data = json.loads(response.data)
    self.assertIn("error", data)
```

- [ ] **Step 5: Run tests — expect failures on the updated and new tests**

```bash
pytest test_app.py -v
```

Expected: `test_neighbours_valid`, `test_neighbours_n_at_cap`, `test_neighbours_with_d`, `test_neighbours_d_exceeds_digits_shows_null`, `test_neighbours_d_out_of_range`, `test_neighbours_d_zero`, `test_neighbours_d_not_integer` all FAIL. All other existing tests still PASS.

- [ ] **Step 6: Commit tests**

```bash
git add test_app.py
git commit -m "test: update neighbours tests for tabular response with d-digit count"
```

---

### Task 2: Update `neighbours_process` in `app.py`

**Files:**
- Modify: `app.py:130-177`

**Interfaces:**
- Consumes: `FP.from_float(float_value)` → `FP`, `seed.fp_gen()` → generator, `fp_obj.get_d_digit_decimals(d)` → `(int, Decimal, list)`
- Produces: JSON `{"input": str, "d": int|absent, "rows": [{"fp": float, "d_digit_count": int|null}]}`

- [ ] **Step 1: Replace `neighbours_process` in `app.py`**

Replace the entire `neighbours_process` function (from `@app.route("/neighbours", methods=["POST"])` through the closing `}`) with:

```python
@app.route("/neighbours", methods=["POST"])
def neighbours_process():  # pylint: disable=too-many-return-statements
    """Return seed + next n consecutive floats, with optional d-digit decimal counts per row."""
    decimal_input = request.form.get("decimal", "").strip()
    n_input = request.form.get("n", "").strip()
    d_input = request.form.get("d", "").strip()

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

    if float_value < 0 or (float_value == 0.0 and math.copysign(1, float_value) < 0):
        return jsonify({"error": "Please enter a non-negative number (≥ 0)."}), 400

    try:
        n = int(n_input)
    except ValueError:
        return jsonify({"error": "Count n must be a positive integer."}), 400

    if n < 1 or n > 1000:
        return jsonify({"error": "Count n must be between 1 and 1000."}), 400

    d = None
    if d_input:
        try:
            d = int(d_input)
        except ValueError:
            return jsonify({"error": "Significant digits d must be a positive integer."}), 400
        if d < 1 or d > 50:
            return jsonify({"error": "Significant digits d must be between 1 and 50."}), 400

    seed = FP.from_float(float_value)
    fp_objects = [seed]
    try:
        gen = seed.fp_gen()
        next(gen)  # skip the seed itself
        for fp_obj in gen:
            fp_objects.append(fp_obj)
            if len(fp_objects) == n + 1:
                break
    except OverflowError:
        return jsonify({"error": "Reached infinity before collecting enough neighbours."}), 400

    def make_row(fp_obj: FP) -> dict:
        """Build a single response row, optionally including d-digit count."""
        row: dict = {"fp": fp_obj.fp}
        if d is not None:
            try:
                count, _, _ = fp_obj.get_d_digit_decimals(d)
                row["d_digit_count"] = count
            except ValueError:
                row["d_digit_count"] = None
        return row

    result: dict = {
        "input": decimal_input,
        "rows": [make_row(fp_obj) for fp_obj in fp_objects],
    }
    if d is not None:
        result["d"] = d

    return jsonify(result)
```

- [ ] **Step 2: Run tests — all should pass**

```bash
pytest test_app.py -v
```

Expected: all tests PASS including the 7 updated/new neighbour tests.

- [ ] **Step 3: Commit backend**

```bash
git add app.py
git commit -m "feat: extend neighbours route with d-digit count per row and seed in response"
```

---

### Task 3: Update `templates/neighbours.html`

**Files:**
- Modify: `templates/neighbours.html`

**Interfaces:**
- Consumes: JSON from Task 2 — `{input, d?, rows: [{fp, d_digit_count?}]}`

- [ ] **Step 1: Replace the entire contents of `templates/neighbours.html`**

```html
{% extends "base.html" %}
{% block title %}Neighbours{% endblock %}
{% block extra_css %}
<style>
    .neighbours-table {
        border-collapse: collapse;
        width: 100%;
        margin-top: 12px;
        font-family: 'Courier New', monospace;
        font-size: 0.95em;
    }
    .neighbours-table th,
    .neighbours-table td {
        border: 1px solid #c3e6cb;
        padding: 6px 12px;
        text-align: left;
    }
    .neighbours-table th {
        background-color: #b8dfc0;
        font-family: sans-serif;
        font-size: 0.9em;
    }
    .neighbours-table tr.seed-row td {
        font-weight: bold;
        background-color: rgba(0,0,0,0.06);
    }
</style>
{% endblock %}
{% block content %}
<h1>Neighbours</h1>
<p>Given a non-negative float and a count <strong>n</strong> (1–1000), lists the seed float (row 0)
   and the next <em>n</em> consecutive representable IEEE-754 double-precision floats in ascending
   order. Optionally, provide <strong>d</strong> (1–50) to also show how many d-digit decimal numbers
   round to each float.</p>

<form id="neighboursForm">
    <div class="form-group">
        <label for="decimal">Number (must be ≥ 0):</label>
        <input type="text" id="decimal" name="decimal" required placeholder="e.g., 0.1, 1.0, 1024">
    </div>
    <div class="form-group">
        <label for="n">Count (n, 1–1000):</label>
        <input type="number" id="n" name="n" required min="1" max="1000" placeholder="e.g., 10">
    </div>
    <div class="form-group">
        <label for="d">Significant digits (d, 1–50, optional):</label>
        <input type="number" id="d" name="d" min="1" max="50" placeholder="e.g., 15">
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
        const d = document.getElementById('d').value.trim();
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
        if (d) formData.append('d', d);
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
                    const showD = 'd' in data;
                    const headerCells = showD
                        ? '<th>#</th><th>Float (Python repr)</th><th>d-digit count</th>'
                        : '<th>#</th><th>Float (Python repr)</th>';
                    const bodyRows = data.rows.map((row, i) => {
                        const seedClass = i === 0 ? ' class="seed-row"' : '';
                        const cells = showD
                            ? `<td>${i}</td><td>${row.fp}</td><td>${row.d_digit_count === null ? 'N/A' : row.d_digit_count}</td>`
                            : `<td>${i}</td><td>${row.fp}</td>`;
                        return `<tr${seedClass}>${cells}</tr>`;
                    }).join('');
                    result.innerHTML = `
                        <div class="result-content">
                            <strong>Input:</strong> ${data.input}<br>
                            ${showD ? `<strong>d:</strong> ${data.d}<br>` : ''}
                            <table class="neighbours-table">
                                <thead><tr>${headerCells}</tr></thead>
                                <tbody>${bodyRows}</tbody>
                            </table>
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

- [ ] **Step 2: Run the full test suite to confirm nothing is broken**

```bash
pytest test_app.py fp_test.py -v
```

Expected: all tests PASS.

- [ ] **Step 3: Manually verify the page in the browser**

```bash
python app.py
```

Open `http://localhost:8080/neighbours`. Verify:
- Three form fields render correctly; `d` is optional.
- Submit with `decimal=0.1`, `n=5`, no `d` → table shows 6 rows (seed + 5), two columns (`#`, `Float`). Row 0 is bold.
- Submit the same with `d=15` → table gains `d-digit count` column; each cell shows an integer.
- Submit with `decimal=1.0`, `n=3`, `d=2` → d-digit count column shows `N/A` for all rows (1.0's exact decimal has only 1 significant digit).
- Submit with `d=51` → error message displayed.

- [ ] **Step 4: Commit frontend**

```bash
git add templates/neighbours.html
git commit -m "feat: replace neighbours list with table and add optional d-digit count column"
```

---

### Task 4: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Find the `/neighbours` section in `README.md` and update it**

Locate the section describing the `/neighbours` page. Update it to reflect:
- The form now accepts an optional `d` field (1–50 significant digits).
- Results are shown as a table (row 0 = seed, rows 1–n = neighbours).
- When `d` is provided, a third column shows the count of d-digit decimal numbers that round to each float.

- [ ] **Step 2: Commit README**

```bash
git add README.md
git commit -m "docs: update README for neighbours tabular output and d-digit count"
```
