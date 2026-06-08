# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
I very originally chose to do CS professor reviews at my college (UIUC). The knowledge isn't necessarily difficult to find through official channels, but it can be rather time consuming to look for specific things about professors/classes or a summary overall.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Rate my professor | Margaret Fleck| https://www.ratemyprofessors.com/professor/1169737|
| 2 | RMP| Geoffrey Challen| https://www.ratemyprofessors.com/professor/2327680|
| 3 | RMP| Michael Nowak| https://www.ratemyprofessors.com/professor/2685082|
| 4 | RMP| Ryan Cunningham| https://www.ratemyprofessors.com/professor/1966577|
| 5 | RMP| Ruta Mehta| https://www.ratemyprofessors.com/professor/2575487|
| 6 | RMP| Mike Woodley| https://www.ratemyprofessors.com/professor/1698730|
| 7 | RMP| Hongye Liu| https://www.ratemyprofessors.com/professor/2527253|
| 8 | RMP| Brad Solomon| https://www.ratemyprofessors.com/professor/2873724|
| 9 | RMP| Marco Morales Aguirre| https://www.ratemyprofessors.com/professor/2719900|
| 10 | RMP| Han Zhao| https://www.ratemyprofessors.com/professor/2861440|

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
300
**Overlap:**
75
**Reasoning:**
Since rate my professor reviews are rather short 300 characters should be enough to encapsulate each review with some extra head room for longer reviews.
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2
**Top-k:**
3
**Production tradeoff reflection:**
I'd heavily weigh in the accuracy of the results to ensure the wrong information wasn't being spread. Latency would be second.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about CS 361?| The professor is nice, but the lectures are bad.|
| 2 | What do students say about CS 173?| The class has way too many quizzes|
| 3 | What do students say about CS 222?| The entire class seems to be AI generated|
| 4 | What do students say about CS 225?| The opinion is mixed, most say the lectures are good|
| 5 | What do students say about CS 374?| The professor is great and the course is great|

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.
Hallucination, it could start talking about things not mentioned in the reviews or expand off them.
2.
The chunking could be too big or too small which would lessen the quality of the responses.
---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

Rate my professor -> CS professor reviews (300 char, 75 overlap) -> ChromaDB, all-MiniLM-L6-v2 -> Course summary
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
