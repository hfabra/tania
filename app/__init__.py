from datetime import datetime
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="change-me",
        SQLALCHEMY_DATABASE_URI="sqlite:///documents.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=str(Path("uploads")),
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50 MB max file size
    )

    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.utcnow().year}

    with app.app_context():
        from . import routes  # noqa: F401
        db.create_all()

    return app
