from datetime import date

from . import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(120), nullable=False)
    upload_date = db.Column(db.Date, nullable=False, default=date.today)
    stored_filename = db.Column(db.String(260), nullable=False)
    original_filename = db.Column(db.String(260), nullable=False)

    def __repr__(self) -> str:
        return f"<Document {self.title!r} ({self.id})>"

    @property
    def year(self) -> str:
        return self.upload_date.strftime("%Y")
