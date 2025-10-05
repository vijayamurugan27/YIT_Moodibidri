from flask import Flask, render_template_string, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import traceback
from werkzeug.exceptions import HTTPException
import os

app = Flask(__name__)

# ============================================
# 1. FLASK DEBUGGER CONFIGURATION
# ============================================

# Enable debug mode (NEVER use in production!)
app.config['DEBUG'] = True  # Set to False in production

# Secret key for sessions
app.config['SECRET_KEY'] = 'your-secret-key-here'

# ============================================
# 2. LOGGING SETUP
# ============================================

def setup_logging():
    """Configure application logging"""
    if not app.debug:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler for errors
        file_handler = RotatingFileHandler(
            'logs/flask_app.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Flask application startup')

setup_logging()

# ============================================
# 3. CUSTOM ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    app.logger.warning(f'404 error: {request.url}')
    
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        # Return JSON for API requests
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status': 404
        }), 404
    
    # Return HTML for browser requests
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>404 - Page Not Found</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .error-container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }
                h1 {
                    font-size: 72px;
                    margin: 0;
                    color: #667eea;
                }
                h2 {
                    color: #333;
                    margin: 10px 0;
                }
                p {
                    color: #666;
                    line-height: 1.6;
                }
                a {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background 0.3s;
                }
                a:hover {
                    background: #764ba2;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>404</h1>
                <h2>Page Not Found</h2>
                <p>Sorry, the page you're looking for doesn't exist.</p>
                <a href="/">Go Home</a>
            </div>
        </body>
        </html>
    '''), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f'Server Error: {error}')
    app.logger.error(traceback.format_exc())
    
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status': 500
        }), 500
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>500 - Server Error</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .error-container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }
                h1 {
                    font-size: 72px;
                    margin: 0;
                    color: #f5576c;
                }
                h2 {
                    color: #333;
                    margin: 10px 0;
                }
                p {
                    color: #666;
                    line-height: 1.6;
                }
                a {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 30px;
                    background: #f5576c;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background 0.3s;
                }
                a:hover {
                    background: #f093fb;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>500</h1>
                <h2>Internal Server Error</h2>
                <p>Oops! Something went wrong on our end. We're working on it!</p>
                <a href="/">Go Home</a>
            </div>
        </body>
        </html>
    '''), 500

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 Forbidden errors"""
    app.logger.warning(f'403 error: {request.url}')
    
    if request.accept_mimetypes.accept_json:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status': 403
        }), 403
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>403 - Forbidden</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .error-container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }
                h1 {
                    font-size: 72px;
                    margin: 0;
                    color: #fa709a;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>403</h1>
                <h2>Access Forbidden</h2>
                <p>You don't have permission to access this resource.</p>
                <a href="/">Go Home</a>
            </div>
        </body>
        </html>
    '''), 403

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions"""
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        return e
    
    # Log the exception
    app.logger.error(f'Unhandled Exception: {e}')
    app.logger.error(traceback.format_exc())
    
    # Return 500 error
    return internal_error(e)

# ============================================
# 4. CUSTOM ERROR CLASSES
# ============================================

class ValidationError(Exception):
    """Custom exception for validation errors"""
    status_code = 400
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status_code
        return rv

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle custom validation errors"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# ============================================
# 5. DEMO ROUTES
# ============================================

@app.route('/')
def home():
    """Home page with error testing links"""
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flask Error Handling Demo</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                h1 {
                    color: #333;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                }
                .link-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-top: 30px;
                }
                a {
                    display: block;
                    padding: 20px;
                    background: white;
                    color: #667eea;
                    text-decoration: none;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    text-align: center;
                    transition: transform 0.3s, box-shadow 0.3s;
                }
                a:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                .warning {
                    background: #fff3cd;
                    border: 1px solid #ffc107;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <h1>Flask Error Handling & Debugging Demo</h1>
            <p>Click the links below to test different error scenarios:</p>
            
            <div class="link-grid">
                <a href="/404-test">Test 404 Error</a>
                <a href="/500-test">Test 500 Error</a>
                <a href="/403-test">Test 403 Error</a>
                <a href="/validation-test">Test Validation Error</a>
                <a href="/api/error">Test API Error (JSON)</a>
                <a href="/log-test">Test Logging</a>
            </div>
            
            <div class="warning">
                <strong>⚠️ Debug Mode:</strong> Debug mode is currently 
                {{ 'ENABLED' if debug else 'DISABLED' }}. 
                Never enable debug mode in production!
            </div>
        </body>
        </html>
    ''', debug=app.debug)

@app.route('/500-test')
def test_500():
    """Trigger a 500 error"""
    # Intentionally cause an error
    result = 1 / 0
    return result

@app.route('/403-test')
def test_403():
    """Trigger a 403 error"""
    from flask import abort
    abort(403)

@app.route('/validation-test')
def test_validation():
    """Trigger a custom validation error"""
    raise ValidationError('Invalid data provided', payload={'field': 'email'})

@app.route('/api/error')
def test_api_error():
    """Test error handling for API endpoints"""
    # This will return JSON error format
    from flask import abort
    abort(404)

@app.route('/log-test')
def test_logging():
    """Test different logging levels"""
    app.logger.debug('This is a debug message')
    app.logger.info('This is an info message')
    app.logger.warning('This is a warning message')
    app.logger.error('This is an error message')
    
    return jsonify({
        'message': 'Logging test complete. Check console or logs/flask_app.log',
        'status': 'success'
    })

# ============================================
# 6. DEBUGGING TIPS
# ============================================

"""
DEBUGGING BEST PRACTICES:

1. Development vs Production:
   - Use DEBUG=True only in development
   - Never expose debug mode in production
   - Use environment variables: app.config['DEBUG'] = os.getenv('FLASK_DEBUG', False)

2. Flask Debugger Features:
   - Interactive debugger in browser (when DEBUG=True)
   - Automatic reloader on code changes
   - Detailed error pages with stack traces
   
3. Logging Strategies:
   - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Log to files in production
   - Include context (user ID, request ID, etc.)
   
4. Error Handling Patterns:
   - Create custom error pages for better UX
   - Return JSON for API endpoints
   - Log all errors for monitoring
   
5. Common Error Types:
   - 400: Bad Request (client error)
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not Found
   - 500: Internal Server Error
   - 503: Service Unavailable

6. Testing Errors:
   - Test error handlers with pytest
   - Use Flask's test client
   - Mock external dependencies

7. Production Monitoring:
   - Use services like Sentry for error tracking
   - Set up alerts for critical errors
   - Monitor log files regularly
"""

if __name__ == '__main__':
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)