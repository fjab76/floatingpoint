#!/usr/bin/env python3
"""
Simple Echo Web Application
A Flask-based web application that captures a user's name and returns a personalized greeting.
Follows the client-server model where the web page sends the name to the server,
which composes a greeting and returns it to be displayed.
"""

from flask import Flask, render_template, request, jsonify
import os

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

if __name__ == '__main__':
    # Run the application in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5000)