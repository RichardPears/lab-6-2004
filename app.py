from flask import Flask, request, jsonify
from models import db, Student
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Create database tables when the app starts
with app.app_context():
    db.create_all()

# Create a new student
@app.route('/api/students', methods=['POST'])
def create_student():
    data = request.get_json()
    
    if not all(key in data for key in ['first_name', 'last_name', 'dob', 'amount_due']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        student = Student(
            first_name=data['first_name'],
            last_name=data['last_name'],
            dob=dob,
            amount_due=float(data['amount_due'])
        )
        db.session.add(student)
        db.session.commit()
        return jsonify(student.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get all students
@app.route('/api/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

# Get a specific student
@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify(student.to_dict())

# Update a student
@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    data = request.get_json()
    
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'dob' in data:
        student.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
    if 'amount_due' in data:
        student.amount_due = float(data['amount_due'])
    
    db.session.commit()
    return jsonify(student.to_dict())

# Delete a student
@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': f'Student with ID {student_id} deleted successfully'})

@app.route("/")
def home():
    return "Hello, World! The Flask API is running."

if __name__ == '__main__':
    app.run(debug=True)