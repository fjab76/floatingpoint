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

if __name__ == '__main__':
    unittest.main()