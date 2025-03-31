import pytest
import json
import sys
import os

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Student
from datetime import datetime, date

@pytest.fixture
def client():
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Create application context first
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Then create test client within the app context
        with app.test_client() as test_client:
            yield test_client
        
        # Clean up after test
        db.session.remove()
        db.drop_all()

def test_create_student(client):
    with app.app_context():
        response = client.post('/api/students', 
                            data=json.dumps({
                                'first_name': 'John',
                                'last_name': 'Doe',
                                'dob': '2000-01-01',
                                'amount_due': 100.50
                            }),
                            content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['first_name'] == 'John'
        assert data['last_name'] == 'Doe'
        assert data['dob'] == '2000-01-01'
        assert data['amount_due'] == 100.50

def test_get_students(client):
    with app.app_context():
        # Add a test student
        student = Student(
            first_name='Jane',
            last_name='Smith',
            dob=date(1995, 5, 15),
            amount_due=200.75
        )
        db.session.add(student)
        db.session.commit()
        
        response = client.get('/api/students')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['first_name'] == 'Jane'
        assert data[0]['last_name'] == 'Smith'

def test_get_student(client):
    with app.app_context():
        # Add a test student
        student = Student(
            first_name='Alice',
            last_name='Johnson',
            dob=date(1998, 8, 20),
            amount_due=150.25
        )
        db.session.add(student)
        db.session.commit()
        student_id = student.student_id
        
        response = client.get(f'/api/students/{student_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['first_name'] == 'Alice'
        assert data['last_name'] == 'Johnson'
        assert data['dob'] == '1998-08-20'
        assert data['amount_due'] == 150.25

def test_update_student(client):
    with app.app_context():
        # Add a test student
        student = Student(
            first_name='Bob',
            last_name='Brown',
            dob=date(1992, 3, 10),
            amount_due=300.00
        )
        db.session.add(student)
        db.session.commit()
        student_id = student.student_id
        
        response = client.put(f'/api/students/{student_id}',
                            data=json.dumps({
                                'first_name': 'Robert',
                                'amount_due': 350.00
                            }),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['first_name'] == 'Robert'  # Updated
        assert data['last_name'] == 'Brown'    # Unchanged
        assert data['amount_due'] == 350.00    # Updated

def test_delete_student(client):
    with app.app_context():
        # Add a test student
        student = Student(
            first_name='Charlie',
            last_name='Davis',
            dob=date(1990, 12, 25),
            amount_due=450.50
        )
        db.session.add(student)
        db.session.commit()
        student_id = student.student_id
        
        response = client.delete(f'/api/students/{student_id}')
        assert response.status_code == 200
        
        # Verify student is deleted
        response = client.get(f'/api/students/{student_id}')
        assert response.status_code == 404