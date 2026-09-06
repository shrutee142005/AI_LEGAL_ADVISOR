import os

from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from werkzeug.utils import secure_filename

from app.extensions import db

from app.models.document import Document
from app.models.document_analysis import DocumentAnalysis

from app.services.pdf_loader import (
    extract_text_from_pdf,
    split_text_into_chunks
)

from app.services.embedding_services import (
    EmbeddingService
)

from app.services.vector_store import (
    VectorStore
)

from app.services.document_analyzer import (
    DocumentAnalyzer
)


# ==================================================
# BLUEPRINT
# ==================================================

document_bp = Blueprint(
    "document",
    __name__,
    url_prefix="/api/documents"
)


# ==================================================
# CONFIGURATION
# ==================================================

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf"
}


# ==================================================
# SERVICES
# ==================================================

embedding_service = EmbeddingService()

vector_store = VectorStore(
    dimension=384
)

vector_store.load_index()

document_analyzer = DocumentAnalyzer()


# ==================================================
# FILE CHECK
# ==================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower() in ALLOWED_EXTENSIONS
    )


# ==================================================
# UPLOAD PDF
# ==================================================

@document_bp.route(
    "/upload",
    methods=["POST"]
)
@jwt_required()
def upload_document():

    try:

        # ------------------------------------------
        # CURRENT USER
        # ------------------------------------------

        current_user_id = int(
            get_jwt_identity()
        )

        print()
        print("======================================")
        print("PDF UPLOAD STARTED")
        print("USER ID:", current_user_id)
        print("======================================")


        # ------------------------------------------
        # CHECK FILE
        # ------------------------------------------

        if "file" not in request.files:

            return jsonify({
                "error": "No file uploaded"
            }), 400


        file = request.files["file"]


        # ------------------------------------------
        # CHECK FILE NAME
        # ------------------------------------------

        if not file.filename:

            return jsonify({
                "error": "No file selected"
            }), 400


        # ------------------------------------------
        # CHECK FILE TYPE
        # ------------------------------------------

        if not allowed_file(
            file.filename
        ):

            return jsonify({
                "error":
                    "Only PDF files are allowed"
            }), 400


        # ------------------------------------------
        # SECURE FILE NAME
        # ------------------------------------------

        filename = secure_filename(
            file.filename
        )


        # ------------------------------------------
        # CREATE UPLOAD FOLDER
        # ------------------------------------------

        os.makedirs(
            UPLOAD_FOLDER,
            exist_ok=True
        )


        # ------------------------------------------
        # FILE PATH
        # ------------------------------------------

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )


        # ------------------------------------------
        # SAVE PDF
        # ------------------------------------------

        file.save(
            file_path
        )

        print(
            "PDF saved:",
            file_path
        )


        # ==================================================
        # EXTRACT TEXT
        # ==================================================

        print()
        print(
            "======================================"
        )
        print(
            "EXTRACTING PDF TEXT"
        )
        print(
            "======================================"
        )


        text = extract_text_from_pdf(
            file_path
        )


        # ------------------------------------------
        # CHECK EXTRACTED TEXT
        # ------------------------------------------

        if not text or not text.strip():

            if os.path.exists(
                file_path
            ):

                os.remove(
                    file_path
                )


            return jsonify({
                "error":
                    "No text could be extracted from PDF"
            }), 400


        print(
            "PDF text extracted successfully"
        )

        print(
            "Extracted characters:",
            len(text)
        )


        # ==================================================
        # SAVE DOCUMENT
        # ==================================================

        document = Document(

            user_id=current_user_id,

            filename=filename,

            file_path=file_path,

            extracted_text=text

        )


        db.session.add(
            document
        )

        db.session.commit()


        print(
            "Document saved in database"
        )

        print(
            "Document ID:",
            document.id
        )


        # ==================================================
        # AI DOCUMENT ANALYSIS
        # ==================================================

        print()
        print(
            "======================================"
        )

        print(
            "GENERATING AI DOCUMENT ANALYSIS"
        )

        print(
            "======================================"
        )


        analysis_result = (
            document_analyzer.analyze(
                text
            )
        )


        print(
            "AI document analysis generated"
        )


        print()
        print(
            "========== DOCUMENT ANALYSIS =========="
        )

        print(
            analysis_result
        )

        print(
            "========================================"
        )


        # ==================================================
        # CHECK ANALYSIS RESULT
        # ==================================================

        if not isinstance(
            analysis_result,
            dict
        ):

            raise ValueError(
                "Document analyzer must return "
                "a dictionary."
            )


        # ==================================================
        # GET ANALYSIS FIELDS
        # ==================================================

        summary = (
            analysis_result.get(
                "summary",
                ""
            )
        )


        important_points = (
            analysis_result.get(
                "important_points",
                []
            )
        )


        key_topics = (
            analysis_result.get(
                "key_topics",
                []
            )
        )


        # ------------------------------------------
        # MAKE SURE LISTS ARE LISTS
        # ------------------------------------------

        if not isinstance(
            important_points,
            list
        ):

            important_points = [
                str(important_points)
            ]


        if not isinstance(
            key_topics,
            list
        ):

            key_topics = [
                str(key_topics)
            ]


        # ==================================================
        # SAVE DOCUMENT ANALYSIS
        # ==================================================

        analysis = DocumentAnalysis(

            document_id=document.id,

            summary=str(
                summary
            ),

            important_points="\n".join(
                str(point)
                for point in important_points
            ),

            key_topics="\n".join(
                str(topic)
                for topic in key_topics
            )

        )


        db.session.add(
            analysis
        )

        db.session.commit()


        print(
            "Document analysis saved"
        )


        # ==================================================
        # SPLIT TEXT INTO CHUNKS
        # ==================================================

        chunks = split_text_into_chunks(
            text
        )


        print(
            "Total chunks:",
            len(chunks)
        )


        if not chunks:

            return jsonify({
                "error":
                    "Could not create text chunks"
            }), 400


        # ==================================================
        # CREATE EMBEDDINGS
        # ==================================================

        embeddings = (
            embedding_service.create_embeddings(
                chunks
            )
        )


        print(
            "Embeddings created successfully"
        )


        # ==================================================
        # ADD TO VECTOR STORE
        # ==================================================

        vector_store.add_embeddings(

            embeddings,

            chunks,

            document_id=document.id,

            user_id=current_user_id

        )


        print(
            "Vectors added to vector store"
        )


        # ==================================================
        # SAVE VECTOR INDEX
        # ==================================================

        vector_store.save_index()


        print(
            "Vector index saved"
        )


        # ==================================================
        # FINAL RESPONSE
        # ==================================================

        print()
        print(
            "======================================"
        )

        print(
            "PDF PROCESSING COMPLETED"
        )

        print(
            "DOCUMENT ID:",
            document.id
        )

        print(
            "======================================"
        )


        return jsonify({

            "message":
                "PDF uploaded and analyzed successfully",

            "filename":
                filename,

            "document_id":
                document.id,

            "user_id":
                current_user_id,

            "chunks":
                len(chunks),

            "text_length":
                len(text),

            "analysis": {

                "summary":
                    summary,

                "important_points":
                    important_points,

                "key_topics":
                    key_topics

            }

        }), 201


    except Exception as e:

        db.session.rollback()

        import traceback

        traceback.print_exc()


        return jsonify({

            "error":
                str(e)

        }), 500


