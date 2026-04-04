# Segment Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `length` (segment span) and `float_index` (position of queried float within its segment) to the Segment / ULP tool.

**Architecture:** `length` is a segment-level quantity added to the `Segment` domain class in `fp.py`. `float_index` depends on both the segment and the specific float, so it is computed in the `segment_process` route in `app.py` and returned in the JSON response alongside `length`. The template `segment.html` displays both new fields.

**Tech Stack:** Python 3.11, `decimal.Decimal` (400-bit precision), Flask, Jinja2, vanilla JS (existing fetch pattern)

---

### Task 1: Extend `Segment` with `length`

**Files:**
- Modify: `fp.py` — `Segment.__init__`, `Segment.from_exponent`, `Segment.__repr__`, `Segment.__eq__`
- Test: `fp_test.py` — add new test, update existing parametrized expectations

- [ ] **Step 1: Write the failing test**

Add this test to `fp_test.py` (after the existing `test_segment_from_fp` block):

```python
@pytest.mark.parametrize(
    "exponent,expected_length",
    [
        (52, Decimal('4503599627370495')),
        (9,  Decimal('511.9999999999998863131622783839702606201171875')),
    ]
)
def test_segment_length(exponent, expected_length):
    seg = Segment.from_exponent(exponent, ctx)
    assert seg.length == expected_length
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/fab/projects/floatingpoint && source .venv/bin/activate && pytest fp_test.py::test_segment_length -v
```

Expected: `FAILED` — `AttributeError: 'Segment' object has no attribute 'length'`

- [ ] **Step 3: Update `Segment.__init__` to accept `length`**

In `fp.py`, replace the `Segment.__init__` signature and body:

```python
def __init__(self, unbiased_exp: int, min_val: Decimal, max_val: Decimal, distance: Decimal, length: Decimal) -> None:
    self.unbiased_exp = unbiased_exp
    self.min_val = min_val
    self.max_val = max_val
    self.distance = distance
    self.length = length
```

- [ ] **Step 4: Compute `length` in `Segment.from_exponent`**

In `fp.py`, replace the `from_exponent` static method body:

```python
@staticmethod
def from_exponent(e: int, ctx: Context) -> "Segment":
    """Calculate the segment corresponding to the unbiased exponent 'e'
    """
    setcontext(ctx)
    p = 52
    two = Decimal(2)
    min_val: Decimal = two**e
    max_val: Decimal = two**(e + 1) * (1 - two**(-p - 1))
    distance: Decimal = two**(e - p)
    length: Decimal = (max_val - min_val).normalize()
    return Segment(e, min_val.normalize(), max_val.normalize(), distance.normalize(), length)
```

- [ ] **Step 5: Update `__repr__` and `__eq__`**

Replace `Segment.__repr__`:

```python
def __repr__(self):
    return f"Segment(unbiased_exp={self.unbiased_exp}, min_val={self.min_val}, max_val={self.max_val}, distance={self.distance}, length={self.length})"
```

Replace `Segment.__eq__`:

```python
def __eq__(self, other):
    return (self.unbiased_exp == other.unbiased_exp
            and self.min_val == other.min_val
            and self.max_val == other.max_val
            and self.distance == other.distance
            and self.length == other.length)
```

- [ ] **Step 6: Update existing parametrized test data to include `length`**

In `fp_test.py`, the existing `test_segment_from_exponent` and `test_segment_from_fp` parametrize blocks construct `Segment(...)` directly. Update both to pass `length` as the fifth argument:

```python
@pytest.mark.parametrize(
    "data,expected",
    [
        ((9, ctx), Segment(9, Decimal('512'), Decimal('1023.9999999999998863131622783839702606201171875'), Decimal('1.136868377216160297393798828125E-13'), Decimal('511.9999999999998863131622783839702606201171875'))),
        ((52, ctx), Segment(52, Decimal('4503599627370496'), Decimal('9007199254740991'), Decimal('1'), Decimal('4503599627370495'))),
    ]
)
def test_segment_from_exponent(data, expected):
    assert Segment.from_exponent(*data) == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ((1023.0, ctx), Segment(9, Decimal('512'), Decimal('1023.9999999999998863131622783839702606201171875'), Decimal('1.136868377216160297393798828125E-13'), Decimal('511.9999999999998863131622783839702606201171875'))),
        ((4503599627370497.0, ctx), Segment(52, Decimal('4503599627370496'), Decimal('9007199254740991'), Decimal('1'), Decimal('4503599627370495'))),
    ]
)
def test_segment_from_fp(data, expected):
    assert Segment.from_fp(*data) == expected
```

