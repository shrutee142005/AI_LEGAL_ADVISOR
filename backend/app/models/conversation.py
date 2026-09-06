from app.extensions import db
from datetime import datetime


class Conversation(db.Model):

    __tablename__ = "conversations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=True
    )

    title = db.Column(
        db.String(200),
        nullable=False,
        default="New Conversation"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    messages = db.relationship(
        "Message",
        backref="conversation",
        lazy=True,
        cascade="all, delete-orphan"
    )