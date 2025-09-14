from flask import render_template, request, redirect, url_for, flash
from app.views import bp
from app.models import Student

@bp.route('/')
def index():
    """Display all students."""
    students = Student.query.all()
    return render_template('index.html', students=students)

@bp.route('/add', methods=['GET', 'POST'])
def add_student():
    """Add a new student."""
    if request.method == 'POST':
        try:
            name = request.form['name']
            course = request.form['course']
            
            if not name or not course:
                flash('Name and course are required.', 'error')
                return render_template('add_student.html')
            
            Student.create(name=name, course=course)
            flash('Student added successfully!', 'success')
            return redirect(url_for('main.index'))
        
        except Exception as e:
            flash(f'Error adding student: {str(e)}', 'error')
            return render_template('add_student.html')
    
    return render_template('add_student.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    """Edit an existing student."""
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            name = request.form['name']
            course = request.form['course']
            
            if not name or not course:
                flash('Name and course are required.', 'error')
                return render_template('edit_student.html', student=student)
            
            student.update(name=name, course=course)
            flash('Student updated successfully!', 'success')
            return redirect(url_for('main.index'))
        
        except Exception as e:
            flash(f'Error updating student: {str(e)}', 'error')
            return render_template('edit_student.html', student=student)
    
    return render_template('edit_student.html', student=student)

@bp.route('/delete/<int:id>')
def delete_student(id):
    """Delete a student."""
    try:
        student = Student.query.get_or_404(id)
        student.delete()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))
