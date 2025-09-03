from flask import Flask
from flask_sqlalchemy import SQLAlchemy


import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Set to False for better performance

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Create a large number of users
start_time = time.time()
for i in range(100000):
    user = User(name=f"User {i}")
    db.session.add(user)
db.session.commit()
print(f"Time taken: {time.time() - start_time} seconds")

# Repeat the same operation with SQLALCHEMY_TRACK_MODIFICATIONS set to True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
start_time = time.time()
for i in range(100000):
    user = User(name=f"User {i}")
    db.session.add(user)
db.session.commit()
print(f"Time taken with tracking enabled: {time.time() - start_time} seconds")