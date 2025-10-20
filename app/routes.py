from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from sqlalchemy import func, or_
from werkzeug.utils import secure_filename

from . import db
from .models import Document

bp = Blueprint("main", __name__)


@bp.record_once
def on_load(state):
    app = state.app
    app.register_blueprint(bp)


def _get_upload_path() -> Path:
    return Path(current_app.config["UPLOAD_FOLDER"])


@bp.route("/", methods=["GET", "POST"])
def index() -> str:
    if request.method == "POST":
        return _handle_upload()

    query = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()
    year_filter = request.args.get("year", "").strip()

    documents = Document.query

    if query:
        like_query = f"%{query}%"
        documents = documents.filter(
            or_(
                Document.title.ilike(like_query),
                Document.description.ilike(like_query),
                Document.original_filename.ilike(like_query),
            )
        )

    if category_filter:
        documents = documents.filter(Document.category == category_filter)

    if year_filter:
        documents = documents.filter(func.strftime("%Y", Document.upload_date) == year_filter)

    documents = documents.order_by(Document.upload_date.desc(), Document.title.asc()).all()

    categories = [row[0] for row in db.session.query(Document.category).distinct().order_by(Document.category).all()]
    years = [row[0] for row in db.session.query(func.strftime("%Y", Document.upload_date)).distinct().order_by(func.strftime("%Y", Document.upload_date)).all()]

    return render_template(
        "index.html",
        documents=documents,
        query=query,
        category_filter=category_filter,
        year_filter=year_filter,
        categories=categories,
        years=years,
    )


def _handle_upload() -> Response:
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    upload_date_str = request.form.get("upload_date", "").strip()
    file = request.files.get("file")

    if not title or not description or not category or not upload_date_str or not file or not file.filename:
        flash("Todos los campos son obligatorios", "error")
        return redirect(url_for("main.index"))

    try:
        upload_date = datetime.strptime(upload_date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("La fecha no tiene un formato válido (YYYY-MM-DD)", "error")
        return redirect(url_for("main.index"))

    safe_name = secure_filename(file.filename)
    if not safe_name:
        flash("El nombre del archivo contiene caracteres inválidos", "error")
        return redirect(url_for("main.index"))

    unique_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{safe_name}"
    upload_path = _get_upload_path()
    upload_path.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / unique_name
    file.save(file_path)

    document = Document(
        title=title,
        description=description,
        category=category,
        upload_date=upload_date,
        stored_filename=unique_name,
        original_filename=file.filename,
    )
    db.session.add(document)
    db.session.commit()

    flash("Documento guardado correctamente", "success")
    return redirect(url_for("main.index"))


@bp.route("/download/<int:document_id>")
def download(document_id: int):
    document = Document.query.get_or_404(document_id)
    return send_from_directory(
        directory=_get_upload_path(),
        path=document.stored_filename,
        as_attachment=True,
        download_name=document.original_filename,
    )


@bp.route("/reportes")
def reports() -> str:
    yearly_totals = (
        db.session.query(
            func.strftime("%Y", Document.upload_date).label("year"),
            func.count(Document.id).label("total"),
        )
        .group_by("year")
        .order_by("year")
        .all()
    )

    category_breakdown_query = (
        db.session.query(
            func.strftime("%Y", Document.upload_date).label("year"),
            Document.category,
            func.count(Document.id).label("total"),
        )
        .group_by("year", Document.category)
        .order_by("year", Document.category)
        .all()
    )

    category_breakdown: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for entry in category_breakdown_query:
        category_breakdown[entry.year].append(
            {"category": entry.category, "total": entry.total}
        )

    return render_template(
        "reports.html",
        yearly_totals=yearly_totals,
        category_breakdown=category_breakdown,
    )
