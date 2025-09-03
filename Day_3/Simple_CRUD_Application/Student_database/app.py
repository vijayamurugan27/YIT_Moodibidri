from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    university_number = db.Column(db.String(100), nullable=False, unique=True)
    department = db.Column(db.String(100), nullable=False)
    email_id = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"Student('{self.name}', '{self.university_number}', '{self.department}', '{self.email_id}')"

    def __init__(self, name, university_number, department, email_id):
        self.name = name
        self.university_number = university_number
        self.department = department
        self.email_id = email_id


@app.route('/')
def home():
    students = Student.query.all()
    return render_template('home.html', students=students)


@app.route('/bootstrap')
def bootstrap():
    students = Student.query.all()
    return render_template('bootstrap.html', students=students)


# @app.route('/details/<int:id>')
# def details(id):
#     student = Student.query.get_or_404(id)
#     return render_template('details.html', student=student)


@app.route('/detail_data/<int:id>')
def detail_data(id):
    student = Student.query.get_or_404(id)
    return render_template('detail_data.html', student=student)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.university_number = request.form['university_number']
        student.department = request.form['department']
        student.email_id = request.form['email_id']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('update.html', student=student)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(student)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('delete.html', student=student)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        student = Student(
            name=request.form['name'],
            university_number=request.form['university_number'],
            department=request.form['department'],
            email_id=request.form['email_id']
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
