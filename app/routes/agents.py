
from flask import Blueprint, jsonify

from ..models import Student
from ..services.agents import (
    run_student_risk_agent,
    run_recommendation_agent,
    run_data_quality_agent,
)

agents_bp = Blueprint("agents", __name__)


@agents_bp.get("/insights")
def insights():
    students = Student.query.all()

    if not students:
        return jsonify({
            "status": "no_data",
            "message": "Import student records to generate insights.",
            "insights": [],
        })

    sufficiently_assessed = [
        student
        for student in students
        if student.success_score is not None
    ]

    high_academic = [
        student for student in sufficiently_assessed
        if student.academic_risk == "High"
    ]

    high_placement = [
        student for student in sufficiently_assessed
        if student.placement_risk == "High"
    ]

    low_attendance = [
        student for student in students
        if student.attendance is not None
        and student.attendance < 75
    ]

    incomplete = [
        student for student in students
        if run_data_quality_agent(student)["data_completeness"] < 100
    ]

    items = []

    if high_academic:
        items.append({
            "type": "academic_risk",
            "title": f"{len(high_academic)} students have high academic risk",
            "detail": "Review attendance, CGPA, and backlogs with faculty.",
        })

    if high_placement:
        items.append({
            "type": "placement_risk",
            "title": f"{len(high_placement)} students have high placement risk",
            "detail": "Review placement scores and plan targeted practice.",
        })

    if low_attendance:
        items.append({
            "type": "attendance",
            "title": f"{len(low_attendance)} students have attendance below 75%",
            "detail": "Verify attendance records and arrange faculty follow-up.",
        })

    items.append({
        "type": "data_quality",
        "title": f"{len(incomplete)} students have incomplete scoring data",
        "detail": (
            "Complete missing records before relying on student risk "
            "or recommendation results."
        ),
    })

    return jsonify({"status": "ok", "insights": items})


@agents_bp.get("/student/<student_id>")
def student_agents(student_id):
    student = Student.query.filter_by(
        student_id=student_id
    ).first_or_404()

    return jsonify({
        "risk_agent": run_student_risk_agent(student),
        "recommendation_agent": run_recommendation_agent(student),
        "data_quality_agent": run_data_quality_agent(student),
    })
