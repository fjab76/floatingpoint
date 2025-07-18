# Echo Web Application

A simple web application that demonstrates the client-server model. Users can enter their name through a web form, and the server returns a personalized greeting.

## Features

- Clean, responsive web interface
- Client-server architecture using Flask
- Form validation and error handling
- Real-time greeting display without page reload
- Modern styling with CSS

## Requirements

- Python 3.6 or higher
- Flask 3.0.0

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd floatingpoint
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running tests

1. Ensure you have `pytest` installed:
   ```bash
   pip install pytest
   ```

2. Run the tests:
   ```bash
   pytest tests/
   ```

3. Run the tests:
   ```bash
   python -m unittest test_app.py -v
   ```

## Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Enter your name in the text field and click "Get Greeting" to receive a personalized message.

## How it Works

1. **Client**: The web page (`templates/index.html`) contains a form with a text field for name input
2. **Server**: The Flask application (`app.py`) processes the form submission:
   - Validates the input
   - Composes a personalized greeting
   - Returns the greeting as JSON
3. **Display**: JavaScript updates the page to show the greeting without requiring a page reload

## Architecture

- **Frontend**: HTML5, CSS3, and JavaScript for the user interface
- **Backend**: Python Flask server handling requests and responses
- **Communication**: HTTP POST requests with JSON responses

## Screenshots

![Initial Form](https://github.com/user-attachments/assets/eaa10df1-b943-487e-ba34-fba4fadf1593)
*Initial form where users enter their name*

![Greeting Response](https://github.com/user-attachments/assets/c58ee7b1-3b09-4332-862f-05884e05548d)
*Personalized greeting displayed after form submission*