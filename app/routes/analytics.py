
from flask import Blueprint, jsonify, request
from ..models import Student

analytics_bp = Blueprint("analytics", __name__)


def average(values):
    valid_values = [value for value in values if value is not None]
    return round(sum(valid_values) / len(valid_values), 1) if valid_values else 0

@analytics_bp.get("/summary")
def summary():
    department = request.args.get("department")
    query = Student.query

    if department and department != "All Departments":
        query = query.filter_by(department=department)

    students = query.all()
    total = len(students)

    valid_scores = [
        s.success_score for s in students
        if s.success_score is not None
    ]
    avg_score = average(valid_scores)

    academic_high = sum(s.academic_risk == "High" for s in students)
    placement_high = sum(s.placement_risk == "High" for s in students)

    risk_counts = {
        "Low": sum(s.academic_risk == "Low" for s in students),
        "Medium": sum(s.academic_risk == "Medium" for s in students),
        "High": academic_high,
    }

    dimensions = {
        "Academic": average([
            (s.cgpa / 10) * 100
            for s in students if s.cgpa is not None
        ]),
        "Attendance": average([s.attendance for s in students]),
        "LMS Activity": average([
            s.assignment_completion for s in students
        ]),
        "Engagement": average([s.engagement_score for s in students]),
        "Skills": average([
            (s.technical_skill_score + s.soft_skill_score) / 2
            for s in students
            if s.technical_skill_score is not None
            and s.soft_skill_score is not None
        ]),
        "Placement": average([
            (s.aptitude_score + s.coding_score + s.mock_interview_score) / 3
            for s in students
            if s.aptitude_score is not None
            and s.coding_score is not None
            and s.mock_interview_score is not None
        ]),
    }

    departments = sorted({
        s.department for s in Student.query.all()
    })

    segments = {
        name: sum(s.segment == name for s in students)
        for name in sorted({s.segment for s in students})
    }

    return jsonify({
        "total_students": total,
        "assessed_students": len(valid_scores),
        "average_success_score": avg_score,
        "academic_high_risk": academic_high,
        "placement_high_risk": placement_high,
        "risk_counts": risk_counts,
        "dimensions": dimensions,
        "departments": departments,
        "segments": segments,
    })
