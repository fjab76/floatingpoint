#!/usr/bin/env python3
"""
Basic tests for the Echo Web Application
"""

import unittest
import json
from app import app

class EchoAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True

    def test_index_page(self):
        """Test that the index page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Echo Web Application', response.data)
        self.assertIn(b'Your Name:', response.data)

    def test_echo_with_valid_name(self):
        """Test echo endpoint with valid name"""
        response = self.app.post('/echo', data={'name': 'John'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('greeting', data)
        self.assertEqual(data['greeting'], 'Hello, John! Welcome to our echo application.')

    def test_echo_with_empty_name(self):
        """Test echo endpoint with empty name"""
        response = self.app.post('/echo', data={'name': ''})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Please enter your name')

    def test_echo_with_whitespace_name(self):
        """Test echo endpoint with whitespace-only name"""
        response = self.app.post('/echo', data={'name': '   '})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Please enter your name')

    def test_echo_with_special_characters(self):
        """Test echo endpoint with special characters in name"""
        response = self.app.post('/echo', data={'name': 'José María'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('greeting', data)
        self.assertEqual(data['greeting'], 'Hello, José María! Welcome to our echo application.')

    def test_exact_decimal_page(self):
        """Test that the exact decimal page loads correctly"""
        response = self.app.get('/exact-decimal')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Exact Decimal Converter', response.data)
        self.assertIn(b'Enter a decimal number:', response.data)

    def test_exact_decimal_with_valid_number(self):
        """Test exact decimal endpoint with valid number"""
        response = self.app.post('/exact-decimal', data={'decimal': '0.1', 'digits': '5'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('input', data)
        self.assertIn('digits', data)
        self.assertIn('fp', data)
        self.assertIn('bits', data)
        self.assertIn('exact_decimal', data)
        self.assertIn('unbiased_exp', data)
        self.assertIn('d_digit_count', data)
        self.assertIn('d_digit_distance', data)
        self.assertIn('d_digit_list', data)
        self.assertEqual(data['input'], '0.1')
        self.assertEqual(data['digits'], 5)
        self.assertEqual(data['fp'], 0.1)
        self.assertEqual(data['bits'], '0011111110111001100110011001100110011001100110011001100110011010')
        self.assertEqual(data['exact_decimal'], '0.1000000000000000055511151231257827021181583404541015625')
        self.assertEqual(data['unbiased_exp'], -4)

    def test_exact_decimal_with_precision_issue(self):
        """Test exact decimal endpoint with a number that has precision issues"""
        # 0.1 + 0.2 = 0.30000000000000004 in floating point
        response = self.app.post('/exact-decimal', data={'decimal': '0.30000000000000004', 'digits': '3'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('input', data)
        self.assertIn('digits', data)
        self.assertIn('fp', data)
        self.assertIn('bits', data)
        self.assertIn('exact_decimal', data)
        self.assertIn('unbiased_exp', data)
        self.assertIn('d_digit_count', data)
        self.assertIn('d_digit_distance', data)
        self.assertIn('d_digit_list', data)
        self.assertEqual(data['input'], '0.30000000000000004')
        self.assertEqual(data['digits'], 3)
        self.assertEqual(data['fp'], 0.30000000000000004)
        self.assertEqual(data['bits'], '0011111111010011001100110011001100110011001100110011001100110100')
        self.assertEqual(data['exact_decimal'], '0.3000000000000000444089209850062616169452667236328125')
        self.assertEqual(data['unbiased_exp'], -2)

    def test_exact_decimal_with_empty_input(self):
        """Test exact decimal endpoint with empty input"""
        response = self.app.post('/exact-decimal', data={'decimal': '', 'digits': '5'})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Please enter a decimal number')

    def test_exact_decimal_with_empty_digits(self):
        """Test exact decimal endpoint with empty digits"""
        response = self.app.post('/exact-decimal', data={'decimal': '0.1', 'digits': ''})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Please enter the number of digits')

    def test_exact_decimal_with_invalid_digits(self):
        """Test exact decimal endpoint with invalid digits range"""
        response = self.app.post('/exact-decimal', data={'decimal': '0.1', 'digits': '100'})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Number of digits must be between 1 and 50')

    def test_exact_decimal_with_invalid_input(self):
        """Test exact decimal endpoint with invalid input"""
        response = self.app.post('/exact-decimal', data={'decimal': 'not a number', 'digits': '5'})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid decimal number or number of digits. Please enter valid numbers.')

    def test_exact_decimal_with_integer(self):
        """Test exact decimal endpoint with integer input"""
        response = self.app.post('/exact-decimal', data={'decimal': '5', 'digits': '1'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('input', data)
        self.assertIn('digits', data)
        self.assertIn('fp', data)
        self.assertIn('bits', data)
        self.assertIn('exact_decimal', data)
        self.assertIn('unbiased_exp', data)
        self.assertIn('d_digit_count', data)
        self.assertIn('d_digit_distance', data)
        self.assertIn('d_digit_list', data)
        self.assertEqual(data['input'], '5')
        self.assertEqual(data['digits'], 1)
        self.assertEqual(data['fp'], 5.0)
        self.assertIn('fp', data)
        self.assertIn('bits', data)
        self.assertIn('exact_decimal', data)
        self.assertIn('unbiased_exp', data)
        self.assertEqual(data['input'], '5')
        self.assertEqual(data['fp'], 5.0)
        self.assertEqual(data['bits'], '0100000000010100000000000000000000000000000000000000000000000000')
        self.assertEqual(data['exact_decimal'], '5')
        self.assertEqual(data['unbiased_exp'], 2)

if __name__ == '__main__':
    unittest.main()