from flask import Blueprint, jsonify
from ..models.import_history import ImportHistory

import_history_bp = Blueprint("import_history", __name__)


@import_history_bp.get("/")
def get_import_history():
    records = (
        ImportHistory.query
        .order_by(ImportHistory.imported_at.desc())
        .limit(100)
        .all()
    )

    return jsonify({
        "total": len(records),
        "imports": [record.to_dict() for record in records]
    })
