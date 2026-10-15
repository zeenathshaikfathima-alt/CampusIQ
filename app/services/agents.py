
from .scoring import analyze_student


def run_student_risk_agent(student):
    result = analyze_student(student)

    return {
        "agent": "Student Risk Analysis Agent",
        "student_id": student.student_id,
        "academic_risk": result["academic_risk"],
        "placement_risk": result["placement_risk"],
        "success_score": result["success_score"],
        "data_completeness": result["data_completeness"],
        "risk_drivers": result["risk_drivers"],
        "note": (
            "This prototype uses transparent rules, not a validated "
            "predictive model. Faculty should verify the findings."
        ),
    }


def run_recommendation_agent(student):
    result = analyze_student(student)

    actions = []
    missing_data = []

    # Academic recommendations
    if student.attendance is None:
        missing_data.append("attendance")
    elif student.attendance < 75:
        actions.append({
            "priority": "High" if student.attendance < 65 else "Medium",
            "area": "Attendance",
            "reason": f"Attendance is {student.attendance}%, below 75%.",
            "action": (
                "Arrange an advisor meeting and agree on an attendance "
                "recovery plan."
            ),
        })

    if student.cgpa is None:
        missing_data.append("CGPA")
    elif student.cgpa < 6.5:
        actions.append({
            "priority": "High" if student.cgpa < 5.5 else "Medium",
            "area": "Academic performance",
            "reason": f"CGPA is {student.cgpa}, below 6.5.",
            "action": (
                "Create a subject-level remedial plan and schedule "
                "a follow-up assessment."
            ),
        })

    if student.backlogs is None:
        missing_data.append("backlogs")
    elif student.backlogs > 0:
        actions.append({
            "priority": "High" if student.backlogs >= 3 else "Medium",
            "area": "Backlogs",
            "reason": f"The student has {student.backlogs} backlog(s).",
            "action": (
                "Prioritize backlog subjects and establish a weekly "
                "revision and assessment schedule."
            ),
        })

    if student.assignment_completion is None:
        missing_data.append("assignment completion")
    elif student.assignment_completion < 60:
        actions.append({
            "priority": "Medium",
            "area": "LMS assignments",
            "reason": (
                f"Assignment completion is "
                f"{student.assignment_completion}%, below 60%."
            ),
            "action": (
                "Review incomplete assignments and set a weekly "
                "completion target."
            ),
        })

    # Placement recommendations: evaluate available scores only.
    placement_fields = {
        "aptitude": student.aptitude_score,
        "coding": student.coding_score,
        "mock interview": student.mock_interview_score,
        "technical skills": student.technical_skill_score,
        "soft skills": student.soft_skill_score,
    }

    available_placement = {
        name: value
        for name, value in placement_fields.items()
        if value is not None
    }

    for name, value in placement_fields.items():
        if value is None:
            missing_data.append(name)

    if len(available_placement) >= 3:
        placement_average = (
            sum(available_placement.values())
            / len(available_placement)
        )

        if placement_average < 65:
            actions.append({
                "priority": (
                    "High" if placement_average < 40 else "Medium"
                ),
                "area": "Placement readiness",
                "reason": (
                    f"Average of available placement indicators is "
                    f"{placement_average:.1f}%, below 65%."
                ),
                "action": (
                    "Create a placement preparation plan covering the "
                    "weakest measured aptitude, coding, and interview "
                    "skills."
                ),
            })

        # Recommend specific practice based on the lowest measured areas.
        for name, value in sorted(
            available_placement.items(), key=lambda item: item[1]
        ):
            if value < 50:
                actions.append({
                    "priority": "Medium",
                    "area": name.title(),
                    "reason": f"{name.title()} score is {value}%, below 50%.",
                    "action": (
                        f"Assign targeted {name} practice and review "
                        "progress at the next checkpoint."
                    ),
                })

    else:
        missing_data.append(
            "at least three placement indicators are needed "
            "to assess placement readiness"
        )

    if not actions and result["data_completeness"] >= 60:
        actions.append({
            "priority": "Low",
            "area": "Progress monitoring",
            "reason": (
                "No major intervention trigger was identified by "
                "the current rules."
            ),
            "action": (
                "Maintain the current plan and review the student's "
                "indicators at the next checkpoint."
            ),
        })

    if result["data_completeness"] < 60:
        actions.insert(0, {
            "priority": "High",
            "area": "Data quality",
            "reason": (
                f"Only {result['data_completeness']}% of weighted "
                "scoring data is available."
            ),
            "action": (
                "Import the missing academic, attendance, engagement, "
                "and placement records before making a confident "
                "student assessment."
            ),
        })

    return {
        "agent": "Recommendation Agent",
        "student_id": student.student_id,
        "success_score": result["success_score"],
        "data_completeness": result["data_completeness"],
        "academic_risk": result["academic_risk"],
        "placement_risk": result["placement_risk"],
        "risk_drivers": result["risk_drivers"],
        "recommendations": actions,
        "missing_data": sorted(set(missing_data)),
        "requires_faculty_review": True,
        "note": (
            "Recommendations are rule-based suggestions and require "
            "faculty review before intervention."
        ),
    }


def run_data_quality_agent(student):
    result = analyze_student(student)

    tracked_fields = {
        "cgpa": student.cgpa,
        "backlogs": student.backlogs,
        "attendance": student.attendance,
        "assignment_completion": student.assignment_completion,
        "lms_logins_week": student.lms_logins_week,
        "engagement_score": student.engagement_score,
        "aptitude_score": student.aptitude_score,
        "coding_score": student.coding_score,
        "mock_interview_score": student.mock_interview_score,
        "technical_skill_score": student.technical_skill_score,
        "soft_skill_score": student.soft_skill_score,
    }

    missing_fields = [
        field
        for field, value in tracked_fields.items()
        if value is None
    ]

    return {
        "agent": "Data Quality Agent",
        "student_id": student.student_id,
        "data_completeness": result["data_completeness"],
        "missing_fields": missing_fields,
        "complete": len(missing_fields) == 0,
        "message": (
            "All tracked scoring fields are populated."
            if not missing_fields
            else "Import the missing data before relying on the analysis."
        ),
    }
