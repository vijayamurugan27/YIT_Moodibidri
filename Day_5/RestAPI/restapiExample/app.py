from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
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

with app.app_context():
    db.create_all()

# ------------------ REST API (same as before) ------------------
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])

@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    if student:
        return jsonify(student.to_dict())
    return jsonify({"error": "Student not found"}), 404

@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    new_student = Student(name=data['name'], course=data['course'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict()), 201

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

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"})

# ------------------ HTML CRUD Routes ------------------

@app.route('/')
def home():
    students = Student.query.all()
    return render_template("index.html", students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student_html():
    if request.method == 'POST':
        name = request.form['name']
        course = request.form['course']
        new_student = Student(name=name, course=course)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add_student.html")

@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student_html(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.course = request.form['course']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit_student.html", student=student)

@app.route('/delete/<int:student_id>')
def delete_student_html(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('home'))

# ------------------ Run ------------------
if __name__ == '__main__':
    app.run(debug=True)
