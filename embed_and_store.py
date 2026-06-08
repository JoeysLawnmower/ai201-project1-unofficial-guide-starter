#!/usr/bin/env python3
"""
Embedding and vector storage for CS professor reviews.
Uses: all-MiniLM-L6-v2 model, ChromaDB vector store
"""

import sys
from pathlib import Path
from typing import List, Tuple

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install sentence-transformers chromadb")
    sys.exit(1)

from process_documents import load_and_process_documents


class ReviewEmbedder:
    """Embed and store review chunks using ChromaDB and sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", db_path: str = ".claude/chroma_db"):
        """
        Initialize embedder with specified model and database.

        Args:
            model_name: HuggingFace model ID (e.g., "all-MiniLM-L6-v2")
            db_path: Path to store ChromaDB data
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)

        # Initialize ChromaDB client (new API)
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.db_path))

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="professor_reviews",
            metadata={"hnsw:space": "cosine"}
        )
        print(f"Using ChromaDB collection with {self.collection.count()} existing embeddings")

    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """
        Embed chunks using sentence-transformers.

        Args:
            chunks: List of text chunks to embed

        Returns:
            List of embedding vectors
        """
        print(f"Embedding {len(chunks)} chunks...")
        embeddings = self.model.encode(chunks, show_progress_bar=True)
        return embeddings.tolist()

    def store_chunks(self, chunks: List[str], embeddings: List[List[float]]) -> None:
        """
        Store chunks and embeddings in ChromaDB.

        Args:
            chunks: List of text chunks
            embeddings: List of embedding vectors
        """
        print(f"Storing {len(chunks)} chunks in ChromaDB...")

        # Create unique IDs for each chunk
        ids = [f"chunk_{i}" for i in range(len(chunks))]

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{"chunk_index": i} for i in range(len(chunks))]
        )

        print(f"Successfully stored {len(chunks)} chunks. Collection now has {self.collection.count()} total embeddings")

    def retrieve_chunks(self, query: str, top_k: int = 3) -> Tuple[List[str], List[float]]:
        """
        Retrieve top-k most similar chunks for a query.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            Tuple of (chunks, similarity_scores)
        """
        print(f"\nRetrieving top {top_k} chunks for query: '{query}'")

        # Embed the query
        query_embedding = self.model.encode(query).tolist()

        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        chunks = results["documents"][0]
        distances = results["distances"][0]

        # Convert distances to similarity scores (cosine distance to similarity)
        similarities = [1 - d for d in distances]

        return chunks, similarities

    def persist(self) -> None:
        """Embeddings are automatically persisted in the new ChromaDB API."""
        print(f"Embeddings automatically persisted to {self.db_path}")


def main():
    """Main pipeline: load chunks, embed, and store."""
    print("=" * 80)
    print("EMBEDDING AND STORAGE PIPELINE")
    print("=" * 80)

    # Step 1: Load and process documents
    print("\nStep 1: Loading and processing documents...")
    chunks, chunk_count = load_and_process_documents()

    if chunk_count == 0:
        print("No chunks to embed. Please run process_documents.py first.")
        return

    print(f"Loaded {chunk_count} chunks")

    # Step 2: Initialize embedder
    print("\nStep 2: Initializing embedder...")
    embedder = ReviewEmbedder(model_name="all-MiniLM-L6-v2")

    # Step 3: Embed chunks
    print("\nStep 3: Embedding chunks...")
    embeddings = embedder.embed_chunks(chunks)

    # Step 4: Store in ChromaDB
    print("\nStep 4: Storing embeddings in ChromaDB...")
    embedder.store_chunks(chunks, embeddings)

    # Step 5: Persist to disk
    print("\nStep 5: Persisting to disk...")
    embedder.persist()

    print("\n" + "=" * 80)
    print("EMBEDDING COMPLETE")
    print("=" * 80)
    print(f"✓ {chunk_count} chunks embedded and stored")
    print(f"✓ Model: all-MiniLM-L6-v2")
    print(f"✓ Database: ChromaDB at .claude/chroma_db")

    # Test retrieval with sample queries
    print("\n" + "=" * 80)
    print("TESTING RETRIEVAL")
    print("=" * 80)

    test_queries = [
        "What do students say about CS 225?",
        "Is Margaret Fleck a good professor?",
        "Are there a lot of quizzes in CS 173?",
    ]

    for query in test_queries:
        retrieved_chunks, similarities = embedder.retrieve_chunks(query, top_k=3)
        for i, (chunk, sim) in enumerate(zip(retrieved_chunks, similarities), 1):
            print(f"\n  Result {i} (similarity: {sim:.3f}):")
            # Show first 150 chars of chunk
            preview = chunk[:150] + "..." if len(chunk) > 150 else chunk
            print(f"  {preview}")


if __name__ == "__main__":
    main()
