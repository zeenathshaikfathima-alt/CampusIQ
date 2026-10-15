
from app import create_app
from app.extensions import db
from sqlalchemy import inspect
from alembic.migration import MigrationContext
from alembic.operations import Operations

NULLABLE_FIELDS = [
    "cgpa",
    "backlogs",
    "attendance",
    "lms_logins_week",
    "assignment_completion",
    "engagement_score",
    "aptitude_score",
    "coding_score",
    "mock_interview_score",
    "technical_skill_score",
    "soft_skill_score",
    "satisfaction_score",
    "success_score",
]

app = create_app()

with app.app_context():
    engine = db.engine
    columns = {
        c["name"]: c
        for c in inspect(engine).get_columns("students")
    }

    missing = [name for name in NULLABLE_FIELDS if name not in columns]
    if missing:
        raise RuntimeError(f"Missing expected columns: {missing}")

    required_changes = [
        name for name in NULLABLE_FIELDS
        if not columns[name]["nullable"]
    ]

    if not required_changes:
        print("All scoring fields are already nullable.")
    else:
        with engine.begin() as connection:
            context = MigrationContext.configure(connection)
            operations = Operations(context)

            with operations.batch_alter_table(
                "students", recreate="always"
            ) as batch:
                for name in required_changes:
                    batch.alter_column(
                        name,
                        existing_type=columns[name]["type"],
                        nullable=True,
                    )

        print("Migration completed:", required_changes)

    print(
        "Verified:",
        [(c["name"], c["nullable"])
         for c in inspect(engine).get_columns("students")
         if c["name"] in NULLABLE_FIELDS],
    )
