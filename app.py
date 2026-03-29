#!/usr/bin/env python3
"""
Flask web application for exploring IEEE-754 double-precision floating-point behavior.
"""

import math
from decimal import ROUND_HALF_UP, Context

from flask import Flask, jsonify, render_template, request

from fp import FP, Segment

app = Flask(__name__)

_SEGMENT_CTX = Context(prec=400, rounding=ROUND_HALF_UP)


@app.route("/")
def index():
    """Serve the home page with mission and links to tools."""
    return render_template("index.html", nav_active="home")


@app.route("/exact-decimal")
def exact_decimal_form():
    """Serve the exact decimal form page."""
    return render_template("exact_decimal.html", nav_active="exact_decimal")


@app.route("/exact-decimal", methods=["POST"])
def exact_decimal_process():
    """Process the decimal input and return exact decimal representation."""
    decimal_input = request.form.get("decimal", "").strip()
    digits_input = request.form.get("digits", "").strip()

    if not decimal_input:
        return jsonify({"error": "Please enter a decimal number"}), 400

    if not digits_input:
        return jsonify({"error": "Please enter the number of digits"}), 400

    try:
        float_value = float(decimal_input)
        digits_value = int(digits_input)

        if digits_value < 1 or digits_value > 50:
            return jsonify({"error": "Number of digits must be between 1 and 50"}), 400

        result = FP.from_float(float_value)
        d_digit_result = result.get_d_digit_decimals(digits_value)
        d_digit_count, d_digit_distance, d_digit_list = d_digit_result

        return jsonify({
            "input": decimal_input,
            "digits": digits_value,
            "fp": result.fp,
            "bits": result.bits,
            "exact_decimal": str(result.exact_decimal),
            "unbiased_exp": result.unbiased_exp,
            "d_digit_count": d_digit_count,
            "d_digit_distance": str(d_digit_distance),
            "d_digit_list": [str(d) for d in d_digit_list],
        })
    except ValueError as exc:
        error_msg = str(exc)
        if "could not convert string to float" in error_msg:
            return jsonify({
                "error": "Invalid decimal number or number of digits. Please enter valid numbers.",
            }), 400
        if "invalid literal" in error_msg:
            return jsonify({
                "error": "Invalid decimal number or number of digits. Please enter valid numbers.",
            }), 400
        return jsonify({"error": f"Error processing input: {error_msg}"}), 400


@app.route("/segment")
def segment_form():
    """Serve the segment / ULP explorer page."""
    return render_template("segment.html", nav_active="segment")


@app.route("/segment", methods=["POST"])
def segment_process():
    """Return binade bounds and ULP (distance) for the float parsed from user input."""
    decimal_input = request.form.get("decimal", "").strip()

    if not decimal_input:
        return jsonify({"error": "Please enter a number"}), 400

    try:
        float_value = float(decimal_input)
    except ValueError:
        return jsonify({"error": "Invalid number. Please enter a valid floating-point literal."}), 400

    if not math.isfinite(float_value):
        return jsonify({"error": "Please enter a finite number (not infinity or NaN)."}), 400

    try:
        seg = Segment.from_fp(float_value, _SEGMENT_CTX)
    except OverflowError:
        return jsonify({"error": "Cannot compute segment for this value."}), 400

    fp_obj = FP.from_float(float_value)
    return jsonify({
        "input": decimal_input,
        "fp": fp_obj.fp,
        "unbiased_exp": seg.unbiased_exp,
        "min_val": str(seg.min_val),
        "max_val": str(seg.max_val),
        "distance": str(seg.distance),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
