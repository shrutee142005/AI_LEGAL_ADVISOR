from app.services.embedding_services import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.legal_advisor import LegalAdvisor


class RAGPipeline:

    def __init__(self):

        # ==================================================
        # EMBEDDING SERVICE
        # ==================================================

        self.embedding_service = (
            EmbeddingService()
        )


        # ==================================================
        # VECTOR STORE
        # ==================================================

        self.vector_store = (
            VectorStore(
                dimension=384
            )
        )

        # Load latest saved FAISS index
        self.vector_store.load_index()


        # ==================================================
        # LEGAL ADVISOR
        # ==================================================

        self.legal_advisor = (
            LegalAdvisor()
        )


    # ==================================================
    # ASK
    # ==================================================

    def ask(
        self,
        question,
        user_id,
        conversation_history="",
        document_id=None
    ):

        print()
        print(
            "======================================"
        )

        print(
            "RAG PIPELINE"
        )

        print(
            "Question:",
            question
        )

        print(
            "User ID:",
            user_id
        )

        print(
            "Document ID:",
            document_id
        )

        print(
            "======================================"
        )


        # ==================================================
        # VALIDATE DOCUMENT ID
        # ==================================================

        if document_id is None:

            print(
                "No document ID provided."
            )

            return (
                "Please select a document before "
                "asking a document-related question."
            )


        # ==================================================
        # QUESTION EMBEDDING
        # ==================================================

        query_embedding = (
            self.embedding_service
            .create_embeddings(
                [question]
            )[0]
        )


        print(
            "Question embedding created."
        )


        # ==================================================
        # RELOAD LATEST VECTOR INDEX
        # ==================================================
        #
        # Important:
        #
        # PDF upload uses its own VectorStore instance.
        # The uploaded vectors are saved to disk.
        #
        # Reload here so the RAG pipeline always uses
        # the latest saved vectors.
        #
        # ==================================================

        self.vector_store.load_index()


        print(
            "Latest vector index loaded."
        )


        # ==================================================
        # DOCUMENT-SPECIFIC VECTOR SEARCH
        # ==================================================

        chunks = (
            self.vector_store.search(

                query_embedding,

                top_k=5,

                user_id=user_id,

                document_id=document_id

            )
        )


        # ==================================================
        # DEBUG RETRIEVED CHUNKS
        # ==================================================

        print()
        print(
            "========== RETRIEVED CHUNKS =========="
        )


        if not chunks:

            print(
                "No relevant chunks found."
            )


        for number, chunk in enumerate(
            chunks,
            start=1
        ):

            print()
            print(
                f"--- Chunk {number} ---"
            )

            print(
                chunk
            )


        print()
        print(
            "======================================"
        )


        # ==================================================
        # CREATE CONTEXT
        # ==================================================

        context = "\n\n".join(
            chunks
        )


        print()
        print(
            "========== CONTEXT =========="
        )

        if context:

            print(
                context
            )

        else:

            print(
                "No context available."
            )

        print(
            "============================="
        )


        # ==================================================
        # GENERATE ANSWER
        # ==================================================

        answer = (
            self.legal_advisor.generate_answer(

                question=question,

                context=context,

                conversation_history=
                    conversation_history

            )
        )


        # ==================================================
        # FINAL DEBUG
        # ==================================================

        print()
        print(
            "========== FINAL ANSWER =========="
        )

        print(
            answer
        )

        print(
            "=================================="
        )


        return answer