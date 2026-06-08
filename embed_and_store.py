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
        Retrieve top-k most similar chunks for a query using hybrid search.
        Combines semantic similarity with keyword matching.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            Tuple of (chunks, similarity_scores)
        """
        print(f"\nRetrieving top {top_k} chunks for query: '{query}'")

        import re

        # Embed the query
        query_embedding = self.model.encode(query).tolist()

        # Get ALL chunks for keyword filtering (hybrid search)
        # Query semantically but then rerank with keywords
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.collection.count()  # Get all results for reranking
        )

        chunks = results["documents"][0]
        distances = results["distances"][0]
        similarities = [1 - d for d in distances]

        # Extract course codes and keywords from query
        courses_in_query = re.findall(r'CS\s*\d{3}', query)
        courses_in_query = [c.replace(' ', '') for c in courses_in_query]  # Normalize

        # Rerank with keyword boosting
        scored_chunks = []
        for chunk, score in zip(chunks, similarities):
            original_score = score
            boost = 0

            # STRONG boost for exact course match
            if courses_in_query:
                courses_in_chunk = re.findall(r'CS\s*\d{3}', chunk)
                courses_in_chunk = [c.replace(' ', '') for c in courses_in_chunk]
                if any(c in courses_in_chunk for c in courses_in_query):
                    boost += 1.0  # Very strong boost

            # Moderate boost for professor names in query
            query_words = query.split()
            for word in query_words:
                if len(word) > 3 and word[0].isupper():
                    if word.lower() in chunk.lower():
                        boost += 0.2

            final_score = original_score + boost
            scored_chunks.append((chunk, final_score, boost, original_score))

        # Sort by final score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        # Print debug info
        print(f"  Semantic search found these top candidates:")
        for i, (chunk, final, boost, orig) in enumerate(scored_chunks[:top_k + 3]):
            boost_str = f" +{boost:.2f}" if boost > 0 else ""
            print(f"    [{i+1}] {final:.3f}{boost_str} | {chunk[30:70]}...")

        # Return top_k
        final_chunks, final_scores, _, _ = zip(*scored_chunks[:top_k])

        return list(final_chunks), list(final_scores)

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
