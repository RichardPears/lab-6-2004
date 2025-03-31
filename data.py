import pandas as pd
import numpy as np
from faker import Faker
from app import app, db
from models import Student
from datetime import datetime, timedelta
import random

fake = Faker()

def generate_student_dataframe(count=100):
    """Generate a pandas DataFrame with synthetic student data"""
    first_names = []
    last_names = []
    dobs = []
    amounts_due = []
    
    for _ in range(count):
        first_names.append(fake.first_name())
        last_names.append(fake.last_name())
        
        years_ago = random.randint(6, 22)
        days_variance = random.randint(-365, 365)  
        dob = datetime.now() - timedelta(days=365 * years_ago + days_variance)
        dobs.append(dob.date())
        
        amounts_due.append(round(random.uniform(0, 5000), 2))
    
    df = pd.DataFrame({
        'first_name': first_names,
        'last_name': last_names,
        'dob': dobs,
        'amount_due': amounts_due
    })
    
    return df

def save_dataframe_to_db(df):
    """Save the pandas DataFrame to the SQLite database"""
    with app.app_context():
        db.session.query(Student).delete()
        db.session.commit()
        
        for index, row in df.iterrows():
            student = Student(
                first_name=row['first_name'],
                last_name=row['last_name'],
                dob=row['dob'],
                amount_due=row['amount_due']
            )
            db.session.add(student)
            
            if (index + 1) % 10 == 0:
                db.session.commit()
        
        db.session.commit()
        print(f"Created {len(df)} student records in the database")

def analyze_data(df):
    """Perform basic analysis on the student data using pandas"""
    print(f"Total students: {len(df)}")
    
    today = datetime.now().date()
    df['age'] = df['dob'].apply(lambda x: (today - x).days // 365)
    
    print(f"Average age: {df['age'].mean():.2f} years")
    print(f"Youngest student: {df['age'].min()} years")
    print(f"Oldest student: {df['age'].max()} years")
    
    print(f"Average amount due: ${df['amount_due'].mean():.2f}")
    print(f"Highest amount due: ${df['amount_due'].max():.2f}")
    print(f"Total amount due: ${df['amount_due'].sum():.2f}")
    
    print("\nAge Distribution:")
    age_counts = df['age'].value_counts().sort_index()
    for age, count in age_counts.items():
        print(f"Age {age}: {count} students")
    
    df.drop('age', axis=1, inplace=True)
    
    return df

def sample_data(df, n=5):
    """Display a sample of n records from the DataFrame"""
    print(f"\nSample of {n} students:")
    sample = df.sample(n=min(n, len(df)))
    for _, row in sample.iterrows():
        print(f"Name: {row['first_name']} {row['last_name']}, "
              f"DOB: {row['dob']}, Amount Due: ${row['amount_due']:.2f}")

def generate_and_save_students(count=100):
    """Generate synthetic student data and save to database"""
    df = generate_student_dataframe(count)
    
    df = analyze_data(df)
    
    sample_data(df)
    
    save_dataframe_to_db(df)
    
    return df

if __name__ == "__main__":
    df = generate_and_save_students(10)