- [ ] **Step 7: Run all unit tests to verify they pass**

```bash
pytest fp_test.py -v
```

Expected: all tests `PASSED`

- [ ] **Step 8: Commit**

```bash
git add fp.py fp_test.py
git commit -m "feat: add length attribute to Segment class"
```

---

### Task 2: Add `float_index` and `length` to the segment route

**Files:**
- Modify: `app.py` — `segment_process` route
- Test: `test_app.py` — update `test_segment_with_one`, add `test_segment_float_index`

- [ ] **Step 1: Write the failing integration tests**

In `test_app.py`, update `test_segment_with_one` to assert the two new fields:

```python
def test_segment_with_one(self) -> None:
    response = self.client.post("/segment", data={"decimal": "1.0"})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    self.assertEqual(data["input"], "1.0")
    self.assertEqual(data["fp"], 1.0)
    self.assertEqual(data["unbiased_exp"], 0)
    self.assertEqual(data["min_val"], "1")
    self.assertEqual(
        data["max_val"],
        "1.9999999999999997779553950749686919152736663818359375",
    )
    self.assertEqual(
        data["distance"],
        "2.220446049250313080847263336181640625E-16",
    )
    self.assertEqual(
        data["length"],
        "0.9999999999999997779553950749686919152736663818359375",
    )
    self.assertEqual(data["float_index"], 0)
```

Also add a new test for a float that is not at the segment boundary:

```python
def test_segment_float_index_nonzero(self) -> None:
    # 4503599627370497.0 is the second float in the e=52 segment (index 1)
    response = self.client.post("/segment", data={"decimal": "4503599627370497"})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    self.assertEqual(data["float_index"], 1)
    self.assertEqual(data["length"], "4503599627370495")
```

- [ ] **Step 2: Run the failing tests**

```bash
pytest test_app.py::FloatingpointAppTestCase::test_segment_with_one test_app.py::FloatingpointAppTestCase::test_segment_float_index_nonzero -v
```

Expected: `FAILED` — `KeyError: 'length'` and `KeyError: 'float_index'`

- [ ] **Step 3: Update `segment_process` in `app.py`**

Replace the `return jsonify(...)` block in `segment_process`:

```python
float_index = int((fp_obj.exact_decimal - seg.min_val) / seg.distance)
return jsonify({
    "input": decimal_input,
    "fp": fp_obj.fp,
    "unbiased_exp": seg.unbiased_exp,
    "min_val": str(seg.min_val),
    "max_val": str(seg.max_val),
    "distance": str(seg.distance),
    "length": str(seg.length),
    "float_index": float_index,
})
```

- [ ] **Step 4: Run the integration tests to verify they pass**

```bash
pytest test_app.py -v
```

Expected: all tests `PASSED`

- [ ] **Step 5: Commit**

```bash
git add app.py test_app.py
git commit -m "feat: return segment length and float index from /segment route"
```

---

### Task 3: Display `length` and `float_index` in the template

**Files:**
- Modify: `templates/segment.html`

- [ ] **Step 1: Add two new rows to the result display**

In `templates/segment.html`, replace the `result.innerHTML` template literal inside the `.then(data => ...)` block:

```javascript
result.innerHTML = `
    <div class="result-content">
        <strong>Input:</strong> ${data.input}<br>
        <strong>Float (Python):</strong> ${data.fp}<br>
        <strong>Unbiased exponent (segment e):</strong> ${data.unbiased_exp}<br>
        <strong>Segment min (exact decimal):</strong> ${data.min_val}<br>
        <strong>Segment max (exact decimal):</strong> ${data.max_val}<br>
        <strong>Segment length (exact decimal):</strong> ${data.length}<br>
        <strong>ULP / spacing (exact decimal):</strong> ${data.distance}<br>
        <strong>Float index in segment:</strong> ${data.float_index} of 4503599627370496
    </div>
`;
```

- [ ] **Step 2: Run the full test suite to confirm nothing is broken**

```bash
pytest test_app.py fp_test.py -v
```

Expected: all tests `PASSED`

- [ ] **Step 3: Smoke-test in the browser**

Start the dev server:

```bash
python app.py
```

Navigate to `http://localhost:8080/segment`, enter `1.0`, and verify the result shows:
- `Segment length (exact decimal): 0.9999999999999997779553950749686919152736663818359375`
- `Float index in segment: 0 of 4503599627370496`

Enter `4503599627370497` and verify `Float index in segment: 1 of 4503599627370496`.

- [ ] **Step 4: Commit**

```bash
git add templates/segment.html
git commit -m "feat: display segment length and float index in segment tool UI"
```
