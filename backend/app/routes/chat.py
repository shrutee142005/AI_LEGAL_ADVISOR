from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.conversation import Conversation
from app.models.message import Message
from app.routes.documnets import(embedding_service,vector_store)

chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/api/chat"
)


@chat_bp.route("/conversations", methods=["POST"])
@jwt_required()
def create_conversation():

    current_user_id = get_jwt_identity()

    data = request.get_json() or {}

    title = data.get(
        "title",
        "New Conversation"
    )

    new_conversation = Conversation(
        user_id=int(current_user_id),
        title=title
    )

    db.session.add(new_conversation)
    db.session.commit()

    return jsonify({
        "message": "Conversation created successfully",
        "conversation": {
            "id": new_conversation.id,
            "title": new_conversation.title,
            "user_id": new_conversation.user_id
        }
    }), 201

@chat_bp.route(
    "/conversations/<int:conversation_id>/messages",
    methods=["POST"]
)
@jwt_required()
def add_message(conversation_id):

    current_user_id = int(get_jwt_identity())

    data = request.get_json() or {}
    content = data.get("content")

    if not content:
        return jsonify({
            "error": "Message content is required"
        }), 400

    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user_id
    ).first()

    if not conversation:
        return jsonify({
            "error": "Conversation not found"
        }), 404

    new_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=content
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify({
        "message": "Message saved successfully",
        "data": {
            "id": new_message.id,
            "conversation_id": new_message.conversation_id,
            "role": new_message.role,
            "content": new_message.content
        }
    }), 201

@chat_bp.route(
    "/conversations/<int:conversation_id>/messages",
    methods=["GET"]
)
@jwt_required()
def get_messages(conversation_id):

    current_user_id = int(get_jwt_identity())

    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user_id
    ).first()

    if not conversation:
        return jsonify({
            "error": "Conversation not found"
        }), 404

    messages = Message.query.filter_by(
        conversation_id=conversation_id
    ).order_by(
        Message.created_at.asc()
    ).all()

    return jsonify({
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat()
            }
            for message in messages
        ]
    }), 200

@chat_bp.route("/ask", methods=["POST"])
@jwt_required()
def ask_question():

    data = request.get_json() or {}

    question = data.get("question")

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    query_embedding = embedding_service.create_embeddings(
        [question]
    )[0]

    results = vector_store.search(
        query_embedding,
        top_k=3
    )

    return jsonify({
        "question": question,
        "relevant_chunks": results
    }), 200