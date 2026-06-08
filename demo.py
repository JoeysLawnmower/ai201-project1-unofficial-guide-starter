#!/usr/bin/env python3
"""
Demo script for CS Professor Review RAG System.
Shows the complete pipeline end-to-end without requiring API key.
"""

from embed_and_store import ReviewEmbedder
from process_documents import load_and_process_documents


def demo_retrieval():
    """Demonstrate the retrieval system without generation."""
    print("="*80)
    print("CS PROFESSOR REVIEW SYSTEM - RETRIEVAL DEMO")
    print("="*80)
    print("\nThis demo shows document processing and retrieval without needing an API key.")
    print("To enable generation with source attribution, set: export GROQ_API_KEY='...'")

    # Load embedder and test queries
    print("\n" + "="*80)
    print("LOADING VECTOR DATABASE")
    print("="*80)

    embedder = ReviewEmbedder()

    # Sample queries to demonstrate retrieval
    test_queries = [
        "What do students say about CS 225?",
        "Is Margaret Fleck a good professor?",
        "Are there a lot of quizzes in CS 173?",
        "What's the difficulty level of algorithms courses?",
        "Which professors give extra credit?",
    ]

    print(f"\nVector database loaded with {embedder.collection.count()} embeddings\n")

    # Test each query
    for i, query in enumerate(test_queries, 1):
        print("="*80)
        print(f"QUERY {i}: {query}")
        print("="*80)

        # Retrieve top 3
        retrieved_chunks, similarities = embedder.retrieve_chunks(query, top_k=3)

        print(f"\nTop 3 Retrieved Chunks (by cosine similarity):\n")

        for j, (chunk, sim) in enumerate(zip(retrieved_chunks, similarities), 1):
            print(f"[Source {j}] Similarity: {sim:.3f}")
            print("-" * 80)
            print(chunk)
            print("-" * 80)
            print()

        input("Press Enter to continue to next query...")
        print("\n")

    print("="*80)
    print("DEMO COMPLETE")
    print("="*80)
    print("\nTo generate answers with source attribution:")
    print("  1. Get API key: https://console.groq.com/keys")
    print("  2. Set key: export GROQ_API_KEY='your-key'")
    print("  3. Run: python3 generate_answers.py --query 'Your question?'")


def show_document_stats():
    """Show document processing statistics."""
    print("\n" + "="*80)
    print("DOCUMENT PROCESSING STATISTICS")
    print("="*80)

    chunks, count = load_and_process_documents()

    print(f"\n✓ Total chunks processed: {count}")
    print(f"✓ Chunk size: 300 characters")
    print(f"✓ Chunk overlap: 75 characters")
    print(f"✓ Embedding model: all-MiniLM-L6-v2 (384-dim)")
    print(f"✓ Vector database: ChromaDB at .claude/chroma_db/")

    print(f"\nSample chunks:")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n  [{i}] {chunk[:120]}...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        show_document_stats()
    else:
        demo_retrieval()
