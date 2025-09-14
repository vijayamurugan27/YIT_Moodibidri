# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)

# # Database configuration (SQLite)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# # Define the Student model
# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     course = db.Column(db.String(50), nullable=False)

#     def to_dict(self):
#         return {"id": self.id, "name": self.name, "course": self.course}


# # Create the database tables
# with app.app_context():
#     db.create_all()


# # ----------- REST API Routes -----------


# # @app.route('/')
# # def home():
# #     return "Welcome to the Student REST API with Database! 🚀 Try /students"

# # Home
# @app.route('/')
# def home():
#     return "Welcome to the Student REST API with Database! try /students"


# # Get all students
# @app.route('/students', methods=['GET'])
# def get_students():
#     students = Student.query.all()
#     return jsonify([s.to_dict() for s in students])


# # Get single student by ID
# @app.route('/students/<int:student_id>', methods=['GET'])
# def get_student(student_id):
#     student = Student.query.get(student_id)
#     if student:
#         return jsonify(student.to_dict())
#     return jsonify({"error": "Student not found"}), 404


# # Add new student
# @app.route('/students', methods=['POST'])
# def add_student():
#     data = request.get_json()
#     new_student = Student(name=data['name'], course=data['course'])
#     db.session.add(new_student)
#     db.session.commit()
#     return jsonify(new_student.to_dict()), 201


# # Update student
# @app.route('/students/<int:student_id>', methods=['PUT'])
# def update_student(student_id):
#     data = request.get_json()
#     student = Student.query.get(student_id)
#     if student:
#         student.name = data.get('name', student.name)
#         student.course = data.get('course', student.course)
#         db.session.commit()
#         return jsonify(student.to_dict())
#     return jsonify({"error": "Student not found"}), 404


# # Delete student
# @app.route('/students/<int:student_id>', methods=['DELETE'])
# def delete_student(student_id):
#     student = Student.query.get(student_id)
#     if student:
#         db.session.delete(student)
#         db.session.commit()
#         return jsonify({"message": "Student deleted"})
#     return jsonify({"error": "Student not found"}), 404


# # Run the app
# if __name__ == '__main__':
#     app.run(debug=True)










from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "course": self.course}


# Create the database tables
with app.app_context():
    db.create_all()


# ----------- REST API Routes -----------

# Home
@app.route('/')
def home():
    return "Welcome to the Student REST API with Database! Try /students"


# Get all students
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])


# Get single student by ID
@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    if student:
        return jsonify(student.to_dict())
    return jsonify({"error": "Student not found"}), 404


# Add new student
@app.route('/students', methods=['POST'])
def add_student():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'name' not in data or 'course' not in data:
            return jsonify({"error": "Missing required fields: name and course"}), 400
        
        new_student = Student(name=data['name'], course=data['course'])
        db.session.add(new_student)
        db.session.commit()
        return jsonify(new_student.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create student: " + str(e)}), 500


# Update student
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        data = request.get_json()
        student = Student.query.get(student_id)
        
        if student:
            # Only update fields that are provided
            if 'name' in data:
                student.name = data['name']
            if 'course' in data:
                student.course = data['course']
                
            db.session.commit()
            return jsonify(student.to_dict())
        return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update student: " + str(e)}), 500


# Delete student
@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        student = Student.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return jsonify({"message": "Student deleted"})
        return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete student: " + str(e)}), 500


# Run the app
if __name__ == '__main__':
    app.run(debug=True)