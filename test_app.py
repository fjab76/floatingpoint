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

    def test_floating_point_enumeration_page(self):
        """Test that the floating point enumeration page loads correctly"""
        response = self.app.get('/floating-point-enumeration')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Floating Point Enumeration', response.data)
        self.assertIn(b'Enter a decimal number (seed):', response.data)

    def test_floating_point_enumeration_with_valid_input(self):
        """Test floating point enumeration endpoint with valid input"""
        response = self.app.post('/floating-point-enumeration', data={'decimal': '1.0', 'count': '3'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('input', data)
        self.assertIn('count', data)
        self.assertIn('starting_fp', data)
        self.assertIn('starting_exact_decimal', data)
        self.assertIn('results', data)
        self.assertEqual(data['input'], '1.0')
        self.assertEqual(data['count'], 3)
        self.assertEqual(data['starting_fp'], 1.0)
        self.assertEqual(data['starting_exact_decimal'], '1')
        self.assertEqual(len(data['results']), 3)
        
        # Check first result
        first_result = data['results'][0]
        self.assertEqual(first_result['index'], 1)
        self.assertEqual(first_result['fp'], 1.0)
        self.assertEqual(first_result['exact_decimal'], '1')
        
        # Check second result (next floating point number)
        second_result = data['results'][1]
        self.assertEqual(second_result['index'], 2)
        self.assertEqual(second_result['fp'], 1.0000000000000002)
        self.assertEqual(second_result['exact_decimal'], '1.0000000000000002220446049250313080847263336181640625')

    def test_floating_point_enumeration_with_empty_decimal(self):
        """Test floating point enumeration endpoint with empty decimal input"""
        response = self.app.post('/floating-point-enumeration', data={'decimal': '', 'count': '5'})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Please enter a decimal number')

    def test_floating_point_enumeration_with_empty_count(self):
        """Test floating point enumeration endpoint with empty count"""
        response = self.app.post('/floating-point-enumeration', data={'decimal': '1.0', 'count': ''})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Please enter the number of consecutive floating point numbers')

    def test_floating_point_enumeration_with_invalid_count(self):
        """Test floating point enumeration endpoint with invalid count range"""
        response = self.app.post('/floating-point-enumeration', data={'decimal': '1.0', 'count': '150'})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Number of consecutive floating point numbers must be between 1 and 100')

    def test_floating_point_enumeration_with_invalid_decimal(self):
        """Test floating point enumeration endpoint with invalid decimal input"""
        response = self.app.post('/floating-point-enumeration', data={'decimal': 'not a number', 'count': '5'})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid decimal number or count. Please enter valid numbers.')

    def test_floating_point_enumeration_with_different_seed(self):
        """Test floating point enumeration endpoint with different seed value"""
        response = self.app.post('/floating-point-enumeration', data={'decimal': '0.1', 'count': '2'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['input'], '0.1')
        self.assertEqual(data['count'], 2)
        self.assertEqual(data['starting_fp'], 0.1)
        self.assertEqual(len(data['results']), 2)
        
        # Check that results are consecutive floating point numbers
        first_result = data['results'][0]
        second_result = data['results'][1]
        self.assertEqual(first_result['index'], 1)
        self.assertEqual(second_result['index'], 2)
        self.assertEqual(first_result['fp'], 0.1)
        # The next floating point number after 0.1
        self.assertNotEqual(first_result['fp'], second_result['fp'])

if __name__ == '__main__':
    unittest.main()