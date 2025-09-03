from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import os

DB_PATH = "sqlite:///example.db"

def create_app(track_modifications):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = track_modifications
    return app

class UserModel:
    def __init__(self, app):
        self.db = SQLAlchemy(app)
        class User(self.db.Model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            name = self.db.Column(self.db.String(100), nullable=False)
        self.User = User
        with app.app_context():
            self.db.create_all()

def run_benchmark(track_modifications):
    # Remove old DB to avoid conflicts between runs
    if os.path.exists("example.db"):
        os.remove("example.db")

    app = create_app(track_modifications)
    model = UserModel(app)
    User = model.User
    db = model.db

    with app.app_context():
        start_time = time.time()
        users = [User(name=f"User {i}") for i in range(100000)]
        db.session.bulk_save_objects(users)
        db.session.commit()
        duration = time.time() - start_time
    return duration

time_false = run_benchmark(False)
time_true = run_benchmark(True)

print(f"Time with TRACK_MODIFICATIONS=False: {time_false:.2f} seconds")
print(f"Time with TRACK_MODIFICATIONS=True: {time_true:.2f} seconds")
