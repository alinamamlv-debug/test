from __future__ import annotations

from datetime import datetime

from .database import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Protocol(db.Model, TimestampMixin):
    __tablename__ = "protocols"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    meeting_date = db.Column(db.Date, nullable=False)
    participants = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    body = db.Column(db.Text, nullable=False)

    decisions = db.relationship(
        "Decision", back_populates="protocol", cascade="all, delete-orphan"
    )
    assignments = db.relationship(
        "Assignment", back_populates="protocol", cascade="all, delete-orphan"
    )
    corrections = db.relationship(
        "Correction", back_populates="protocol", cascade="all, delete-orphan"
    )


class Decision(db.Model, TimestampMixin):
    __tablename__ = "decisions"

    id = db.Column(db.Integer, primary_key=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey("protocols.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)

    protocol = db.relationship("Protocol", back_populates="decisions")


class Assignment(db.Model, TimestampMixin):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey("protocols.id"), nullable=False)
    responsible = db.Column(db.String(255), nullable=True)
    text = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    protocol = db.relationship("Protocol", back_populates="assignments")


class Correction(db.Model, TimestampMixin):
    __tablename__ = "corrections"

    id = db.Column(db.Integer, primary_key=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey("protocols.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)

    protocol = db.relationship("Protocol", back_populates="corrections")
