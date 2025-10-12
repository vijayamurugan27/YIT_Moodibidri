from flask import Flask
import time

app = Flask(__name__)

# ----------------------------------------------------------
# 1️⃣ Simple Middleware (Basic Logging Before and After Flask)
# ----------------------------------------------------------
class SimpleMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Before request reaches Flask
        print(f"📥 Incoming Request Path: {environ['PATH_INFO']}")

        # Pass control to next middleware / Flask app
        response = self.app(environ, start_response)

        # After Flask processes the request
        print("📤 Response sent successfully.")
        return response


# ----------------------------------------------------------
# 2️⃣ Timing Middleware (Measures Request Duration)
# ----------------------------------------------------------
class TimingMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        start = time.time()  # Start time

        # Inner function modifies the HTTP headers if needed
        def custom_start_response(status, headers, exc_info=None):
            duration = time.time() - start
            headers.append(("X-Response-Time", f"{duration:.4f}s"))
            print(f"⏱️ Request took {duration:.4f} seconds")
            return start_response(status, headers, exc_info)

        # Pass to the next layer
        return self.app(environ, custom_start_response)


# ----------------------------------------------------------
# 3️⃣ Security Headers Middleware (Adds Security Headers)
# ----------------------------------------------------------
class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            headers.append(("X-Frame-Options", "DENY"))
            headers.append(("X-Content-Type-Options", "nosniff"))
            headers.append(("X-XSS-Protection", "1; mode=block"))
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)


# ----------------------------------------------------------
# 4️⃣ Logging Middleware (Shows HTTP Method + Status)
# ----------------------------------------------------------
class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "")
        path = environ.get("PATH_INFO", "")
        print(f"📝 [LOG] {method} request for {path}")

        def custom_start_response(status, headers, exc_info=None):
            print(f"✅ [LOG] Response Status: {status}")
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)


# ----------------------------------------------------------
# 🔗 Chain the Middlewares (Order Matters!)
# ----------------------------------------------------------
# Flow: Logging → Simple → Timing → Security → Flask
app.wsgi_app = LoggingMiddleware(
    SimpleMiddleware(
        TimingMiddleware(
            SecurityHeadersMiddleware(app.wsgi_app)
        )
    )
)

# ----------------------------------------------------------
# 5️⃣ Flask Routes
# ----------------------------------------------------------
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
    time.sleep(0.5)  # simulate delay
    return "This is the about page."


# ----------------------------------------------------------
# Run Flask App
# ----------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
