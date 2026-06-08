# CS Professor Review RAG System

Complete retrieval-augmented generation pipeline for UIUC CS professor reviews.

## Setup

### 1. Install Dependencies
```bash
pip install sentence-transformers chromadb groq
```

### 2. Set Groq API Key
Get your API key from [console.groq.com](https://console.groq.com/keys), then:

```bash
export GROQ_API_KEY='your-api-key-here'
```

## Pipeline Overview

### Stage 1: Document Processing (`process_documents.py`)
- Loads RateMyProfessors HTML files from `documents/` directory
- Extracts reviews from JSON data (professor name, course, ratings, tags, review text)
- Cleans boilerplate and metadata
- **Output**: 74 chunks (300 chars, 75 char overlap)

```bash
python3 process_documents.py
```

### Stage 2: Embedding & Storage (`embed_and_store.py`)
- Embeds chunks using `all-MiniLM-L6-v2` model (384-dim vectors)
- Stores in ChromaDB with cosine similarity indexing
- **Output**: `.claude/chroma_db/` (740KB)

```bash
python3 embed_and_store.py
```

### Stage 3: Generation & Retrieval (`generate_answers.py`)
- Retrieves top-3 most similar chunks for any query
- Sends to Groq's `llama-3.3-70b-versatile` model
- Enforces source-only answers with citation
- **Output**: Factual answers with [Source N] attribution

```bash
# Single query
python3 generate_answers.py --query "What do students say about Margaret Fleck?"

# Interactive Q&A
python3 generate_answers.py --interactive
```

## Example Queries

```
"What do students say about CS 225?"
"Is Margaret Fleck a good professor?"
"Are there a lot of quizzes in CS 173?"
"What's the difficulty of CS 374?"
"Which professors are hardest graders?"
```

## Architecture

```
RateMyProfessors HTML
       ↓
[Document Processing] → Clean chunks (74 total)
       ↓
[Embedding] → all-MiniLM-L6-v2 vectors
       ↓
[Vector Store] → ChromaDB
       ↓
[Retrieval] → Top-3 cosine similarity
       ↓
[Generation] → Groq llama-3.3-70b-versatile
       ↓
[Interface] → Cited answers
```

## Key Features

✓ **Source Attribution**: Every claim is cited with [Source N]  
✓ **Hallucination Prevention**: System prompt enforces source-only responses  
✓ **Efficient Retrieval**: Cosine similarity on 384-dim embeddings  
✓ **Production Ready**: Persistent ChromaDB storage  
✓ **Clean Data**: HTML boilerplate removed, structured reviews preserved  

## Files

- `process_documents.py` - Document loading and chunking
- `embed_and_store.py` - Embedding and ChromaDB storage
- `generate_answers.py` - RAG generation interface
- `.claude/chroma_db/` - Vector database (created after embedding)
- `documents/` - Input HTML files from RateMyProfessors

## Specifications (from planning.md)

- **Chunk Size**: 300 characters
- **Overlap**: 75 characters
- **Embedding Model**: all-MiniLM-L6-v2
- **Vector Store**: ChromaDB
- **Retrieval**: Top-k=3
- **Generation Model**: Groq llama-3.3-70b-versatile
- **Key Data Preserved**: Professor names, course codes, ratings, review text, tags
