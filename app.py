#!/usr/bin/env python3
"""
Simple Echo Web Application
A Flask-based web application that captures a user's name and returns a personalized greeting.
Follows the client-server model where the web page sends the name to the server,
which composes a greeting and returns it to be displayed.
"""

from flask import Flask, render_template, request, jsonify
import os
from fp import from_float

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main page with the name input form."""
    return render_template('index.html')

@app.route('/echo', methods=['POST'])
def echo():
    """Process the name input and return a personalized greeting."""
    # Get the name from the form data
    name = request.form.get('name', '').strip()
    
    # Validate input
    if not name:
        return jsonify({'error': 'Please enter your name'}), 400
    
    # Compose the greeting
    greeting = f"Hello, {name}! Welcome to our echo application."
    
    # Return the greeting as JSON
    return jsonify({'greeting': greeting})

@app.route('/exact-decimal')
def exact_decimal_form():
    """Serve the exact decimal form page."""
    return render_template('exact_decimal.html')

@app.route('/exact-decimal', methods=['POST'])
def exact_decimal_process():
    """Process the decimal input and return exact decimal representation."""
    # Get the decimal value from the form data
    decimal_input = request.form.get('decimal', '').strip()
    
    # Validate input
    if not decimal_input:
        return jsonify({'error': 'Please enter a decimal number'}), 400
    
    try:
        # Convert to float
        float_value = float(decimal_input)
        
        # Process with from_float function
        result = from_float(float_value)
        
        # Return the exact decimal representation
        return jsonify({
            'input': decimal_input,
            'exact_decimal': result.exact_decimal
        })
    except ValueError:
        return jsonify({'error': 'Invalid decimal number. Please enter a valid number.'}), 400

if __name__ == '__main__':
    # Run the application in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5000)