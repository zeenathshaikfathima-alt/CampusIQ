from datetime import datetime
from ..extensions import db


class ImportHistory(db.Model):
    __tablename__ = "import_history"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    rows_received = db.Column(db.Integer, nullable=False, default=0)
    created = db.Column(db.Integer, nullable=False, default=0)
    updated = db.Column(db.Integer, nullable=False, default=0)
    rejected = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="completed")
    imported_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "filename": self.filename,
            "rows_received": self.rows_received,
            "created": self.created,
            "updated": self.updated,
            "rejected": self.rejected,
            "status": self.status,
            "imported_at": self.imported_at.isoformat(),
        }
