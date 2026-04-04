#!/usr/bin/env python3
"""Tests for the CLI module (cli.py)."""

import io
import sys
import unittest
from unittest.mock import patch


class TestCLIExactDecimal(unittest.TestCase):
    """Tests for the ``exact-decimal`` subcommand."""

    def _run(self, *argv: str) -> str:
        """Run the CLI with the given arguments and capture stdout."""
        with patch("sys.argv", ["fpctl"] + list(argv)):
            captured = io.StringIO()
            with patch("sys.stdout", captured):
                from cli import main  # pylint: disable=import-outside-toplevel
                main()
        return captured.getvalue()

    def test_exact_decimal_basic(self) -> None:
        output = self._run("exact-decimal", "0.1")
        self.assertIn("0.1000000000000000055511151231257827021181583404541015625", output)
        self.assertIn("Bits:", output)
        self.assertIn("Exact decimal:", output)
        self.assertIn("Unbiased exp:", output)

    def test_exact_decimal_shows_neighbors(self) -> None:
        output = self._run("exact-decimal", "1.0")
        self.assertIn("Lower neighbor:", output)
        self.assertIn("Upper neighbor:", output)

    def test_exact_decimal_with_digits(self) -> None:
        output = self._run("exact-decimal", "0.1", "--digits", "2")
        self.assertIn("2-digit decimals that map to this float:", output)
        self.assertIn("Count:", output)
        self.assertIn("Distance:", output)

    def test_exact_decimal_invalid_number(self) -> None:
        output = self._run("exact-decimal", "not-a-number")
        self.assertIn("Error:", output)


class TestCLISegment(unittest.TestCase):
    """Tests for the ``segment`` subcommand."""

    def _run(self, *argv: str) -> str:
        with patch("sys.argv", ["fpctl"] + list(argv)):
            captured = io.StringIO()
            with patch("sys.stdout", captured):
                from cli import main  # pylint: disable=import-outside-toplevel
                main()
        return captured.getvalue()

    def test_segment_one(self) -> None:
        output = self._run("segment", "1.0")
        self.assertIn("Segment min:    1", output)
        self.assertIn("Distance (ULP):", output)
        self.assertIn("Unbiased exp:   0", output)

    def test_segment_shows_min_max(self) -> None:
        output = self._run("segment", "1.0")
        self.assertIn("Segment min:", output)
        self.assertIn("Segment max:", output)

    def test_segment_invalid_number(self) -> None:
        output = self._run("segment", "abc")
        self.assertIn("Error:", output)

    def test_segment_infinity(self) -> None:
        output = self._run("segment", "inf")
        self.assertIn("Error:", output)


class TestCLIEnumerate(unittest.TestCase):
    """Tests for the ``enumerate`` subcommand."""

    def _run(self, *argv: str) -> str:
        with patch("sys.argv", ["fpctl"] + list(argv)):
            captured = io.StringIO()
            with patch("sys.stdout", captured):
                from cli import main  # pylint: disable=import-outside-toplevel
                main()
        return captured.getvalue()

    def test_enumerate_default_count(self) -> None:
        output = self._run("enumerate", "1.0")
        data_rows = [
            line for line in output.split("\n") if line.strip() and line[0].isdigit()
        ]
        self.assertEqual(len(data_rows), 10)

    def test_enumerate_custom_count(self) -> None:
        output = self._run("enumerate", "1.0", "--count", "3")
        data_rows = [
            line for line in output.split("\n") if line.strip() and line[0].isdigit()
        ]
        self.assertEqual(len(data_rows), 3)

    def test_enumerate_shows_exact_decimal(self) -> None:
        output = self._run("enumerate", "1.0", "--count", "1")
        self.assertIn("1", output)
        self.assertIn("Exact Decimal", output)

    def test_enumerate_invalid_number(self) -> None:
        output = self._run("enumerate", "xyz")
        self.assertIn("Error:", output)

    def test_enumerate_invalid_count(self) -> None:
        output = self._run("enumerate", "1.0", "--count", "0")
        self.assertIn("Error:", output)


if __name__ == "__main__":
    unittest.main()
