# Segment Tool Enrichment — Design Spec

**Date:** 2026-04-04

## Summary

Enrich the existing Segment / ULP tool with two additional properties:

- **Segment length** — the total real-number span covered by the binade (`max − min`)
- **Float index in segment** — the 0-based position of the queried float among the `2^52` floats in its segment

Both values are exact and are already derivable from existing `Segment` and `FP` data; no new I/O or external dependencies are required.

## Architecture

The change touches three layers: domain (`fp.py`), route (`app.py`), and template (`segment.html`), plus tests.

### `fp.py` — `Segment` class

Add a `length: Decimal` attribute.

- Computed in `from_exponent`: `length = (max_val - min_val).normalize()`
- Added to `__init__` signature and stored as `self.length`
- Included in `__repr__` and `__eq__`

`length` is a segment-level quantity (depends only on the exponent, not on any specific float), so it belongs on `Segment` alongside `min_val`, `max_val`, and `distance`.

### `app.py` — `segment_process` route

After constructing `seg` and `fp_obj`, compute the float index:

```python
float_index = int((fp_obj.exact_decimal - seg.min_val) / seg.distance)
```

This is an exact integer because `exact_decimal`, `min_val`, and `distance` are all high-precision `Decimal` values representing exact IEEE-754 quantities.

Add to the JSON payload:

```python
"length": str(seg.length),
"float_index": float_index,
```

`float_index` is a two-argument computation (float + segment), so the route handler is the right place for it.

### `segment.html` — result display

Add two new rows after the existing ULP / spacing row:

- **Segment length (exact decimal):** `data.length`
- **Float index in segment:** rendered as `{data.float_index} of 4503599627370496` to give the denominator context (2^52, always the same for double precision)

## Data Flow

```
User input (decimal string)
  → POST /segment
  → float(input) → Segment.from_fp() → seg.length (new)
  → FP.from_float() → (fp.exact_decimal - seg.min_val) / seg.distance → float_index (new)
  → JSON response: { ..., length, float_index }
  → segment.html renders two new rows
```

## Error Handling

No new error cases. Both computations are always valid for any finite float that passes the existing validation (non-NaN, non-infinite).

## Testing

**Unit test (`fp_test.py`):**
- For a known exponent `e`, assert `Segment.from_exponent(e, ctx).length == expected_length`
- Verify `__eq__` and `__repr__` include `length`

**Integration test (`test_app.py`):**
- POST a known value to `/segment`
- Assert `length` and `float_index` are present in the response
- Assert their values match hand-computed expectations for the chosen input
