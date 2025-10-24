from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .database import db
from .models import Assignment, Correction, Decision, Protocol
from .neural_analysis import MockNeuralAnalyzer

bp = Blueprint("protocols", __name__)


def _get_analyzer() -> MockNeuralAnalyzer:
    return MockNeuralAnalyzer()


@bp.route("/")
def index():
    protocols = Protocol.query.order_by(Protocol.meeting_date.desc()).all()
    return render_template("index.html", protocols=protocols)


@bp.route("/protocol/new", methods=["GET", "POST"])
def create_protocol():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date_str = request.form.get("meeting_date", "").strip()
        participants = request.form.get("participants", "").strip()
        summary = request.form.get("summary", "").strip()
        body = request.form.get("body", "").strip()

        if not title or not body or not date_str:
            flash("Название, дата и текст протокола обязательны.", "error")
            return render_template("create_protocol.html")

        try:
            meeting_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Некорректный формат даты. Используйте YYYY-MM-DD.", "error")
            return render_template("create_protocol.html")

        protocol = Protocol(
            title=title,
            meeting_date=meeting_date,
            participants=participants or None,
            summary=summary or None,
            body=body,
        )
        db.session.add(protocol)
        db.session.commit()

        _run_analysis(protocol)
        flash("Протокол сохранен и проанализирован.", "success")
        return redirect(url_for("protocols.view_protocol", protocol_id=protocol.id))

    return render_template("create_protocol.html")


@bp.route("/protocol/<int:protocol_id>")
def view_protocol(protocol_id: int):
    protocol = Protocol.query.get_or_404(protocol_id)
    return render_template("protocol_detail.html", protocol=protocol)


@bp.route("/protocol/<int:protocol_id>/reanalyze", methods=["POST"])
def reanalyze(protocol_id: int):
    protocol = Protocol.query.get_or_404(protocol_id)
    clear_analysis(protocol)
    _run_analysis(protocol)
    flash("Анализ обновлен.", "success")
    return redirect(url_for("protocols.view_protocol", protocol_id=protocol.id))


@bp.route("/assignments/<int:assignment_id>/toggle", methods=["POST"])
def toggle_assignment(assignment_id: int):
    assignment = Assignment.query.get_or_404(assignment_id)
    assignment.completed = not assignment.completed
    db.session.commit()
    flash("Статус поручения обновлён.", "success")
    return redirect(url_for("protocols.view_protocol", protocol_id=assignment.protocol_id))


def _run_analysis(protocol: Protocol) -> None:
    analyzer = _get_analyzer()
    result = analyzer.analyze(protocol.body)

    for decision_text in result.decisions:
        db.session.add(Decision(protocol=protocol, text=decision_text))

    for responsible, text, due in result.assignments:
        db.session.add(
            Assignment(
                protocol=protocol,
                responsible=responsible,
                text=text,
                due_date=due.date() if due else None,
            )
        )

    for correction_text in result.corrections:
        db.session.add(Correction(protocol=protocol, text=correction_text))

    db.session.commit()


def clear_analysis(protocol: Protocol) -> None:
    Assignment.query.filter_by(protocol_id=protocol.id).delete()
    Decision.query.filter_by(protocol_id=protocol.id).delete()
    Correction.query.filter_by(protocol_id=protocol.id).delete()
    db.session.commit()
