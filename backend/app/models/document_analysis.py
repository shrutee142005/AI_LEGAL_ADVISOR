from app.extensions import db
from datetime import datetime


class DocumentAnalysis(db.Model):

    __tablename__ = "document_analysis"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=False,
        unique=True
    )

    summary = db.Column(
        db.Text,
        nullable=True
    )

    important_points = db.Column(
        db.Text,
        nullable=True
    )

    key_topics = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    document = db.relationship(
        "Document",
        backref=db.backref(
            "analysis",
            uselist=False
        )
    )