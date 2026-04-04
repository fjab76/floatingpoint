# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Commands

```bash
python app.py          # Run dev server at http://localhost:8080 (debug mode on)
pytest test_app.py     # Integration tests (Flask test client)
pytest fp_test.py      # Unit tests for FP/bit logic
pylint fp.py fputil.py app.py  # Lint
```

## Architecture

This is an IEEE-754 floating-point visualization tool (Flask, Python 3.11+).

**Layer separation:**
- `fputil.py` — low-level bit manipulation (pack/unpack IEEE-754, binary conversions)
- `fp.py` — domain logic: `FP` and `Segment` classes, d-digit decimal analysis
- `app.py` — Flask routes: `/`, `/exact-decimal`, `/segment`, `/notes`, `/notes/content`
- `templates/` — Jinja2 templates with `base.html` as the layout base

**Key design decisions:**
- All numeric computation uses Python `Decimal` at 400-bit precision with `ROUND_HALF_UP` — never native floats — to represent exact IEEE-754 values correctly.
- `FP` and `Segment` use static factory methods (`from_float()`, `from_binary()`, `from_decimal()`, etc.) rather than direct constructors.
- `FP.fp_gen()` is a generator that yields consecutive representable floats.

**API response conventions:**
- FP objects expose: `fp`, `bits`, `exact_decimal`, `unbiased_exp`
- Segment objects add: `min_val`, `max_val`, `distance` (ULP) — all as strings (large-precision Decimal)

## Coding Conventions

- Type hints and docstrings on all functions, classes, and methods.
- Single responsibility per function.
- All routes validate and sanitize input before use.
- Tests: integration tests in `test_app.py`, unit tests in `fp_test.py`; both use `unittest.TestCase` (pytest-compatible).

## Version control system

- Code is hosted in GitHub
- All new features must be developed in a new branch
- NEVER commit directly to the main branch
- Follow the angular commit formatting
