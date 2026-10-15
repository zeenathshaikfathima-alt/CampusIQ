import random
from app import create_app
from app.extensions import db
from app.models import Student
from app.services.scoring import refresh_student_analysis

random.seed(42)
app = create_app()

names = [
    "Aarav Sharma", "Priya Reddy", "Rahul Kumar", "Ananya Rao", "Sai Teja",
    "Meera Nair", "Arjun Patel", "Kavya Singh", "Vikram Das", "Ishita Verma",
    "Rohan Gupta", "Sana Khan", "Aditya Rao", "Divya Menon", "Kiran Reddy",
    "Neha Joshi", "Manoj Yadav", "Aisha Ali", "Harsha V", "Pooja Shah",
    "Nikhil Kumar", "Sravya M", "Farhan Ahmed", "Keerthi S", "Abhinav R"
]
departments = ["CSE", "AI & ML", "ECE", "EEE", "Mechanical"]

with app.app_context():
    if Student.query.count():
        print("Demo data already exists. No changes made.")
    else:
        for i, name in enumerate(names, start=1):
            profile = random.choice(["strong", "average", "risk", "placement_gap"])
            if profile == "strong":
                cgpa, attendance, backlogs = round(random.uniform(7.5, 9.5), 2), random.uniform(82, 98), 0
                aptitude, coding, mock = random.uniform(70, 95), random.uniform(70, 98), random.uniform(65, 95)
            elif profile == "risk":
                cgpa, attendance, backlogs = round(random.uniform(4.5, 6.4), 2), random.uniform(48, 74), random.randint(1, 4)
                aptitude, coding, mock = random.uniform(25, 60), random.uniform(20, 55), random.uniform(25, 60)
            elif profile == "placement_gap":
                cgpa, attendance, backlogs = round(random.uniform(7.5, 9.2), 2), random.uniform(80, 95), 0
                aptitude, coding, mock = random.uniform(30, 55), random.uniform(25, 50), random.uniform(30, 55)
            else:
                cgpa, attendance, backlogs = round(random.uniform(6.2, 7.8), 2), random.uniform(70, 88), random.randint(0, 1)
                aptitude, coding, mock = random.uniform(45, 75), random.uniform(45, 75), random.uniform(45, 75)
            s = Student(
                student_id=f"CIQ{i:04d}", name=name, department=departments[(i-1) % len(departments)],
                year=random.choice([2, 3, 4]), cgpa=cgpa, backlogs=backlogs,
                attendance=round(attendance, 1), lms_logins_week=random.randint(0, 14),
                assignment_completion=round(random.uniform(25, 100), 1),
                engagement_score=round(random.uniform(10, 100), 1),
                aptitude_score=round(aptitude, 1), coding_score=round(coding, 1),
                mock_interview_score=round(mock, 1),
                technical_skill_score=round(random.uniform(30, 95), 1),
                soft_skill_score=round(random.uniform(35, 95), 1),
                satisfaction_score=round(random.uniform(45, 100), 1)
            )
            db.session.add(s)
            db.session.flush()
            refresh_student_analysis(s)
        db.session.commit()
        print(f"Created {len(names)} synthetic demo students.")
        print("IMPORTANT: This is synthetic demonstration data, not real student records.")
