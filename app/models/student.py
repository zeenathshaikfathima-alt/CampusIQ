
from datetime import datetime
from ..extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    # Required student information
    student_id = db.Column(
        db.String(30), unique=True, nullable=False, index=True
    )
    name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(80), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, default=3)

    # Optional academic and engagement data.
    # None means the value has not been provided.
    cgpa = db.Column(db.Float, nullable=True, default=None)
    backlogs = db.Column(db.Integer, nullable=True, default=None)
    attendance = db.Column(db.Float, nullable=True, default=None)
    lms_logins_week = db.Column(db.Integer, nullable=True, default=None)
    assignment_completion = db.Column(db.Float, nullable=True, default=None)
    engagement_score = db.Column(db.Float, nullable=True, default=None)

    # Optional placement-readiness data
    aptitude_score = db.Column(db.Float, nullable=True, default=None)
    coding_score = db.Column(db.Float, nullable=True, default=None)
    mock_interview_score = db.Column(db.Float, nullable=True, default=None)
    technical_skill_score = db.Column(db.Float, nullable=True, default=None)
    soft_skill_score = db.Column(db.Float, nullable=True, default=None)
    satisfaction_score = db.Column(db.Float, nullable=True, default=None)

    # Analysis results can also be unavailable when no input data exists.
    success_score = db.Column(db.Float, nullable=True, default=None)
    academic_risk = db.Column(
        db.String(30), nullable=False, default="Insufficient data"
    )
    placement_risk = db.Column(
        db.String(30), nullable=False, default="Insufficient data"
    )
    segment = db.Column(
        db.String(100), nullable=False, default="Insufficient data"
    )

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "name": self.name,
            "department": self.department,
            "year": self.year,
            "cgpa": self.cgpa,
            "backlogs": self.backlogs,
            "attendance": self.attendance,
            "lms_logins_week": self.lms_logins_week,
            "assignment_completion": self.assignment_completion,
            "engagement_score": self.engagement_score,
            "aptitude_score": self.aptitude_score,
            "coding_score": self.coding_score,
            "mock_interview_score": self.mock_interview_score,
            "technical_skill_score": self.technical_skill_score,
            "soft_skill_score": self.soft_skill_score,
            "satisfaction_score": self.satisfaction_score,
            "success_score": self.success_score,
            "academic_risk": self.academic_risk,
            "placement_risk": self.placement_risk,
            "segment": self.segment,
        }
