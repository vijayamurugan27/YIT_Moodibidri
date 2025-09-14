from flask import request, jsonify
from app.api import bp
from app.models import Student
from app import db

@bp.route('/students', methods=['POST'])
def create_student():
    """Create a new student via API."""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'course' not in data:
            return jsonify({'error': 'Invalid input. Name and course are required.'}), 400
        
        student = Student.create(name=data['name'], course=data['course'])
        return jsonify(student.serialize()), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/students', methods=['GET'])
def get_students():
    """Get all students via API."""
    try:
        students = Student.query.all()
        return jsonify([student.serialize() for student in students])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    """Get a single student by ID via API."""
    try:
        student = Student.query.get(id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        return jsonify(student.serialize())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    """Update a student via API."""
    try:
        data = request.get_json()
        student = Student.query.get(id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Update fields if provided
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'course' in data:
            update_data['course'] = data['course']
        
        student.update(**update_data)
        return jsonify(student.serialize())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    """Delete a student via API."""
    try:
        student = Student.query.get(id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        student.delete()
        return jsonify({'message': 'Student deleted successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
