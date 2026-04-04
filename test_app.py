#!/usr/bin/env python3
"""Tests for the Floatingpoint Flask application."""

import json
import unittest

from app import app


class FloatingpointAppTestCase(unittest.TestCase):
    """Integration tests for routes and JSON APIs."""

    def setUp(self) -> None:
        self.client = app.test_client()
        self.client.testing = True

    def test_index_page(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Floatingpoint", response.data)
        self.assertIn(b"IEEE-754", response.data)

    def test_exact_decimal_page(self) -> None:
        response = self.client.get("/exact-decimal")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Exact value", response.data)
        self.assertIn(b"Representable floats are isolated points", response.data)
        self.assertIn(b"regular lattice", response.data)

    def test_exact_decimal_with_valid_number(self) -> None:
        response = self.client.post("/exact-decimal", data={"decimal": "0.1", "digits": "5"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["input"], "0.1")
        self.assertEqual(data["digits"], 5)
        self.assertEqual(data["fp"], 0.1)
        self.assertEqual(
            data["bits"],
            "0011111110111001100110011001100110011001100110011001100110011010",
        )
        self.assertEqual(
            data["exact_decimal"],
            "0.1000000000000000055511151231257827021181583404541015625",
        )
        self.assertEqual(data["unbiased_exp"], -4)
        self.assertIn("d_digit_count", data)
        self.assertIn("d_digit_distance", data)
        self.assertIn("d_digit_list", data)
        self.assertIn("neighbor_lower", data)
        self.assertIn("neighbor_higher", data)
        self.assertLess(data["neighbor_lower"], data["fp"])
        self.assertLess(data["fp"], data["neighbor_higher"])

    def test_exact_decimal_with_empty_input(self) -> None:
        response = self.client.post("/exact-decimal", data={"decimal": "", "digits": "5"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_segment_page(self) -> None:
        response = self.client.get("/segment")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Segment", response.data)
        self.assertIn(b"ULP", response.data)

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
        self.assertEqual(data["num_floats"], 2 ** 52)

    def test_segment_float_index_nonzero(self) -> None:
        # 4503599627370497.0 is the second float in the e=52 segment (index 1)
        response = self.client.post("/segment", data={"decimal": "4503599627370497"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["float_index"], 1)
        self.assertEqual(data["length"], "4503599627370495")

    def test_segment_non_finite(self) -> None:
        response = self.client.post("/segment", data={"decimal": "inf"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_segment_empty(self) -> None:
        response = self.client.post("/segment", data={"decimal": ""})
        self.assertEqual(response.status_code, 400)

    def test_notes_page(self) -> None:
        response = self.client.get("/notes")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"notes-content", response.data)

    def test_notes_content(self) -> None:
        response = self.client.get("/notes/content")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.content_type)
        self.assertIn(b"Floating-point numbers", response.data)


if __name__ == "__main__":
    unittest.main()
