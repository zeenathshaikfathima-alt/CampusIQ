
from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Student
from ..services.scoring import refresh_student_analysis, analyze_student

students_bp = Blueprint("students", __name__)


def student_with_analysis(student):
    """Return the student record with its latest scoring explanation."""
    data = student.to_dict()
    analysis = analyze_student(student)

    data["data_completeness"] = analysis["data_completeness"]
    data["score_components"] = analysis["score_components"]
    data["risk_drivers"] = analysis["risk_drivers"]

    # Include the latest calculated analysis for detailed student views.
    data["explanation"] = analysis

    return data


@students_bp.get("")
def list_students():
    query = Student.query

    department = request.args.get("department")
    search = request.args.get("search", "").strip()
    risk = request.args.get("risk")

    if department and department != "All Departments":
        query = query.filter_by(department=department)

    if search:
        query = query.filter(
            db.or_(
                Student.name.ilike(f"%{search}%"),
                Student.student_id.ilike(f"%{search}%"),
            )
        )

    if risk:
        query = query.filter_by(academic_risk=risk)

    students = query.order_by(Student.success_score.asc()).all()

    return jsonify([
        student_with_analysis(student)
        for student in students
    ])


@students_bp.get("/<student_id>")
def get_student(student_id):
    student = Student.query.filter_by(
        student_id=student_id
    ).first_or_404()

    return jsonify(student_with_analysis(student))


@students_bp.post("")
def create_student():
    data = request.get_json(silent=True) or {}

    required = ["student_id", "name", "department"]
    missing = [
        key for key in required
        if not data.get(key)
    ]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing,
        }), 400

    if Student.query.filter_by(
        student_id=data["student_id"]
    ).first():
        return jsonify({
            "error": "Student ID already exists"
        }), 409

    allowed = {
        column.name
        for column in Student.__table__.columns
    }

    protected_fields = {
        "id",
        "success_score",
        "academic_risk",
        "placement_risk",
        "segment",
        "created_at",
    }

    student_data = {
        key: value
        for key, value in data.items()
        if key in allowed and key not in protected_fields
    }

    student = Student(**student_data)

    db.session.add(student)
    db.session.flush()

    refresh_student_analysis(student)
    db.session.commit()

    return jsonify(student_with_analysis(student)), 201
