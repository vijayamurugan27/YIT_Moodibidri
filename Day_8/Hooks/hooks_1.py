from flask import Flask, request

app = Flask(__name__)

@app.before_request
def before_request_func():
    print(f"➡️ Before handling request to: {request.path}")

@app.after_request
def after_request_func(response):
    print(f"⬅️ After handling request: {response.status}")
    return response

@app.teardown_request
def teardown_request_func(error=None):
    print("🧹 Cleaning up resources after request.")

@app.route('/')
def home():
    return "Request hooks example"

if __name__ == "__main__":
    app.run(debug=True)
