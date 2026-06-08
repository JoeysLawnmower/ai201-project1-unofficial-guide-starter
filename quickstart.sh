#!/bin/bash
# Quick start script for the RAG system

echo "=========================================="
echo "CS Professor Review RAG - Quick Start"
echo "=========================================="

# Check if embeddings exist
if [ ! -d ".claude/chroma_db" ]; then
    echo ""
    echo "⚠️  Vector database not found. Running embedding pipeline..."
    python3 embed_and_store.py
else
    echo "✓ Vector database found (.claude/chroma_db)"
fi

echo ""
echo "=========================================="
echo "To use the system:"
echo "=========================================="
echo ""
echo "1. SET YOUR GROQ API KEY:"
echo "   export GROQ_API_KEY='your-api-key-from-console.groq.com'"
echo ""
echo "2. RUN A SINGLE QUERY:"
echo "   python3 generate_answers.py --query 'Your question?'"
echo ""
echo "3. RUN INTERACTIVE MODE:"
echo "   python3 generate_answers.py --interactive"
echo ""
echo "4. VIEW RETRIEVAL DEMO (no API key needed):"
echo "   python3 demo.py"
echo ""
echo "=========================================="
echo "Example Queries:"
echo "=========================================="
echo '  "What do students say about Margaret Fleck?"'
echo '  "Is CS 225 hard?"'
echo '  "Which professors give extra credit?"'
echo '  "Are there many quizzes in CS 173?"'
echo ""
