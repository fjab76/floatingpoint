#!/usr/bin/env python3
"""Command-line interface for exploring IEEE-754 double-precision floating-point behavior."""

import argparse
import math
from decimal import ROUND_HALF_UP, Context

from fp import FP, Segment, next_n_binary_fp

_SEGMENT_CTX = Context(prec=400, rounding=ROUND_HALF_UP)


def cmd_exact_decimal(args: argparse.Namespace) -> None:
    """Handle the exact-decimal subcommand.

    Prints the exact decimal representation, binary bits, unbiased exponent,
    and neighboring floats for the given number.  If ``--digits`` is supplied
    the d-digit decimals that round to the same float are also listed.
    """
    try:
        float_value = float(args.number)
    except ValueError:
        print(f"Error: '{args.number}' is not a valid floating-point number.")
        return

    fp_obj = FP.from_float(float_value)
    print(f"Input:         {args.number}")
    print(f"Float:         {fp_obj.fp}")
    print(f"Bits:          {fp_obj.bits}")
    print(f"Exact decimal: {fp_obj.exact_decimal}")
    print(f"Unbiased exp:  {fp_obj.unbiased_exp}")

    if math.isfinite(float_value):
        print(f"Lower neighbor: {math.nextafter(float_value, -math.inf)}")
        print(f"Upper neighbor: {math.nextafter(float_value, math.inf)}")

    if args.digits is not None:
        try:
            count, distance, decimals = fp_obj.get_d_digit_decimals(args.digits)
            print(f"\n{args.digits}-digit decimals that map to this float:")
            print(f"  Count:    {count}")
            print(f"  Distance: {distance}")
            for d in decimals:
                print(f"  {d}")
        except ValueError as exc:
            print(f"Error computing {args.digits}-digit decimals: {exc}")


def cmd_segment(args: argparse.Namespace) -> None:
    """Handle the segment subcommand.

    Prints the binade bounds (min/max) and the ULP distance for the segment
    containing the given floating-point number.
    """
    try:
        float_value = float(args.number)
    except ValueError:
        print(f"Error: '{args.number}' is not a valid floating-point number.")
        return

    if not math.isfinite(float_value):
        print("Error: Please provide a finite number (not infinity or NaN).")
        return

    try:
        seg = Segment.from_fp(float_value, _SEGMENT_CTX)
    except OverflowError:
        print("Error: Cannot compute segment for this value.")
        return

    fp_obj = FP.from_float(float_value)
    print(f"Input:          {args.number}")
    print(f"Float:          {fp_obj.fp}")
    print(f"Unbiased exp:   {seg.unbiased_exp}")
    print(f"Segment min:    {seg.min_val}")
    print(f"Segment max:    {seg.max_val}")
    print(f"Distance (ULP): {seg.distance}")


def cmd_enumerate(args: argparse.Namespace) -> None:
    """Handle the enumerate subcommand.

    Lists *count* consecutive double-precision floating-point numbers in
    ascending order, starting from the given seed value.
    """
    try:
        float_value = float(args.number)
    except ValueError:
        print(f"Error: '{args.number}' is not a valid floating-point number.")
        return

    if args.count < 1:
        print("Error: --count must be a positive integer.")
        return

    fp_obj = FP.from_float(float_value)
    fps = next_n_binary_fp(fp_obj, args.count)

    col_float = max(len(str(fp.fp)) for fp in fps)
    header = f"{'#':<5}  {'Float':<{col_float}}  Exact Decimal"
    print(header)
    print("-" * len(header))
    for i, fp in enumerate(fps, start=1):
        print(f"{i:<5}  {str(fp.fp):<{col_float}}  {fp.exact_decimal}")


def main() -> None:
    """Entry point for the floating-point CLI."""
    parser = argparse.ArgumentParser(
        prog="fpctl",
        description="Explore IEEE-754 double-precision floating-point behavior.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- exact-decimal subcommand ---
    exact_parser = subparsers.add_parser(
        "exact-decimal",
        help="Show the exact decimal representation of a floating-point number.",
    )
    exact_parser.add_argument("number", help="Decimal number to analyze.")
    exact_parser.add_argument(
        "--digits",
        type=int,
        metavar="D",
        help="Also list all D-digit decimal numbers that map to this float.",
    )
    exact_parser.set_defaults(func=cmd_exact_decimal)

    # --- segment subcommand ---
    seg_parser = subparsers.add_parser(
        "segment",
        help="Show the binade/segment and ULP distance for a floating-point number.",
    )
    seg_parser.add_argument("number", help="Decimal number to analyze.")
    seg_parser.set_defaults(func=cmd_segment)

    # --- enumerate subcommand ---
    enum_parser = subparsers.add_parser(
        "enumerate",
        help="List consecutive floating-point numbers starting from a given value.",
    )
    enum_parser.add_argument("number", help="Seed decimal number.")
    enum_parser.add_argument(
        "--count",
        type=int,
        default=10,
        metavar="N",
        help="Number of consecutive floating-point numbers to list (default: 10).",
    )
    enum_parser.set_defaults(func=cmd_enumerate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
