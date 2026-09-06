from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from app.extensions import db

from app.models.conversation import Conversation
from app.models.message import Message

from app.services.rag_pipleline import RAGPipeline


# ==================================================
# RAG PIPELINE
# ==================================================

rag_pipeline = RAGPipeline()


# ==================================================
# BLUEPRINT
# ==================================================

chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/api/chat"
)


# ==================================================
# CREATE CONVERSATION
# ==================================================

@chat_bp.route(
    "/conversations",
    methods=["POST"]
)
@jwt_required()
def create_conversation():

    try:

        current_user_id = int(
            get_jwt_identity()
        )

        data = request.get_json() or {}

        title = data.get(
            "title",
            "New Conversation"
        )

        new_conversation = Conversation(
            user_id=current_user_id,
            title=title
        )

        db.session.add(
            new_conversation
        )

        db.session.commit()

        return jsonify({

            "message":
                "Conversation created successfully",

            "conversation": {

                "id":
                    new_conversation.id,

                "title":
                    new_conversation.title,

                "user_id":
                    new_conversation.user_id

            }

        }), 201


    except Exception as e:

        db.session.rollback()

        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500


# ==================================================
# GET CONVERSATIONS
# ==================================================

@chat_bp.route(
    "/conversations",
    methods=["GET"]
)
@jwt_required()
def get_conversations():

    try:

        current_user_id = int(
            get_jwt_identity()
        )

        conversations = (
            Conversation.query
            .filter_by(
                user_id=current_user_id
            )
            .order_by(
                Conversation.created_at.desc()
            )
            .all()
        )

        return jsonify({

            "conversations": [

                {

                    "id":
                        conversation.id,

                    "title":
                        conversation.title,

                    "user_id":
                        conversation.user_id,

                    "created_at":
                        conversation.created_at.isoformat()

                }

                for conversation
                in conversations

            ]

        }), 200


    except Exception as e:

        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500


# ==================================================
# ADD MESSAGE
# ==================================================

@chat_bp.route(
    "/conversations/<int:conversation_id>/messages",
    methods=["POST"]
)
@jwt_required()
def add_message(conversation_id):

    try:

        current_user_id = int(
            get_jwt_identity()
        )

        data = request.get_json() or {}

        content = data.get(
            "content"
        )


        if not content:

            return jsonify({
                "error":
                    "Message content is required"
            }), 400


        conversation = (
            Conversation.query
            .filter_by(
                id=conversation_id,
                user_id=current_user_id
            )
            .first()
        )


        if not conversation:

            return jsonify({
                "error":
                    "Conversation not found"
            }), 404


        new_message = Message(

            conversation_id=
                conversation_id,

            role="user",

            content=content

        )


        db.session.add(
            new_message
        )

        db.session.commit()


        return jsonify({

            "message":
                "Message saved successfully",

            "data": {

                "id":
                    new_message.id,

                "conversation_id":
                    new_message.conversation_id,

                "role":
                    new_message.role,

                "content":
                    new_message.content

            }

        }), 201


    except Exception as e:

        db.session.rollback()

        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500


# ==================================================
# GET MESSAGES
# ==================================================

@chat_bp.route(
    "/conversations/<int:conversation_id>/messages",
    methods=["GET"]
)
@jwt_required()
def get_messages(conversation_id):

    try:

        current_user_id = int(
            get_jwt_identity()
        )


        conversation = (
            Conversation.query
            .filter_by(
                id=conversation_id,
                user_id=current_user_id
            )
            .first()
        )


        if not conversation:

            return jsonify({
                "error":
                    "Conversation not found"
            }), 404


        messages = (
            Message.query
            .filter_by(
                conversation_id=conversation_id
            )
            .order_by(
                Message.created_at.asc()
            )
            .all()
        )


        return jsonify({

            "conversation_id":
                conversation_id,

            "messages": [

                {

                    "id":
                        message.id,

                    "role":
                        message.role,

                    "content":
                        message.content,

                    "created_at":
                        message.created_at.isoformat()

                }

                for message in messages

            ]

        }), 200


    except Exception as e:

        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500



