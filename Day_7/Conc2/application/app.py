import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, abort

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app)
    
    return app

def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
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

def register_error_handlers(app):
    """Register all error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return render_error_page(400, "Bad Request - The request was invalid.")
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_error_page(403, "Forbidden - You don't have permission to access this resource.")
    
    @app.errorhandler(404)
    def not_found(error):
        return render_error_page(404, "Page Not Found - The requested URL was not found on the server.")
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_error_page(405, "Method Not Allowed - The method is not allowed for the requested URL.")
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return render_error_page(500, "Internal Server Error - Something went wrong on our end.")
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        # Log the error
        app.logger.error(f'Unhandled Exception: {str(error)}')
        
        # If in production mode, return generic error page
        if not app.debug:
            return render_error_page(500, "An unexpected error occurred.")
        
        # In debug mode, let the Flask debugger handle it
        raise error

def render_error_page(status_code, message):
    """Render appropriate error page based on request type"""
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        return jsonify({
            'error': {
                'code': status_code,
                'message': message
            }
        }), status_code
    
    return render_template(
        f'errors/{status_code}.html',
        error_code=status_code,
        error_message=message
    ), status_code

def register_routes(app):
    """Register application routes"""
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/trigger-error/<int:error_code>')
    def trigger_error(error_code):
        """Route to trigger specific errors for testing"""
        allowed_errors = [400, 403, 404, 405, 500]
        if error_code in allowed_errors:
            abort(error_code)
        return f"Error {error_code} triggered successfully"
    
    @app.route('/divide/<int:a>/<int:b>')
    def divide_numbers(a, b):
        """Route that might cause division by zero"""
        try:
            result = a / b
            return f"Result: {result}"
        except ZeroDivisionError:
            app.logger.error(f"Division by zero: {a} / {b}")
            abort(400, description="Cannot divide by zero")

# Create application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)



# import os
# import logging
# from logging.handlers import RotatingFileHandler
# from flask import Flask, render_template, request, jsonify, abort

# # Create Flask app instance at top level
# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'

# # Simple configuration
# if os.environ.get('FLASK_ENV') == 'development':
#     app.config['DEBUG'] = True
# else:
#     app.config['DEBUG'] = False

# # Setup basic logging
# if not app.debug:
#     if not os.path.exists('logs'):
#         os.mkdir('logs')
#     file_handler = RotatingFileHandler('logs/flask_app.log', maxBytes=10240, backupCount=10)
#     file_handler.setFormatter(logging.Formatter(
#         '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
#     ))
#     file_handler.setLevel(logging.INFO)
#     app.logger.addHandler(file_handler)
#     app.logger.setLevel(logging.INFO)
#     app.logger.info('Flask application startup')

# # Error Handlers
# @app.errorhandler(404)
# def not_found_error(error):
#     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
#         return jsonify({'error': 'Resource not found'}), 404
#     return render_template('errors/404.html'), 404

# @app.errorhandler(500)
# def internal_error(error):
#     app.logger.error(f'Server Error: {error}')
#     if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
#         return jsonify({'error': 'Internal server error'}), 500
#     return render_template('errors/500.html'), 500

# # Routes
# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/trigger-error/<int:error_code>')
# def trigger_error(error_code):
#     allowed_errors = [400, 403, 404, 405, 500]
#     if error_code in allowed_errors:
#         abort(error_code)
#     return f"Error {error_code} is not a testable error"

# # This ensures the app runs when executed directly
# if __name__ == '__main__':
#     app.run(debug=True)