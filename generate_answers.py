#!/usr/bin/env python3
"""
Generation and RAG interface for CS professor reviews.
Uses Groq's llama-3.3-70b-versatile model with source attribution.
"""

import sys
import os
from typing import List, Tuple

# Load .env file if it exists
from pathlib import Path
env_file = Path(".env")
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip("'\"")

try:
    from groq import Groq
except ImportError:
    print("Error: Groq SDK not installed.")
    print("Install with: pip install groq")
    sys.exit(1)

from embed_and_store import ReviewEmbedder


class ProfessorReviewRAG:
    """Retrieval-Augmented Generation interface for professor reviews."""
    def __init__(self, groq_api_key: str = None, top_k: int = 3):
        """
        Initialize RAG system.

        Args:
            groq_api_key: Groq API key (defaults to GROQ_API_KEY env var)
            top_k: Number of chunks to retrieve per query
        """
        if not groq_api_key:
            import os
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable not set")

        self.client = Groq(api_key=groq_api_key)
        self.model = "llama-3.3-70b-versatile"
        self.top_k = top_k

        # Initialize embedder to load existing database
        print("Loading embeddings from ChromaDB...")
        self.embedder = ReviewEmbedder()

    def generate_answer(self, query: str) -> Tuple[str, List[str]]:
        """
        Generate answer to query using retrieved chunks.

        Args:
            query: User question

        Returns:
            Tuple of (answer_text, source_chunks)
        """
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"{'='*80}")

        # Step 1: Retrieve relevant chunks
        print(f"\nRetrieving top {self.top_k} relevant chunks...")
        retrieved_chunks, similarities = self.embedder.retrieve_chunks(query, top_k=self.top_k)

        print(f"Retrieved {len(retrieved_chunks)} chunks with similarities:")
        for i, (chunk, sim) in enumerate(zip(retrieved_chunks, similarities), 1):
            print(f"  [{i}] Similarity: {sim:.3f}")

        # Step 2: Format context for LLM
        context = self._format_context(retrieved_chunks)

        # Step 3: Generate answer with Groq
        print(f"\nGenerating answer using Groq ({self.model})...")
        answer = self._call_groq(query, context)

        # Step 4: Add source attribution at the end
        print(f"\nFormatting answer with source attribution...")
        source_info = [self._extract_source_info(chunk) for chunk in retrieved_chunks]
        final_answer = self._add_sources_to_answer(answer, source_info)

        return final_answer, retrieved_chunks

    def _add_sources_to_answer(self, answer: str, sources: List[str]) -> str:
        """Add source attribution section to the answer."""
        # Remove any existing "Sources Used" section from LLM response
        if "Sources Used:" in answer:
            answer = answer.split("Sources Used:")[0].strip()

        sources_section = "\n\nSOURCES:\n" + "\n".join(f"• {source}" for source in sources)
        return answer + sources_section

    def _format_context(self, chunks: List[str]) -> str:
        """Format chunks for LLM context."""
        context = "SOURCES:\n"
        for i, chunk in enumerate(chunks, 1):
            context += f"\n{chunk}\n"
        return context

    def _extract_source_info(self, chunk: str) -> str:
        """Extract key source information from a chunk."""
        import re

        professor_match = re.search(r'Professor:\s*([^|]+)', chunk)
        course_match = re.search(r'Course:\s*([^|]+)', chunk)

        professor = professor_match.group(1).strip() if professor_match else "Unknown"
        course = course_match.group(1).strip() if course_match else "Unknown"

        return f"{professor} - {course}"

    def _call_groq(self, query: str, context: str) -> str:
        """
        Call Groq API with query and context.
        Enforces source-only constraint.
        """
        system_prompt = """You are a helpful AI assistant answering questions about CS professors at UIUC based on student reviews.

CRITICAL RULES:
1. ONLY use information from the provided sources
2. Do NOT make up, infer, or hallucinate any information
3. If information is not in the sources, say "I don't have information about that"
4. DO NOT use [Source N] notation in your answer
5. Write naturally without numbered citations
6. Be concise and direct

Your answer should be factual and directly based on the student reviews provided."""

        user_message = f"""{context}

Based ONLY on the sources above, answer this question:
{query}

Remember: Only use information from the sources. Write naturally without [Source N] notation."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more factual answers
                max_tokens=1000,
                top_p=0.9,
            )

            answer = response.choices[0].message.content
            return answer

        except Exception as e:
            return f"Error calling Groq API: {str(e)}"

    def interactive_mode(self):
        """Run in interactive Q&A mode."""
        print("\n" + "="*80)
        print("PROFESSOR REVIEW Q&A SYSTEM")
        print("="*80)
        print("Ask questions about CS professors at UIUC (type 'quit' to exit)\n")

        while True:
            try:
                query = input("Your question: ").strip()

                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                if not query:
                    continue

                answer, sources = self.generate_answer(query)

                print(f"\n{'='*80}")
                print("ANSWER:")
                print(f"{'='*80}")
                print(answer)
                print(f"\n{'='*80}\n")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="CS Professor Review Q&A System")
    parser.add_argument("--query", type=str, help="Single query to answer")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    try:
        rag = ProfessorReviewRAG(top_k=3)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nSet your Groq API key:")
        print("  export GROQ_API_KEY='your-api-key'")
        sys.exit(1)

    if args.query:
        # Single query mode
        answer, sources = rag.generate_answer(args.query)
        print(f"\n{'='*80}")
        print("ANSWER:")
        print(f"{'='*80}")
        print(answer)
        print(f"\n{'='*80}\n")

    elif args.interactive or not args.query:
        # Interactive mode (default)
        rag.interactive_mode()


if __name__ == "__main__":
    main()
