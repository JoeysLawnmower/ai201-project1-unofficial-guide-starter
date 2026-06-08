#!/usr/bin/env python3
"""
Document loader, cleaner, and chunker for RateMyProfessors reviews.
Chunk size: 300 characters, Overlap: 75 characters
"""

import re
import json
import os
from pathlib import Path
from typing import List, Tuple


def extract_json_from_html(html_text: str) -> dict:
    """Extract Apollo Client cache JSON from HTML."""
    # Look for Apollo Client cache data in script tags
    pattern = r'<script id="__APOLLO_STATE__" type="application/json">(.*?)</script>'
    match = re.search(pattern, html_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return {}
    return {}


def extract_reviews_from_html(html_text: str, filename: str) -> List[str]:
    """Extract reviews from HTML file by parsing JSON embedded in HTML."""
    reviews = []
    professor_name = filename.split(" at ")[0]

    # Find all Rating comment blocks - simpler pattern first
    comment_pattern = r'"__typename":"Rating"[^}]*?"comment":"([^"]*)"'
    comments = re.findall(comment_pattern, html_text, re.DOTALL)

    # For each comment, try to find corresponding metadata
    # Look for Rating blocks and extract all fields from each
    rating_blocks = re.findall(r'"__typename":"Rating"(.*?)(?="__typename"|"__id"|$)', html_text, re.DOTALL)

    for block in rating_blocks:
        # Extract fields from this block
        comment_match = re.search(r'"comment":"([^"]*)"', block)
        course_match = re.search(r'"class":"([^"]*)"', block)
        clarity_match = re.search(r'"clarityRating":(\d+)', block)
        helpful_match = re.search(r'"helpfulRating":(\d+)', block)
        difficulty_match = re.search(r'"difficultyRating":(\d+)', block)
        tags_match = re.search(r'"ratingTags":"([^"]*)"', block)

        if comment_match:
            comment = comment_match.group(1)
            course = course_match.group(1) if course_match else ""
            clarity = int(clarity_match.group(1)) if clarity_match else 0
            helpful = int(helpful_match.group(1)) if helpful_match else 0
            difficulty = int(difficulty_match.group(1)) if difficulty_match else 0
            tags = tags_match.group(1) if tags_match else ""

            if comment.strip():
                # Build review string
                review_parts = [f"Professor: {professor_name}"]
                if course:
                    review_parts.append(f"Course: {course}")
                if clarity or helpful or difficulty:
                    review_parts.append(f"Clarity: {clarity}/5, Helpful: {helpful}/5, Difficulty: {difficulty}/5")
                if tags:
                    review_parts.append(f"Tags: {tags}")
                review_parts.append(f"Review: {comment}")

                review_text = " | ".join(review_parts)
                reviews.append(review_text)

    return reviews


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 75) -> List[str]:
    """
    Split text into chunks with overlap.

    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    chunks = []
    stride = chunk_size - overlap

    for start in range(0, len(text), stride):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        if end >= len(text):
            break

    return chunks


def load_and_process_documents(doc_dir: str = "documents") -> Tuple[List[str], int]:
    """
    Load all HTML documents from directory, extract reviews, clean, and chunk them.

    Args:
        doc_dir: Directory containing HTML files

    Returns:
        Tuple of (list of chunks, total chunk count)
    """
    all_chunks = []
    doc_path = Path(doc_dir)

    if not doc_path.exists():
        print(f"Creating {doc_dir} directory...")
        doc_path.mkdir(parents=True, exist_ok=True)
        return [], 0

    # Process HTML files
    for file in sorted(doc_path.glob("*.html")):
        print(f"Processing {file.name}...")
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        # Extract reviews from JSON data
        reviews = extract_reviews_from_html(html_content, file.name)

        if reviews:
            # Combine all reviews into a single document
            combined = " ".join(reviews)

            # Chunk the combined reviews
            chunks = chunk_text(combined)
            all_chunks.extend(chunks)
            print(f"  Extracted {len(reviews)} reviews, generated {len(chunks)} chunks")

    return all_chunks, len(all_chunks)


if __name__ == "__main__":
    print("Processing RateMyProfessors documents...")
    print("=" * 80)

    doc_chunks, doc_count = load_and_process_documents()

    if doc_count > 0:
        print("\n" + "=" * 80)
        print(f"TOTAL CHUNKS GENERATED: {doc_count}")
        print("=" * 80 + "\n")

        # Display first 5+ chunks
        display_count = min(6, doc_count)
        for i in range(display_count):
            chunk = doc_chunks[i]
            print(f"--- CHUNK {i+1} ---")
            print(f"Length: {len(chunk)} characters")
            print(chunk)
            print()
    else:
        print("\nNo document files found. Place HTML files from RateMyProfessors in the 'documents' directory.")

