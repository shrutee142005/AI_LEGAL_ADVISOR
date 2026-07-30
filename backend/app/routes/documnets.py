import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

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


document_bp = Blueprint(
    "document",
    __name__
)


UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf"
}


embedding_service = EmbeddingService()


vector_store = VectorStore(
    dimension=384
)

vector_store.load_index()


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower() in ALLOWED_EXTENSIONS
    )


@document_bp.route(
    "/upload",
    methods=["POST"]
)
@jwt_required()
def upload_document():

    if "file" not in request.files:

        return jsonify({
            "error": "No file uploaded"
        }), 400


    file = request.files["file"]


    if file.filename == "":

        return jsonify({
            "error": "No file selected"
        }), 400


    if not allowed_file(
        file.filename
    ):

        return jsonify({
            "error": "Only PDF files are allowed"
        }), 400


    filename = secure_filename(
        file.filename
    )


    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )


    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    file.save(
        file_path
    )


    # PDF se text extract karna

    text = extract_text_from_pdf(
        file_path
    )


    # Text ko chunks me divide karna

    chunks = split_text_into_chunks(
        text
    )


    print(
        "Total chunks:",
        len(chunks)
    )


    # Chunks ke embeddings create karna

    embeddings = embedding_service.create_embeddings(
        chunks
    )


    print(
        "Embeddings created successfully"
    )


    # Embeddings ko vector store me add karna

    vector_store.add_embeddings(
        embeddings,
        chunks
    )

    vector_store.save_index()


    print(
        "Vectors added to vector store"
    )


    return jsonify({

        "message": "PDF uploaded and processed successfully",

        "filename": filename,

        "chunks": len(chunks)

    }), 201
    