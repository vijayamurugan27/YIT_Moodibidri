from flask import Flask, request

import time
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

@app.route('/contactus')
def contact():
    return "Contact us at Yenepoya."

@app.route('/aboutus')
def about():
    time.sleep(0.5)  # simulate delay
    return "This is the about page."



if __name__ == "__main__":
    app.run(debug=True)
