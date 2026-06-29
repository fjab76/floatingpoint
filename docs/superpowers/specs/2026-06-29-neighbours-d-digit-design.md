# Design: /neighbours page — tabular output with d-digit counts

**Date:** 2026-06-29  
**Status:** Approved

## Summary

Extend the `/neighbours` page to display results in a table and, optionally, show how many d-digit decimal numbers round to each neighbour. A new optional form field captures the value of `d`.

## Form changes

Add an optional text field `d` (labelled "Significant digits (d, 1–50):") after the existing `n` field.

- Submitting without `d` is valid; the backend treats it as absent.
- Valid range when provided: integer in `[1, 50]` (consistent with `/exact-decimal`).

## Backend changes (`app.py` — `neighbours_process`)

**Validation:**
- If `d` is present and non-empty: parse as `int`; return 400 if outside `[1, 50]`.
- If `d` is absent or empty: skip d-digit computation.

**Computation:**
- Keep the existing neighbour walk but retain the full `FP` objects (not just `.fp`).
- Prepend the seed `FP` to the list so row 0 is the seed itself.
- If `d` was provided, call `fp_obj.get_d_digit_decimals(d)` for each row; catch `ValueError` and emit `None` for that row.

**Response shape (d provided):**
```json
{
  "input": "0.1",
  "d": 10,
  "rows": [
    { "fp": "0.1",                 "d_digit_count": 5    },
    { "fp": "0.10000000000000001", "d_digit_count": null },
    { "fp": "0.10000000000000002", "d_digit_count": 3    }
  ]
}
```

**Response shape (d absent):**
```json
{
  "input": "0.1",
  "rows": [
    { "fp": "0.1"                  },
    { "fp": "0.10000000000000001"  },
    { "fp": "0.10000000000000002"  }
  ]
}
```

The `"d"` key is omitted when not provided. The frontend uses its presence to decide whether to render the d-digit count column.

## Frontend changes (`templates/neighbours.html`)

**Form:** Add optional `<input type="number" id="d" name="d" min="1" max="50">` field.

**Result rendering:** Replace the `<ol>` with an HTML `<table>`:

| # | Float (Python repr) | d-digit count *(column only present when d is in response)* |
|---|---|---|
| 0 | 0.1 *(seed — visually distinguished: bold or light row background)* | 5 |
| 1 | 0.10000000000000001 | N/A |
| 2 | 0.10000000000000002 | 3 |

- Row 0 (seed) is visually distinguished with a light background (`style="background: var(--bg-alt)"` or equivalent from `base.html`).
- `null` from JSON renders as `N/A`.
- When `d` is absent from the response, the third column is omitted entirely (both header and cells).

## Error handling

| Condition | Behaviour |
|---|---|
| `d` present but not integer | 400: "Significant digits d must be a positive integer." |
| `d` present but outside `[1, 50]` | 400: "Significant digits d must be between 1 and 50." |
| `get_d_digit_decimals` raises `ValueError` for a row | `d_digit_count: null` → renders as `N/A` |
| Existing errors (infinity, invalid float, n out of range) | Unchanged |

## Testing

- Existing tests in `test_app.py` must still pass (response shape changes, so update any assertions on `neighbours`).
- New integration tests:
  - POST with valid `d` → response contains `"d"` and `"rows"` with `d_digit_count` values.
  - POST without `d` → response contains `"rows"` with no `d_digit_count` keys, no `"d"` key.
  - POST with `d` out of range → 400.
  - POST where some rows produce `ValueError` → those rows have `d_digit_count: null`.
