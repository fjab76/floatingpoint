# Floatingpoint

A small Flask app that explains **IEEE-754 binary64** (double-precision): exact value of a float, how decimal literals map to bits, and **binade / ULP** spacing. It is meant to complement reading about floating-point and to contrast **when `float` is appropriate** (performance, tolerant numerics) **vs arbitrary precision** such as Python’s `Decimal` (money, controlled decimal rounding).

## Features

- **Home** — mission, float vs `Decimal` guidance, links to tools
- **Exact value** — `FP.from_float`, exact rational decimal, d-digit decimal strings that round to the same float
- **Segment / ULP** — unbiased exponent band, segment bounds, exact ULP as decimal

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
pytest test_app.py
```

or:

```bash
python -m unittest test_app.py -v
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
| `GET` / `POST /exact-decimal` | Exact value tool (form + JSON) |
| `GET` / `POST /segment` | Segment / ULP tool (form + JSON) |

## Architecture

- **Core logic**: `fp.py`, `fputil.py`
- **Web**: `app.py`, templates under `templates/`

API-style responses expose only what is needed for FP insight (e.g. `fp`, `bits`, `exact_decimal`, `unbiased_exp` where applicable; segment adds `min_val`, `max_val`, `distance`).
