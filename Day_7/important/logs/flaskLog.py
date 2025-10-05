from flask import Flask, request, g, jsonify
import logging
from logging.handlers import RotatingFileHandler
import os
import time
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'path': getattr(record, 'path', ''),
            'method': getattr(record, 'method', ''),
            'remote_addr': getattr(record, 'remote_addr', ''),
            'user_id': getattr(record, 'user_id', 'anonymous')
        }
        return json.dumps(log_entry)

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/app.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(JSONFormatter())
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
    
    # Request logging
    @app.before_request
    def log_request():
        g.start_time = time.time()
        app.logger.info("Request received", extra={
            'path': request.path,
            'method': request.method,
            'remote_addr': request.remote_addr
        })
    
    @app.after_request
    def log_response(response):
        duration = time.time() - g.start_time
        app.logger.info(f"Response sent - {response.status_code} ({duration:.2f}s)")
        return response
    
    # Routes
    @app.route('/')
    def home():
        app.logger.info("Home page accessed")
        return jsonify({"message": "Hello, World!"})
    
    @app.route('/error')
    def error():
        app.logger.error("Simulated error occurred")
        raise Exception("Something went wrong!")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)