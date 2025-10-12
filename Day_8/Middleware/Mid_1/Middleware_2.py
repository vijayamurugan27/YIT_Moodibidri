from flask import Flask, request

app = Flask(__name__)

class SimpleMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Code before the request reaches Flask
        print(f"Incoming Request: {environ['PATH_INFO']}")
        
        # Call the main Flask app
        response = self.app(environ, start_response)
        
        # Code after Flask handles the request
        print("Response sent successfully.")
        return response

import time

class TimingMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        start = time.time()
        response = self.app(environ, start_response)
        duration = time.time() - start
        print(f"⏱️ Request took {duration:.4f} seconds")
        return response

class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            headers.append(('X-Frame-Options', 'DENY'))
            headers.append(('X-Content-Type-Options', 'nosniff'))
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)
# You can stack multiple middlewares
app.wsgi_app = TimingMiddleware(app.wsgi_app) 
app.wsgi_app = SecurityHeadersMiddleware(app.wsgi_app)
app.wsgi_app = SimpleMiddleware(app.wsgi_app)


@app.route('/')
def index():
    return "Hello from Flask with Middleware!"

@app.route('/home')
def home():
    return "Welcome to the home page!"

@app.route('/profile')
def profile():
    return "This is your profile page."

@app.route('/products')
def products():
    return "Here are our products."

@app.route('/services')
def services():
    return "Our services include web development and consulting."

@app.route('/contact')
def contact():
    return "Contact us at Yenepoya."

@app.route('/about')
def about():
    return "This is the about page."



if __name__ == "__main__":
    app.run(debug=True)
