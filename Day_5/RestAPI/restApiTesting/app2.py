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
        """Serialization: Convert model to dict"""
        return {"id": self.id, "name": self.name, "course": self.course}


with app.app_context():
    db.create_all()

# =========================================================
# JSON REST API ROUTES
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
    student = Student(name=data["name"], course=data["course"])
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201

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
# HTML ROUTES (Bootstrap UI)
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
        student = Student(name=request.form["name"], course=request.form["course"])
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
# Automated API Testing (flask test)
# =========================================================

@app.cli.command("test")
def test_api():
    import json
    with app.test_client() as client:
        # Create
        response = client.post("/api/students", json={"name": "Test User", "course": "AI"})
        assert response.status_code == 201
        student_id = json.loads(response.data)["id"]
        print("✅ POST works")

        # Read
        response = client.get(f"/api/students/{student_id}")
        assert response.status_code == 200
        print("✅ GET works")

        # Update
        response = client.put(f"/api/students/{student_id}", json={"course": "ML"})
        assert response.status_code == 200
        print("✅ PUT works")

        # Delete
        response = client.delete(f"/api/students/{student_id}")
        assert response.status_code == 200
        print("✅ DELETE works")

        # Verify
        response = client.get(f"/api/students/{student_id}")
        assert response.status_code == 404
        print("✅ Delete verified")

    print("🎉 All API tests passed!")

if __name__ == "__main__":
    app.run(debug=True)
