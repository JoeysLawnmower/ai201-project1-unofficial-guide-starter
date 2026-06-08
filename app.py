#!/usr/bin/env python3
"""
Gradio web interface for CS Professor Review Q&A system.
"""

import gradio as gr
import os
import sys

# Load environment variables from .env
from pathlib import Path
env_file = Path(".env")
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip("'\"")

from generate_answers import ProfessorReviewRAG

# Initialize the RAG system once
try:
    rag = ProfessorReviewRAG(top_k=3)
    print("✓ RAG system initialized")
except ValueError as e:
    print(f"Error: {e}")
    print("Set your Groq API key in .env file: GROQ_API_KEY='your-key'")
    sys.exit(1)


def query_professor_reviews(question: str) -> tuple:
    """
    Query the professor review system and return answer with sources.

    Args:
        question: User's question

    Returns:
        Tuple of (answer, sources_text)
    """
    if not question.strip():
        return "Please enter a question.", ""

    try:
        # Generate answer
        answer, retrieved_chunks = rag.generate_answer(question)

        # Extract source information
        sources = []
        for chunk in retrieved_chunks:
            import re
            professor_match = re.search(r'Professor:\s*([^|]+)', chunk)
            course_match = re.search(r'Course:\s*([^|]+)', chunk)

            professor = professor_match.group(1).strip() if professor_match else "Unknown"
            course = course_match.group(1).strip() if course_match else "Unknown"

            sources.append(f"{professor} - {course}")

        sources_text = "\n".join(f"• {s}" for s in sources)
        return answer, sources_text

    except Exception as e:
        return f"Error: {str(e)}", ""


# Create Gradio interface
with gr.Blocks(title="CS Professor Reviews") as demo:
    gr.Markdown("# 🎓 UIUC CS Professor Reviews")
    gr.Markdown(
        "Ask questions about CS professors at UIUC based on student reviews. "
        "All answers are sourced from real student feedback."
    )

    with gr.Row():
        with gr.Column():
            question_input = gr.Textbox(
                label="Your Question",
                placeholder="e.g., Is CS 225 difficult? What do students say about Margaret Fleck?",
                lines=2,
            )
            submit_btn = gr.Button("Ask", variant="primary", size="lg")

        with gr.Column():
            gr.Markdown("### 💡 Example Questions\n\n" +
                       "• Is CS 225 difficult?\n" +
                       "• What do students say about Margaret Fleck?\n" +
                       "• Which professors give extra credit?\n" +
                       "• Are there many quizzes in CS 173?")

    with gr.Row():
        answer_output = gr.Textbox(
            label="Answer",
            lines=10,
            interactive=False,
        )

    with gr.Row():
        sources_output = gr.Textbox(
            label="Retrieved From",
            lines=3,
            interactive=False,
        )

    # Connect submit button and enter key
    submit_btn.click(
        fn=query_professor_reviews,
        inputs=question_input,
        outputs=[answer_output, sources_output],
    )
    question_input.submit(
        fn=query_professor_reviews,
        inputs=question_input,
        outputs=[answer_output, sources_output],
    )

    gr.Markdown(
        "---\n"
        "📊 System Info: Uses semantic search + hybrid ranking across 74 chunks "
        "from 50 student reviews. Powered by Groq's llama-3.3-70b-versatile."
    )


if __name__ == "__main__":
    demo.launch(share=False)

