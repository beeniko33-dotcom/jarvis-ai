import chromadb
from chromadb.utils import embedding_functions
import os
from datetime import datetime

class VectorMemory:
    def __init__(self, persist_dir="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection("jarvis_memory")

    def add(self, text: str, metadata=None):
        if metadata is None:
            metadata = {"timestamp": datetime.now().isoformat()}
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[str(hash(text))]
        )

    def query(self, query_text: str, n_results=5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results.get('documents', [[]])[0]
