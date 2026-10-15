
import pandas as pd

from ..extensions import db
from ..models import Student
from ..models.import_history import ImportHistory
from .scoring import refresh_student_analysis


CATEGORY_FIELDS = {
    "academic": {
        "cgpa": (0, 10),
        "backlogs": (0, 100),
    },
    "attendance": {
        "attendance": (0, 100),
    },
    "lms": {
        "lms_logins_week": (0, 1000),
        "assignment_completion": (0, 100),
    },
    "engagement": {
        "engagement_score": (0, 100),
    },
    "placement": {
        "aptitude_score": (0, 100),
        "coding_score": (0, 100),
        "mock_interview_score": (0, 100),
    },
    "skills": {
        "technical_skill_score": (0, 100),
        "soft_skill_score": (0, 100),
    },
    "feedback": {
        "satisfaction_score": (0, 100),
    },
}

BASE_FIELDS = {"student_id", "name", "department"}


def import_student_csv(file_storage, category):
    """Import a CSV dataset and record its import history."""

    if category not in {"students", *CATEGORY_FIELDS.keys()}:
        raise ValueError("Unsupported dataset category.")

    try:
        frame = pd.read_csv(
            file_storage,
            dtype={"student_id": "string"},
        )
    except Exception as exc:
        raise ValueError(f"Could not read CSV: {exc}") from exc

    frame.columns = [
        str(column).strip().lower()
        for column in frame.columns
    ]

    if frame.empty:
        raise ValueError("The CSV file contains no data rows.")

    if frame.columns.duplicated().any():
        raise ValueError("The CSV contains duplicate column names.")

    required = (
        BASE_FIELDS
        if category == "students"
        else {"student_id", *CATEGORY_FIELDS[category].keys()}
    )

    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    created = 0
    updated = 0
    rejected = []
    seen_ids = set()

    # Track whether a student is new in this import without relying
    # on SQLAlchemy session membership after flushes.
    new_student_ids = set()

    try:
        for index, row in frame.iterrows():
            line_number = int(index) + 2
            raw_id = row.get("student_id")

            if pd.isna(raw_id) or not str(raw_id).strip():
                rejected.append({
                    "row": line_number,
                    "reason": "Student ID is missing.",
                })
                continue

            student_id = str(raw_id).strip()

            if student_id in seen_ids:
                rejected.append({
                    "row": line_number,
                    "student_id": student_id,
                    "reason": "Duplicate Student ID in this CSV.",
                })
                continue

            seen_ids.add(student_id)

            student = Student.query.filter_by(
                student_id=student_id
            ).first()

            is_new = student is None

            if category == "students" and is_new:
                name = row.get("name")
                department = row.get("department")

                if pd.isna(name) or not str(name).strip():
                    rejected.append({
                        "row": line_number,
                        "student_id": student_id,
                        "reason": "Name is missing.",
                    })
                    continue

                if (
                    pd.isna(department)
                    or not str(department).strip()
                ):
                    rejected.append({
                        "row": line_number,
                        "student_id": student_id,
                        "reason": "Department is missing.",
                    })
                    continue

                student = Student(
                    student_id=student_id,
                    name=str(name).strip(),
                    department=str(department).strip(),
                )
                db.session.add(student)
                new_student_ids.add(student_id)
                created += 1

            elif is_new:
                rejected.append({
                    "row": line_number,
                    "student_id": student_id,
                    "reason": (
                        "Student ID does not exist. "
                        "Import the students CSV first."
                    ),
                })
                continue

            try:
                fields = (
                    {"year": (1, 8)}
                    if category == "students"
                    else CATEGORY_FIELDS.get(category, {})
                )

                for field, bounds in fields.items():
                    if field not in row.index:
                        continue

                    value = row[field]

                    # Missing CSV values stay missing. Do not turn
                    # blanks into zero or overwrite existing values.
                    if pd.isna(value) or str(value).strip() == "":
                        continue

                    try:
                        number = float(value)
                    except (TypeError, ValueError) as exc:
                        raise ValueError(
                            f"{field} must be a valid number."
                        ) from exc

                    low, high = bounds

                    if not low <= number <= high:
                        raise ValueError(
                            f"{field} must be between {low} and {high}."
                        )

                    if field in {"backlogs", "year"}:
                        if not number.is_integer():
                            raise ValueError(
                                f"{field} must be a whole number."
                            )
                        parsed_value = int(number)
                    else:
                        parsed_value = number

                    setattr(student, field, parsed_value)

                refresh_student_analysis(student)

                if not is_new:
                    updated += 1

            except (ValueError, TypeError) as exc:
                raise ValueError(
                    f"Invalid data at CSV row {line_number}: {exc}. "
                    "No changes from this import were saved."
                ) from exc

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    result = {
        "category": category,
        "rows_received": len(frame),
        "created": created,
        "updated": updated,
        "rejected": rejected,
        "rejected_count": len(rejected),
        "success": len(rejected) == 0,
    }

    history = ImportHistory(
        category=category,
        filename=file_storage.filename or "uploaded.csv",
        rows_received=result["rows_received"],
        created=result["created"],
        updated=result["updated"],
        rejected=result["rejected_count"],
        status=(
            "completed"
            if result["success"]
            else "completed_with_errors"
        ),
    )

    try:
        db.session.add(history)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return result
