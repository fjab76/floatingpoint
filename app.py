#!/usr/bin/env python3
"""
Simple Echo Web Application
A Flask-based web application that captures a user's name and returns a personalized greeting.
Follows the client-server model where the web page sends the name to the server,
which composes a greeting and returns it to be displayed.
"""

from flask import Flask, render_template, request, jsonify
import os
from fp import FP

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
    digits_input = request.form.get('digits', '').strip()
    
    # Validate input
    if not decimal_input:
        return jsonify({'error': 'Please enter a decimal number'}), 400
    
    if not digits_input:
        return jsonify({'error': 'Please enter the number of digits'}), 400
    
    try:
        # Convert to float and int
        float_value = float(decimal_input)
        digits_value = int(digits_input)
        
        # Validate digits range
        if digits_value < 1 or digits_value > 50:
            return jsonify({'error': 'Number of digits must be between 1 and 50'}), 400
        
        # Process with from_float function
        result = FP.from_float(float_value)
        
        # Get d-digit decimals
        d_digit_result = result.get_d_digit_decimals(digits_value)
        d_digit_count, d_digit_distance, d_digit_list = d_digit_result
        
        # Return all FP attributes plus d-digit decimals
        print(f"FP attributes for {decimal_input}: fp={result.fp}, bits={result.bits}, exact_decimal={result.exact_decimal}, unbiased_exp={result.unbiased_exp}")
        print(f"{digits_value}-digit decimals: count={d_digit_count}, distance={d_digit_distance}, list={d_digit_list}")
        return jsonify({
            'input': decimal_input,
            'digits': digits_value,
            'fp': result.fp,
            'bits': result.bits,
            'exact_decimal': str(result.exact_decimal),
            'unbiased_exp': result.unbiased_exp,
            'd_digit_count': d_digit_count,
            'd_digit_distance': str(d_digit_distance),
            'd_digit_list': [str(d) for d in d_digit_list]
        })
    except ValueError as e:
        error_msg = str(e)
        if 'could not convert string to float' in error_msg:
            return jsonify({'error': 'Invalid decimal number or number of digits. Please enter valid numbers.'}), 400
        elif 'invalid literal' in error_msg:
            return jsonify({'error': 'Invalid decimal number or number of digits. Please enter valid numbers.'}), 400
        return jsonify({'error': f'Error processing input: {error_msg}'}), 400

if __name__ == '__main__':
    # Run the application in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=8080)

