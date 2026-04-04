# Floatingpoint

A small Flask app that explains **IEEE-754 binary64** (double-precision): exact value of a float, how decimal literals map to bits, and **binade / ULP** spacing. It is meant to complement reading about floating-point and to contrast **when `float` is appropriate** (performance, tolerant numerics) **vs arbitrary precision** such as Python’s `Decimal` (money, controlled decimal rounding).

## Features

- **Home** — mission, float vs `Decimal` guidance, links to tools
- **Exact value** — `FP.from_float`, exact rational decimal, d-digit decimal strings that round to the same float
- **Segment / ULP** — unbiased exponent band, segment bounds, ULP, segment length, float index within segment
- **Notes** — [Floating-point distribution, decimals, and precision](docs/floating-point-distribution-and-precision.md) rendered client-side with syntax highlighting and KaTeX math

## Requirements

- **Python 3.11** (or **3.10+**; the codebase uses `match` / `case`)
- Flask (see `requirements.txt`)

## Installation

1. Clone the repository and enter the project directory.

2. Create and activate a virtual environment, then install dependencies:

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Running tests

With the virtual environment activated:

```bash
pytest test_app.py   # integration tests
pytest fp_test.py    # unit tests for FP/bit logic
```

## Running the application

```bash
python app.py
```

Open [http://localhost:8080](http://localhost:8080).

## Routes

| Path | Purpose |
|------|---------|
| `GET /` | Home |
| `GET /exact-decimal` | Exact value tool (form) |
| `POST /exact-decimal` | Exact value tool (JSON API) |
| `GET /segment` | Segment / ULP tool (form) |
| `POST /segment` | Segment / ULP tool (JSON API) |
| `GET /notes` | Notes page |
| `GET /notes/content` | Raw markdown served for client-side rendering |

## Architecture

- **Core logic**: `fp.py`, `fputil.py`
- **Web**: `app.py`, templates under `templates/`

API-style responses expose only what is needed for FP insight (e.g. `fp`, `bits`, `exact_decimal`, `unbiased_exp` where applicable; segment adds `min_val`, `max_val`, `distance`, `length`, `float_index`, `num_floats`).
