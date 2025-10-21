from datetime import datetime
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app() -> Flask:
    """Application factory for the document management site."""

    app = Flask(__name__, instance_relative_config=True)

    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    database_path = instance_path / "documents.db"
    upload_folder = (Path(app.root_path).parent / "uploads").resolve()
    upload_folder.mkdir(parents=True, exist_ok=True)

    app.config.update(
        SECRET_KEY="change-me",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=str(upload_folder),
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50 MB max file size
    )

    db.init_app(app)

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.utcnow().year}

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
