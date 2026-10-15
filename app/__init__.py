from flask import Flask, jsonify
from config import Config
from .extensions import db, migrate
from .routes.import_history import import_history_bp
def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa: F401
    from .models.import_history import ImportHistory  # noqa: F401
    from .routes.dashboard import dashboard_bp
    from .routes.students import students_bp
    from .routes.analytics import analytics_bp
    from .routes.agents import agents_bp
    from .routes.data_import import data_import_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp, url_prefix="/api/students")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(agents_bp, url_prefix="/api/agents")
    app.register_blueprint(data_import_bp, url_prefix="/api/import")
    app.register_blueprint(
    import_history_bp,
    url_prefix="/api/import-history"
)
    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "application": "CampusIQ"})

    with app.app_context():
        db.create_all()

    return app
