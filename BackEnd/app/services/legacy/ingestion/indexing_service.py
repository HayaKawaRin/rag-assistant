# from pathlib import Path

# import faiss
# import numpy as np


# class IndexingService:
#     def __init__(self, index_path: str = "storage/faiss/documents.index"):
#         self.index_path = Path(index_path)
#         self.index_path.parent.mkdir(parents=True, exist_ok=True)
#         self.index = None
#         self.dimension = None
#         self.load_index()

#     def create_index(self, dimension: int) -> None:
#         base_index = faiss.IndexFlatIP(dimension)
#         self.index = faiss.IndexIDMap(base_index)
#         self.dimension = dimension

#     def load_index(self) -> None:
#         if self.index_path.exists():
#             self.index = faiss.read_index(str(self.index_path))
#             self.dimension = self.index.d
#         else:
#             self.index = None
#             self.dimension = None

#     def save_index(self) -> None:
#         if self.index is not None:
#             faiss.write_index(self.index, str(self.index_path))

#     def add_embeddings(self, embeddings: list[list[float]], chunk_ids: list[int]) -> None:
#         if not embeddings:
#             return

#         vectors = np.array(embeddings, dtype="float32")
#         ids = np.array(chunk_ids, dtype="int64")

#         if self.index is None:
#             self.create_index(vectors.shape[1])

#         if vectors.shape[1] != self.dimension:
#             raise ValueError(
#                 f"Embedding dimension mismatch: expected {self.dimension}, got {vectors.shape[1]}"
#             )

#         faiss.normalize_L2(vectors)
#         self.index.add_with_ids(vectors, ids)
#         self.save_index()

#     def remove_embeddings(self, chunk_ids: list[int]) -> int:
#         if self.index is None or not chunk_ids:
#             return 0

#         ids = np.array(chunk_ids, dtype="int64")
#         removed_count = self.index.remove_ids(ids)
#         self.save_index()
#         return int(removed_count)


# indexing_service = IndexingService()