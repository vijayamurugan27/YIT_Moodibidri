from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------ Model ------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "course": self.course}

# Create tables if not already present
with app.app_context():
    db.create_all()

# ------------------ Routes ------------------

# Home
@app.route('/')
def home():
    return "Welcome to the Student REST API with Database! 🚀 Try /students"

# ✅ READ all students
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])

# ✅ READ single student
@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    if student:
        return jsonify(student.to_dict())
    return jsonify({"error": "Student not found"}), 404

# ✅ CREATE a new student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    if not data or "name" not in data or "course" not in data:
        return jsonify({"error": "Invalid data"}), 400

    new_student = Student(name=data['name'], course=data['course'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict()), 201

# ✅ UPDATE a student
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    student.name = data.get("name", student.name)
    student.course = data.get("course", student.course)
    db.session.commit()
    return jsonify(student.to_dict())

# ✅ DELETE a student
@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"})

# ------------------ Run ------------------
if __name__ == '__main__':
    app.run(debug=True)