# ==================================================
# GET ALL DOCUMENTS
# ==================================================

@document_bp.route(
    "",
    methods=["GET"]
)
@jwt_required()
def get_documents():

    try:

        current_user_id = int(
            get_jwt_identity()
        )


        documents = (
            Document.query
            .filter_by(
                user_id=current_user_id
            )
            .order_by(
                Document.uploaded_at.desc()
            )
            .all()
        )


        result = []


        for document in documents:

            analysis = (
                DocumentAnalysis.query
                .filter_by(
                    document_id=document.id
                )
                .first()
            )


            result.append({

                "id":
                    document.id,

                "filename":
                    document.filename,

                "file_path":
                    document.file_path,

                "uploaded_at":
                    document.uploaded_at.isoformat(),

                "analysis": {

                    "summary":
                        analysis.summary
                        if analysis
                        else "",

                    "important_points":
                        analysis.important_points.split(
                            "\n"
                        )
                        if (
                            analysis
                            and
                            analysis.important_points
                        )
                        else [],

                    "key_topics":
                        analysis.key_topics.split(
                            "\n"
                        )
                        if (
                            analysis
                            and
                            analysis.key_topics
                        )
                        else []

                }

            })


        return jsonify({

            "documents":
                result

        }), 200


    except Exception as e:

        import traceback

        traceback.print_exc()


        return jsonify({

            "error":
                str(e)

        }), 500


