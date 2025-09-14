from app import db

class Student(db.Model):
    """Student model."""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Student {self.name}>'
    
    def serialize(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "course": self.course
        }
    
    @classmethod
    def create(cls, name, course):
        """Create a new student."""
        student = cls(name=name, course=course)
        db.session.add(student)
        db.session.commit()
        return student
    
    def update(self, **kwargs):
        """Update student attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the student."""
        db.session.delete(self)
        db.session.commit()
