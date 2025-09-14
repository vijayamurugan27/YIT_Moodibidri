from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------
# Database Model
# -----------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        """Serialization for JSON APIs"""
        return {"id": self.id, "name": self.name, "course": self.course}

with app.app_context():
    db.create_all()

# =========================================================
# JSON REST API ROUTES (For Postman, Jupyter, etc.)
# =========================================================

@app.route("/api/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])

@app.route("/api/students/<int:id>", methods=["GET"])
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify(student.to_dict())

@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json()
    if not data or "name" not in data or "course" not in data:
        return jsonify({"error": "Invalid input"}), 400
    new_student = Student(name=data["name"], course=data["course"])
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict()), 201

@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    if "name" in data:
        student.name = data["name"]
    if "course" in data:
        student.course = data["course"]
    db.session.commit()
    return jsonify(student.to_dict())

@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": f"Student {id} deleted"}), 200

# =========================================================
# HTML ROUTES (Browser UI)
# =========================================================

@app.route("/")
def home():
    return redirect(url_for("list_students_html"))

@app.route("/students")
def list_students_html():
    students = Student.query.all()
    return render_template("list_students.html", students=students)

@app.route("/students/add", methods=["GET", "POST"])
def add_student_html():
    if request.method == "POST":
        name = request.form["name"]
        course = request.form["course"]
        student = Student(name=name, course=course)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for("list_students_html"))
    return render_template("add_student.html")

@app.route("/students/edit/<int:id>", methods=["GET", "POST"])
def edit_student_html(id):
    student = Student.query.get_or_404(id)
    if request.method == "POST":
        student.name = request.form["name"]
        student.course = request.form["course"]
        db.session.commit()
        return redirect(url_for("list_students_html"))
    return render_template("edit_student.html", student=student)

@app.route("/students/delete/<int:id>", methods=["POST"])
def delete_student_html(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for("list_students_html"))

# =========================================================
# Run the App
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)
