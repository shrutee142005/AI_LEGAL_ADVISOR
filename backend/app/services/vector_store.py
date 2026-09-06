import os
import pickle

import faiss
import numpy as np


class VectorStore:

    def __init__(self, dimension=384):

        self.dimension = dimension

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.text_chunks = []

        self.metadata = []


    # ==================================================
    # ADD EMBEDDINGS
    # ==================================================

    def add_embeddings(
        self,
        embeddings,
        chunks,
        document_id=None,
        user_id=None
    ):

        if not chunks:
            return

        embeddings = np.array(
            embeddings
        ).astype("float32")


        if len(embeddings) != len(chunks):

            raise ValueError(
                "Number of embeddings must match number of chunks."
            )


        self.index.add(
            embeddings
        )


        self.text_chunks.extend(
            chunks
        )


        for _ in chunks:

            self.metadata.append({

                "document_id":
                    document_id,

                "user_id":
                    user_id

            })


        print(
            f"Added {len(chunks)} chunks "
            f"for document {document_id}"
        )


    # ==================================================
    # SEARCH
    # ==================================================

    def search(
        self,
        query_embedding,
        top_k=5,
        user_id=None,
        document_id=None
    ):

        if self.index.ntotal == 0:

            return []


        query_embedding = np.array(
            [query_embedding]
        ).astype("float32")


        # ------------------------------------------------
        # Search all vectors first
        # ------------------------------------------------

        distances, indices = self.index.search(
            query_embedding,
            self.index.ntotal
        )


        results = []


        for index in indices[0]:

            if index == -1:
                continue


            if index >= len(self.text_chunks):
                continue


            # ------------------------------------------------
            # Metadata
            # ------------------------------------------------

            if index >= len(self.metadata):
                continue


            metadata = self.metadata[index]


            # ------------------------------------------------
            # USER FILTER
            # ------------------------------------------------

            if user_id is not None:

                if metadata.get("user_id") != user_id:
                    continue


            # ------------------------------------------------
            # DOCUMENT FILTER
            # ------------------------------------------------

            if document_id is not None:

                if metadata.get("document_id") != document_id:
                    continue


            # ------------------------------------------------
            # Add result
            # ------------------------------------------------

            results.append(
                self.text_chunks[index]
            )


            if len(results) >= top_k:

                break


        print(
            "\n========== VECTOR SEARCH =========="
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
            "Results:",
            len(results)
        )

        print(
            "===================================\n"
        )


        return results


    # ==================================================
    # SAVE INDEX
    # ==================================================

    def save_index(self):

        os.makedirs(
            "vector_db",
            exist_ok=True
        )


        faiss.write_index(
            self.index,
            "vector_db/legal_index.faiss"
        )


        with open(
            "vector_db/text_chunks.pkl",
            "wb"
        ) as f:

            pickle.dump(
                self.text_chunks,
                f
            )


        with open(
            "vector_db/metadata.pkl",
            "wb"
        ) as f:

            pickle.dump(
                self.metadata,
                f
            )


        print(
            "Vector index and metadata saved."
        )


    # ==================================================
    # LOAD INDEX
    # ==================================================

    def load_index(self):

        index_path = (
            "vector_db/legal_index.faiss"
        )

        chunks_path = (
            "vector_db/text_chunks.pkl"
        )

        metadata_path = (
            "vector_db/metadata.pkl"
        )


        if not os.path.exists(index_path):

            print(
                "No vector index found."
            )

            return


        self.index = faiss.read_index(
            index_path
        )


        if os.path.exists(chunks_path):

            with open(
                chunks_path,
                "rb"
            ) as f:

                self.text_chunks = pickle.load(
                    f
                )


        if os.path.exists(metadata_path):

            with open(
                metadata_path,
                "rb"
            ) as f:

                self.metadata = pickle.load(
                    f
                )

        else:

            self.metadata = [

                {
                    "document_id": None,
                    "user_id": None
                }

                for _ in self.text_chunks

            ]


        print(
            "Vector index loaded."
        )

        print(
            "Text chunks loaded:",
            len(self.text_chunks)
        )

        print(
            "Metadata loaded:",
            len(self.metadata)
        )

        for i, metadata in enumerate(self.metadata):
             print(
        "VECTOR",
        i,
        "DOCUMENT:",
        metadata.get("document_id"),
        "USER:",
        metadata.get("user_id")
    )


    # ==================================================
    # DELETE DOCUMENT
    # ==================================================

    def delete_document(
        self,
        document_id
    ):

        indexes_to_remove = []


        # ------------------------------------------------
        # Find document vectors
        # ------------------------------------------------

        for index, metadata in enumerate(
            self.metadata
        ):

            if metadata.get(
                "document_id"
            ) == document_id:

                indexes_to_remove.append(
                    index
                )


        if not indexes_to_remove:

            print(
                "No vectors found for document:",
                document_id
            )

            return 0


        # ------------------------------------------------
        # Remove from FAISS
        # ------------------------------------------------

        selector = faiss.IDSelectorBatch(
            np.array(
                indexes_to_remove,
                dtype=np.int64
            )
        )


        self.index.remove_ids(
            selector
        )


        # ------------------------------------------------
        # Remove chunks
        # ------------------------------------------------

        indexes_to_remove_set = set(
            indexes_to_remove
        )


        self.text_chunks = [

            chunk

            for index, chunk
            in enumerate(
                self.text_chunks
            )

            if index not in indexes_to_remove_set

        ]


        # ------------------------------------------------
        # Remove metadata
        # ------------------------------------------------

        self.metadata = [

            metadata

            for index, metadata
            in enumerate(
                self.metadata
            )

            if index not in indexes_to_remove_set

        ]


        # ------------------------------------------------
        # Save
        # ------------------------------------------------

        self.save_index()


        print(
            "Deleted vectors for document:",
            document_id
        )


        return len(
            indexes_to_remove
        )