# ==================================================
# DELETE CONVERSATION
# ==================================================

@chat_bp.route(
    "/conversations/<int:conversation_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_conversation(conversation_id):

    try:

        current_user_id = int(
            get_jwt_identity()
        )

        # ==========================================
        # CHECK OWNERSHIP
        # ==========================================

        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user_id
        ).first()

        if not conversation:

            return jsonify({
                "error": "Conversation not found"
            }), 404

        # ==========================================
        # DELETE CONVERSATION
        # ==========================================
        #
        # Conversation model already has:
        #
        # cascade="all, delete-orphan"
        #
        # Therefore associated messages will also
        # be deleted.
        #

        db.session.delete(conversation)

        db.session.commit()

        return jsonify({
            "message": "Conversation deleted successfully",
            "conversation_id": conversation_id
        }), 200

    except Exception as e:

        db.session.rollback()

        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500    


# ==================================================
# ASK QUESTION
# ==================================================

@chat_bp.route(
    "/ask",
    methods=["POST"]
)
@jwt_required()
def ask_question():

    try:

        current_user_id = int(
            get_jwt_identity()
        )


        data = request.get_json() or {}


        question = data.get(
            "question"
        )


        conversation_id = data.get(
            "conversation_id"
        )


        document_id = data.get(
            "document_id"
        )


        print("\n")
        print(
            "======================================"
        )

        print(
            "CHAT ASK"
        )

        print(
            "USER ID:",
            current_user_id
        )

        print(
            "CONVERSATION ID:",
            conversation_id
        )

        print(
            "DOCUMENT ID:",
            document_id
        )

        print(
            "QUESTION:",
            question
        )

        print(
            "======================================"
        )


        # ==================================================
        # VALIDATION
        # ==================================================

        if not question:

            return jsonify({
                "error":
                    "Question is required"
            }), 400


        if not conversation_id:

            return jsonify({
                "error":
                    "conversation_id is required"
            }), 400


        if not document_id:

            return jsonify({
                "error":
                    "document_id is required"
            }), 400


        try:

            document_id = int(
                document_id
            )

        except (TypeError, ValueError):

            return jsonify({
                "error":
                    "Invalid document_id"
            }), 400


        # ==================================================
        # CONVERSATION OWNERSHIP
        # ==================================================

        conversation = (
            Conversation.query
            .filter_by(
                id=conversation_id,
                user_id=current_user_id
            )
            .first()
        )


        if not conversation:

            return jsonify({
                "error":
                    "Conversation not found"
            }), 404


        # ==================================================
        # SAVE USER MESSAGE
        # ==================================================

        user_message = Message(

            conversation_id=
                conversation_id,

            role="user",

            content=question

        )


        db.session.add(
            user_message
        )

        db.session.commit()


        # ==================================================
        # CONVERSATION HISTORY
        # ==================================================

        previous_messages = (
            Message.query
            .filter_by(
                conversation_id=conversation_id
            )
            .order_by(
                Message.created_at.asc()
            )
            .all()
        )


        conversation_history_parts = []


        for message in previous_messages:

            conversation_history_parts.append(

                f"{message.role}: "
                f"{message.content}"

            )


        conversation_history = "\n".join(
            conversation_history_parts
        )


        # ==================================================
        # RAG
        # ==================================================

        answer = rag_pipeline.ask(

            question=question,

            user_id=current_user_id,

            conversation_history=
                conversation_history,

            document_id=document_id

        )


        # ==================================================
        # SAVE AI MESSAGE
        # ==================================================

        ai_message = Message(

            conversation_id=
                conversation_id,

            role="assistant",

            content=answer

        )


        db.session.add(
            ai_message
        )

        db.session.commit()


        # ==================================================
        # RESPONSE
        # ==================================================

        return jsonify({

            "conversation_id":
                conversation_id,

            "document_id":
                document_id,

            "question":
                question,

            "answer":
                answer

        }), 200


    except Exception as e:

        db.session.rollback()

        import traceback
        traceback.print_exc()

        return jsonify({

            "error":
                str(e)

        }), 500