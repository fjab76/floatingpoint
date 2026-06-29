# Neighbours Page — Design Spec

**Date:** 2026-06-29

## Overview

A new tool page at `/neighbours` that accepts a seed float and a count `n`, then displays the next `n` consecutive representable IEEE-754 double-precision floats in ascending order.

## Architecture

### Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/neighbours` | Render form page |
| POST | `/neighbours` | Process input, return JSON |

Both routes added to `app.py`, following the same pattern as `/segment` and `/exact-decimal`.

### Navigation

`base.html` nav bar gets a new "Neighbours" link with `nav_active="neighbours"`.

## Backend (`app.py`)

**Input validation:**
- `decimal`: must be a non-empty string parseable as `float`; reject `inf` and `NaN`
- `n`: must be a positive integer; server-side cap of 1000 to prevent runaway generation

**Processing:**
1. `FP.from_float(float_value)` to get the seed `FP` object
2. Call `fp_gen()` on the seed, skip the seed itself, collect `n` values
3. Stop early and return an error if the generator raises `OverflowError` (hits infinity)

**Response payload (success):**
```json
{
  "input": "0.1",
  "fp": 0.1,
  "neighbours": [0.10000000000000002, 0.10000000000000003, ...]
}
```

**Error responses:** same `{"error": "..."}` / 400 pattern as other routes.

## Frontend (`templates/neighbours.html`)

- Extends `base.html`
- Two form fields:
  - "Number" — text input, placeholder `e.g., 0.1, 1.0`
  - "n" — number input, `min="1"`, `max="1000"`, placeholder `e.g., 10`
- Submit triggers AJAX POST (same fetch/FormData pattern as other pages)
- Loading state: shared `.loading` div
- Success: render a numbered `<ol>` list of float values inside `.result.success`
- Error: render message inside `.result.error`
- No new CSS needed — reuses all existing classes from `base.html`

## Constraints & Edge Cases

- `n` is capped at 1000 server-side; the UI notes this cap
- Generator hitting infinity returns a partial result with an explanatory note, or a 400 error — error path is simpler and consistent with other routes
- Negative and subnormal floats are valid inputs (fp_gen asserts seed >= 0, so negative inputs are rejected with a clear error)

## Testing

- Integration tests in `test_app.py`: GET returns 200, POST with valid input returns correct neighbour count, POST with invalid float returns 400, POST with n > 1000 returns 400, POST with negative float returns 400
- No new unit tests needed in `fp_test.py` — `fp_gen` is already tested there
