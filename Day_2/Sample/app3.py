from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import os

DB_FILE = "example.db"
DB_URI = f"sqlite:///{DB_FILE}"

class UserModel:
    def __init__(self, app):
        self.db = SQLAlchemy(app)
        class User(self.db.Model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            name = self.db.Column(self.db.String(100), nullable=False)
        self.User = User
        with app.app_context():
            self.db.create_all()

def create_app(track_modifications):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = track_modifications
    return app

def run_benchmark(track_modifications, use_bulk=True):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    app = create_app(track_modifications)
    model = UserModel(app)
    db = model.db
    User = model.User

    with app.app_context():
        start_time = time.time()

        if use_bulk:
            users = [User(name=f"User {i}") for i in range(100000)]
            db.session.bulk_save_objects(users)
        else:
            users = [User(name=f"User {i}") for i in range(100000)]
            db.session.add_all(users)

        db.session.commit()
        duration = time.time() - start_time

    return duration

# Benchmarking
time_false_bulk = run_benchmark(False, use_bulk=True)
time_true_bulk = run_benchmark(True, use_bulk=True)

time_false_addall = run_benchmark(False, use_bulk=False)
time_true_addall = run_benchmark(True, use_bulk=False)

print(f"TRACK_MODIFICATIONS=False | bulk_save_objects: {time_false_bulk:.2f}s")
print(f"TRACK_MODIFICATIONS=True  | bulk_save_objects: {time_true_bulk:.2f}s")
print(f"TRACK_MODIFICATIONS=False | session.add_all(): {time_false_addall:.2f}s")
print(f"TRACK_MODIFICATIONS=True  | session.add_all(): {time_true_addall:.2f}s")
