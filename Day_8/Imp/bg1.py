from flask import Flask, jsonify
import threading, time

app = Flask(__name__)

def background_task(name):
    print(f"⏳ Background task {name} started...")
    time.sleep(5)
    print(f"✅ Background task {name} completed!")

@app.route('/start-task')
def start_task():
    thread = threading.Thread(target=background_task, args=("EmailSender",))
    thread.start()
    return jsonify({"message": "Task started in background!"})

if __name__ == "__main__":
    app.run(debug=True)
