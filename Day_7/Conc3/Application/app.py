# app.py
"""
Complete Flask Application for Error Handling and Debugging
This application demonstrates:
- Flask debugger usage
- Custom error pages
- Different error types
- Effective debugging techniques
- User-friendly error handling
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, g
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Initialize Sentry (optional - comment out if not using)
# sentry_sdk.init(
#     dsn="your-sentry-dsn-here",
#     integrations=[FlaskIntegration()],
#     traces_sample_rate=1.0,
#     debug=True  # Set to False in production
# )

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class AuthenticationError(Exception):
    """Custom authentication error"""
    def __init__(self, message="Unauthorized access", status_code=401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-for-teaching')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app)
    
    return app

def setup_logging(app):
    """Configure logging for the application"""
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/flask_error_demo.log', 
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Flask Error Handling Demo startup')
    else:
        # Development logging
        app.logger.setLevel(logging.DEBUG)

def register_error_handlers(app):
    """Register all error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'404 error: {request.url}')
        if request.is_json:
            return jsonify({
                'error': 'The requested resource was not found',
                'status_code': 404
            }), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'403 error: {request.url} - User: {getattr(g, "user_id", "anonymous")}')
        if request.is_json:
            return jsonify({
                'error': 'Access forbidden',
                'status_code': 403
            }), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f'400 error: {request.url} - {str(error)}')
        if request.is_json:
            return jsonify({
                'error': 'Bad request - invalid data',
                'status_code': 400
            }), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'500 error: {str(error)} on {request.url}')
        if request.is_json:
            return jsonify({
                'error': 'Internal server error - we are working to fix this',
                'status_code': 500
            }), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        app.logger.warning(f'Validation error: {error.message}')
        if request.is_json:
            return jsonify({
                'error': error.message,
                'status_code': error.status_code
            }), error.status_code
        return render_template('errors/validation.html', error=error.message), error.status_code

    @app.errorhandler(AuthenticationError)
    def handle_auth_error(error):
        app.logger.warning(f'Authentication error: {error.message}')
        if request.is_json:
            return jsonify({
                'error': error.message,
                'status_code': error.status_code
            }), error.status_code
        return render_template('errors/auth.html', error=error.message), error.status_code

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the exception with context
        app.logger.error(
            f'Unhandled exception on {request.path} [{request.method}]: {str(e)}',
            extra={
                'user_id': getattr(g, 'user_id', 'anonymous'),
                'ip_address': request.remote_addr,
                'user_agent': request.user_agent.string
            }
        )
        if request.is_json:
            return jsonify({
                'error': 'An unexpected error occurred',
                'status_code': 500
            }), 500
        return render_template('errors/500.html'), 500

def register_routes(app):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/debug')
    def debug_route():
        """Route to demonstrate Flask debugger"""
        # This will trigger the interactive debugger when debug=True
        user_id = request.args.get('user_id')
        if user_id is None:
            raise ValueError("User ID parameter is required for debugging")
        return f"Debug route working! User ID: {user_id}"
    
    @app.route('/breakpoint')
    def breakpoint_route():
        """Route to demonstrate pdb debugging"""
        user_id = request.args.get('user_id', 'default')
        
        # Uncomment the next line to set a breakpoint
        # import pdb; pdb.set_trace()
        
        # Simulate some processing
        processed_data = f"Processed user: {user_id}"
        return jsonify({'data': processed_data})
    
    @app.route('/error/<int:error_code>')
    def trigger_error(error_code):
        """Route to trigger specific HTTP errors for testing"""
        if error_code == 404:
            return render_template('non-existent-template.html')
        elif error_code == 403:
            raise AuthenticationError("You don't have permission to access this resource")
        elif error_code == 400:
            raise ValidationError("Invalid request data provided")
        elif error_code == 500:
            # This will trigger a 500 error
            undefined_variable  # This will cause a NameError
        else:
            return f"Error code {error_code} not implemented", 400
    
    @app.route('/api/users', methods=['POST'])
    def create_user():
        """API route demonstrating custom error handling"""
        try:
            data = request.get_json()
            
            # Validate input
            if not data:
                raise ValidationError('No JSON data provided')
            
            if 'email' not in data:
                raise ValidationError('Email field is required')
            
            if 'name' not in data:
                raise ValidationError('Name field is required')
            
            if '@' not in data['email']:
                raise ValidationError('Invalid email format')
            
            # Simulate user creation
            user = {
                'id': 123,
                'name': data['name'],
                'email': data['email']
            }
            
            app.logger.info(f'User created successfully: {user["email"]}')
            return jsonify({'user': user, 'message': 'User created successfully'}), 201
            
        except ValidationError as e:
            # This will be handled by the custom error handler
            raise e
        except Exception as e:
            app.logger.error(f'Unexpected error in create_user: {str(e)}')
            raise  # This will be caught by the generic exception handler
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for production monitoring"""
        try:
            # Simulate database check
            # In real app: db.session.execute('SELECT 1')
            return jsonify({
                'status': 'healthy',
                'version': '1.0.0',
                'environment': 'development' if app.debug else 'production'
            }), 200
        except Exception as e:
            app.logger.error(f'Health check failed: {str(e)}')
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500
    
    @app.route('/simulate-crash')
    def simulate_crash():
        """Route to simulate a crash for testing error handlers"""
        import random
        crash_type = random.choice(['division', 'key', 'attribute', 'index'])
        
        if crash_type == 'division':
            result = 1 / 0
        elif crash_type == 'key':
            my_dict = {}
            value = my_dict['nonexistent']
        elif crash_type == 'attribute':
            my_obj = None
            value = my_obj.some_attribute
        elif crash_type == 'index':
            my_list = [1, 2, 3]
            value = my_list[10]
        
        return "This should not be reached"

if __name__ == '__main__':
    app = create_app()
    
    # Print startup information
    print(f"Flask Error Handling Demo")
    print(f"Debug mode: {app.debug}")
    print(f"Access the following URLs to test error handling:")
    print(f"  http://localhost:5000/ - Home page")
    print(f"  http://localhost:5000/debug?user_id=123 - Debug route")
    print(f"  http://localhost:5000/error/404 - Test 404 error")
    print(f"  http://localhost:5000/error/403 - Test 403 error")
    print(f"  http://localhost:5000/error/400 - Test 400 error")
    print(f"  http://localhost:5000/error/500 - Test 500 error")
    print(f"  http://localhost:5000/simulate-crash - Simulate random crash")
    print(f"  http://localhost:5000/health - Health check")
    print(f"")
    print(f"API Testing:")
    print(f"  POST http://localhost:5000/api/users - Create user (send JSON with name and email)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)