#!/usr/bin/env python3
"""
Example usage of the RAG system showing source attribution.
This demonstrates what happens when you query the system.
"""

from embed_and_store import ReviewEmbedder


def show_example():
    """Show an example of retrieval with source attribution."""
    print("="*80)
    print("EXAMPLE: How Source Attribution Works")
    print("="*80)

    embedder = ReviewEmbedder()

    # Example query
    query = "What do students think about the difficulty of CS 225?"

    print(f"\nQUERY: {query}\n")

    # Retrieve relevant chunks
    chunks, similarities = embedder.retrieve_chunks(query, top_k=3)

    print("="*80)
    print("RETRIEVED SOURCES (these would be sent to Groq LLM)")
    print("="*80)

    for i, (chunk, sim) in enumerate(zip(chunks, similarities), 1):
        print(f"\n[Source {i}] Similarity Score: {sim:.3f}")
        print("-" * 80)
        print(chunk)
        print("-" * 80)

    print("\n" + "="*80)
    print("SYSTEM PROMPT (ensures source-only responses)")
    print("="*80)

    system_prompt = """You are a helpful AI assistant answering questions about CS professors at UIUC based on student reviews.

CRITICAL RULES:
1. ONLY use information from the provided sources
2. Do NOT make up, infer, or hallucinate any information
3. If information is not in the sources, say "I don't have information about that"
4. Always cite which source(s) you're using for each claim
5. Use [Source N] notation to reference sources
6. Be concise and direct

Format your answer as:
- Direct answer to the question
- Each claim should be immediately followed by its source(s)
- End with a "Sources Used" section listing which sources were referenced"""

    print("\n" + system_prompt)

    print("\n" + "="*80)
    print("EXPECTED OUTPUT FORMAT (with source attribution)")
    print("="*80)

    example_output = """Based on the student reviews, here's what students think about CS 225's difficulty:

Students have mixed opinions about the difficulty. Some find it manageable with proper effort. One student noted "The course itself isn't too hard, I think with work you can get through it quite well, especially with 7% extra credit." [Source 2] This suggests the difficulty can be mitigated by taking advantage of available resources.

However, the difficulty varies depending on the coursework components. Another student mentioned that "Quizzes are [the] worst part, not bad but wish coding question on each wasn't 50% of the grade" [Source 3], indicating that while the overall difficulty is moderate, specific assignments (like quizzes) can be challenging.

The homework load contributes to difficulty perception. One review states "The homework is difficult and so are the tests. You need to know the material really well..." [Source 1], suggesting that CS 225 requires solid understanding and preparation.

Sources Used:
- Source 1: Brad Solomon CS225 review
- Source 2: Brad Solomon CS225 review
- Source 3: Brad Solomon CS225 review"""

    print(example_output)

    print("\n" + "="*80)
    print("KEY POINTS")
    print("="*80)
    print("""
✓ Each claim is immediately followed by [Source N] notation
✓ Only information from the retrieved chunks is used
✓ No inferences or assumptions beyond what students said
✓ "Sources Used" section lists all cited sources
✓ System prevents hallucination through prompt engineering
✓ Temperature=0.3 ensures consistent, factual responses
    """)


if __name__ == "__main__":
    show_example()
