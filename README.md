# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
I very originally chose to do CS professor reviews at my college (UIUC). The knowledge isn't necessarily difficult to find through official channels, but it can be rather time consuming to look for specific things about professors/classes or a summary overall.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
300
**Overlap:**
75
**Why these choices fit your documents:**
It encompasses the reviews and creates a lengthy enough summary.
**Final chunk count:**
74
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
all-MiniLM-L6-v2
**Production tradeoff reflection:**
I'd heavily weigh in the accuracy of the results to ensure the wrong information wasn't being spread. Latency would be second.
---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
"The answers should have source attribution and most importantly only use information from the sources."
**How source attribution is surfaced in the response:**
I later clarified the answers should be at the bottom: "for the source attributing it should instead cite the actual source file at the end and not source 1,2,3 etc throughout."
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about CS 361?| Opinion is mixed, most say the lectures are boring| As expected| Good| Partial|
| 2 | What do students say about CS 173?| Course is poor| Expected response and brings up extensive quizzes| Good| Good|
| 3 | What do students say about CS 225?| Mixed opinion, most enjoy the lectures| As expected| Partial| Partial|
| 4 | What do students say about CS 222?| The course seems AI generated| As expected| Good| Good|
| 5 | What do students say about CS 374?| Mostly everybody enjoys the course and lecture| As expected| Good| Good|
**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
What do students say about CS 225?
**What the system returned:**
Snippet: 

SOURCES:
• Brad Solomon - CS225
• Brad Solomon - CS225
• Unknown - CS225
**Root cause (tied to a specific pipeline stage):**
It seems to be tied to the chunking.
**What you would change to fix it:**
I would likely change the function for cleaning up the HTML file as it seems to delete the source.
---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
It made me actually think about what to do, and how to prompt the AI. It also helped guide me through something I'm not 100% knowledgable on.
**One way your implementation diverged from the spec, and why:**
The questions might've been too broad which wasn't preferred in the planning section.
---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

I prompted the AI to produce the retrieval script and it nearly completed it fully outside of producing an incorrect amount of top_k results, which I fixed.
**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

I prompted the AI to generate responses with source attribution and it originally only produced generic source names which I fixed to be at the end, and to actually provide the file that was used.