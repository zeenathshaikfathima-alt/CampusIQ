from flask import render_template
from flask import Blueprint, jsonify, request
from .students import students_bp
from ..services.data_integration import import_student_csv

data_import_bp = Blueprint("data_import", __name__)
@data_import_bp.get("/page")
def import_page():
    return render_template("data_import/index.html")

@data_import_bp.post("/csv")
def upload_csv():
    uploaded_file = request.files.get("file")
    category = request.form.get("category", "").strip().lower()

    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"error": "Please select a CSV file."}), 400

    if not uploaded_file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported."}), 400

    if uploaded_file.content_length and uploaded_file.content_length > 5 * 1024 * 1024:
        return jsonify({"error": "Maximum upload size is 5 MB."}), 413

    try:
        result = import_student_csv(uploaded_file, category)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({
            "error": "The import failed. No changes were committed."
        }), 500
