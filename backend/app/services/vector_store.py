import os
import faiss
import numpy as np


class VectorStore:

    def __init__(self, dimension=384):

        self.dimension = dimension

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.text_chunks = []


    def add_embeddings(
        self,
        embeddings,
        chunks
    ):

        embeddings = np.array(
            embeddings
        ).astype("float32")

        self.index.add(
            embeddings
        )

        self.text_chunks.extend(
            chunks
        )


    def search(
        self,
        query_embedding,
        top_k=3
    ):

        if self.index.ntotal == 0:
            return []

        query_embedding = np.array(
            [query_embedding]
        ).astype("float32")

        distances, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for index in indices[0]:

            if (
                index != -1
                and index < len(self.text_chunks)
            ):

                results.append(
                    self.text_chunks[index]
                )

        return results


    def save_index(self):

        os.makedirs(
            "vector_db",
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            "vector_db/legal_index.faiss"
        )

        print("Vector index saved.")


    def load_index(self):

        if os.path.exists(
            "vector_db/legal_index.faiss"
        ):

            self.index = faiss.read_index(
                "vector_db/legal_index.faiss"
            )

            print("Vector index loaded.")