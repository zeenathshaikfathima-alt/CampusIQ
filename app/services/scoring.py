
def to_number(value):
    """Convert a value to a finite number; return None when unavailable."""
    if value is None:
        return None

    try:
        number = float(value)
        if number != number or number in (float("inf"), float("-inf")):
            return None
        return number
    except (TypeError, ValueError):
        return None


def clamp(value, low=0, high=100):
    number = to_number(value)
    if number is None:
        return None
    return max(low, min(high, number))


def analyze_student(student):
    fields = {
        "cgpa": to_number(student.cgpa),
        "backlogs": to_number(student.backlogs),
        "attendance": clamp(student.attendance),
        "assignment": clamp(student.assignment_completion),
        "lms_logins": to_number(student.lms_logins_week),
        "engagement": clamp(student.engagement_score),
        "aptitude": clamp(student.aptitude_score),
        "coding": clamp(student.coding_score),
        "mock_interview": clamp(student.mock_interview_score),
        "technical": clamp(student.technical_skill_score),
        "soft_skills": clamp(student.soft_skill_score),
    }

    cgpa = fields["cgpa"]
    backlogs = fields["backlogs"]
    attendance = fields["attendance"]
    assignment = fields["assignment"]
    lms_logins = fields["lms_logins"]
    engagement = fields["engagement"]
    aptitude = fields["aptitude"]
    coding = fields["coding"]
    mock_interview = fields["mock_interview"]
    technical = fields["technical"]
    soft_skills = fields["soft_skills"]

    weighted_signals = {
        "cgpa": (
            clamp(cgpa / 10 * 100) if cgpa is not None else None,
            0.25,
        ),
        "backlogs": (
            clamp(100 - backlogs * 22) if backlogs is not None else None,
            0.10,
        ),
        "attendance": (attendance, 0.20),
        "assignment": (assignment, 0.10),
        "lms": (
            clamp(lms_logins / 7 * 100)
            if lms_logins is not None else None,
            0.05,
        ),
        "engagement": (engagement, 0.05),
        "aptitude": (aptitude, 0.08),
        "coding": (coding, 0.07),
        "technical": (technical, 0.06),
        "soft_skills": (soft_skills, 0.04),
    }

    total_possible_weight = sum(
        weight for _, weight in weighted_signals.values()
    )

    total_available_weight = sum(
        weight
        for value, weight in weighted_signals.values()
        if value is not None
    )

    data_completeness = round(
        total_available_weight / total_possible_weight * 100, 1
    )

    if total_available_weight > 0:
        score = round(
            sum(
                value * weight
                for value, weight in weighted_signals.values()
                if value is not None
            ) / total_available_weight,
            1,
        )
    else:
        score = None

    # Components are normalized weighted contributions.
    # Their sum equals the success score, subject to rounding.
    components = {
        key: (
            round(value * weight / total_available_weight, 1)
            if value is not None and total_available_weight > 0
            else None
        )
        for key, (value, weight) in weighted_signals.items()
    }

    # Academic risk
    academic_data_count = sum(
        value is not None
        for value in (cgpa, backlogs, attendance)
    )

    academic_risk = "Insufficient data"

    if academic_data_count >= 2:
        high_academic_risk = (
            (attendance is not None and attendance < 65)
            or (cgpa is not None and cgpa < 5.5)
            or (backlogs is not None and backlogs >= 3)
        )

        medium_academic_risk = (
            (attendance is not None and attendance < 75)
            or (cgpa is not None and cgpa < 6.5)
            or (backlogs is not None and backlogs >= 1)
        )

        if high_academic_risk:
            academic_risk = "High"
        elif medium_academic_risk:
            academic_risk = "Medium"
        else:
            academic_risk = "Low"

    # Placement risk
    placement_values = [
        value
        for value in (
            aptitude, coding, mock_interview, technical, soft_skills
        )
        if value is not None
    ]

    placement_average = (
        sum(placement_values) / len(placement_values)
        if placement_values else None
    )

    placement_risk = "Insufficient data"

    if len(placement_values) >= 3:
        if placement_average < 40:
            placement_risk = "High"
        elif placement_average < 65:
            placement_risk = "Medium"
        else:
            placement_risk = "Low"

    # Student segmentation
    if data_completeness < 60:
        segment = "Insufficient data"
    elif (
        cgpa is not None
        and cgpa >= 7.5
        and placement_average is not None
        and len(placement_values) >= 3
        and placement_average < 55
    ):
        segment = "High academics, low placement readiness"
    elif academic_risk == "High":
        segment = "Academic support needed"
    elif placement_risk == "High":
        segment = "Placement preparation needed"
    elif score is not None and score >= 80:
        segment = "High-performing"
    elif engagement is not None and engagement < 35:
        segment = "Low engagement"
    else:
        segment = "Developing steadily"

    # Explainable risk drivers
    risk_drivers = []

    if attendance is not None and attendance < 75:
        risk_drivers.append("Attendance below 75%")

    if cgpa is not None and cgpa < 6.5:
        risk_drivers.append("CGPA below 6.5")

    if backlogs is not None and backlogs > 0:
        risk_drivers.append("Active backlogs")

    if placement_average is not None and placement_average < 65:
        risk_drivers.append("Placement assessment average below 65")

    if assignment is not None and assignment < 60:
        risk_drivers.append("Low assignment completion")

    if data_completeness < 100:
        risk_drivers.append(
            f"Incomplete scoring data ({data_completeness}% available)"
        )

    return {
        "success_score": score,
        "data_completeness": data_completeness,
        "academic_risk": academic_risk,
        "placement_risk": placement_risk,
        "segment": segment,
        "score_components": components,
        "risk_drivers": risk_drivers,
    }


def refresh_student_analysis(student):
    result = analyze_student(student)

    student.success_score = result["success_score"]
    student.academic_risk = result["academic_risk"]
    student.placement_risk = result["placement_risk"]
    student.segment = result["segment"]

    return result