# ==================================================
# GET SINGLE DOCUMENT
# ==================================================

@document_bp.route(
    "/<int:document_id>",
    methods=["GET"]
)
@jwt_required()
def get_document(document_id):

    try:

        current_user_id = int(
            get_jwt_identity()
        )


        document = (
            Document.query
            .filter_by(

                id=document_id,

                user_id=current_user_id

            )
            .first()
        )


        if not document:

            return jsonify({

                "error":
                    "Document not found"

            }), 404


        analysis = (
            DocumentAnalysis.query
            .filter_by(
                document_id=document.id
            )
            .first()
        )


        return jsonify({

            "document": {

                "id":
                    document.id,

                "filename":
                    document.filename,

                "file_path":
                    document.file_path,

                "extracted_text":
                    document.extracted_text,

                "uploaded_at":
                    document.uploaded_at.isoformat(),

                "analysis": {

                    "summary":
                        analysis.summary
                        if analysis
                        else "",

                    "important_points":
                        analysis.important_points.split(
                            "\n"
                        )
                        if (
                            analysis
                            and
                            analysis.important_points
                        )
                        else [],

                    "key_topics":
                        analysis.key_topics.split(
                            "\n"
                        )
                        if (
                            analysis
                            and
                            analysis.key_topics
                        )
                        else []

                }

            }

        }), 200


    except Exception as e:

        import traceback

        traceback.print_exc()


        return jsonify({

            "error":
                str(e)

        }), 500


# ==================================================
# DELETE DOCUMENT
# ==================================================

@document_bp.route(
    "/<int:document_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_document(document_id):

    try:

        current_user_id = int(
            get_jwt_identity()
        )


        # ------------------------------------------
        # FIND DOCUMENT
        # ------------------------------------------

        document = (
            Document.query
            .filter_by(

                id=document_id,

                user_id=current_user_id

            )
            .first()
        )


        if not document:

            return jsonify({

                "error":
                    "Document not found"

            }), 404


        # ------------------------------------------
        # DELETE VECTOR DATA
        # ------------------------------------------

        deleted_chunks = (
            vector_store.delete_document(
                document.id
            )
        )


        # ------------------------------------------
        # DELETE ANALYSIS
        # ------------------------------------------

        analysis = (
            DocumentAnalysis.query
            .filter_by(
                document_id=document.id
            )
            .first()
        )


        if analysis:

            db.session.delete(
                analysis
            )


        # ------------------------------------------
        # DELETE PHYSICAL PDF
        # ------------------------------------------

        if os.path.exists(
            document.file_path
        ):

            os.remove(
                document.file_path
            )


        # ------------------------------------------
        # DELETE DOCUMENT
        # ------------------------------------------

        db.session.delete(
            document
        )

        db.session.commit()


        # ------------------------------------------
        # RESPONSE
        # ------------------------------------------

        return jsonify({

            "message":
                "Document deleted successfully",

            "document_id":
                document_id,

            "deleted_chunks":
                deleted_chunks

        }), 200


    except Exception as e:

        db.session.rollback()

        import traceback

        traceback.print_exc()


        return jsonify({

            "error":
                str(e)

        }), 500