"""
Legislation Q&A: retrieve relevant statute summaries, then either synthesize
a natural-language answer via an LLM call or, if no API key is configured,
fall back to returning the best-matching excerpt directly.

Boundary note: everything this module sends to an LLM comes from
app/legislation/corpus.py - public statutory summaries, no employee or
client data. This module has no import path to anything in app/exceptions
or app/db that could hand it personal data by accident; that's deliberate,
not just a convention to remember.
"""

import os

import httpx

from app.legislation.retrieval import LegislationRetriever, RetrievedDoc
from app.legislation.schemas import LegislationAnswer, SourceCitation

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
GENERATION_MODEL = "claude-sonnet-4-6"


def _build_prompt(question: str, retrieved: list[RetrievedDoc]) -> str:
    context = "\n\n".join(
        f"[{r.doc.doc_id}] {r.doc.title}\n{r.doc.text}\nSource: {r.doc.citation}"
        for r in retrieved
    )
    return (
        "Answer the associate's question using ONLY the statute summaries below. "
        "Cite the doc_id(s) you relied on. If the summaries don't cover the "
        "question, say so rather than guessing.\n\n"
        f"Statute summaries:\n{context}\n\nQuestion: {question}"
    )


async def _synthesize_with_llm(question: str, retrieved: list[RetrievedDoc]) -> str | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    payload = {
        "model": GENERATION_MODEL,
        "max_tokens": 500,
        "messages": [{"role": "user", "content": _build_prompt(question, retrieved)}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(ANTHROPIC_MESSAGES_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    text_blocks = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
    return "\n".join(text_blocks) if text_blocks else None


async def answer_legislation_question(
    question: str,
    retriever: LegislationRetriever,
    *,
    top_k: int = 3,
) -> LegislationAnswer:
    retrieved = retriever.retrieve(question, top_k=top_k)

    if not retrieved:
        return LegislationAnswer(
            question=question,
            answer=(
                "Nothing in the current legislation corpus matches this question. "
                "It may need a new corpus entry, or fall outside what's covered so far."
            ),
            sources=[],
            generated_by_llm=False,
        )

    llm_answer = await _synthesize_with_llm(question, retrieved)

    if llm_answer is not None:
        return LegislationAnswer(
            question=question,
            answer=llm_answer,
            sources=[
                SourceCitation(doc_id=r.doc.doc_id, title=r.doc.title, citation=r.doc.citation)
                for r in retrieved
            ],
            generated_by_llm=True,
        )

    # No LLM configured - fall back to the best-matching excerpt verbatim
    # rather than failing. Extractive, not generative, but still useful and
    # still statute-only.
    best = retrieved[0]
    return LegislationAnswer(
        question=question,
        answer=best.doc.text,
        sources=[
            SourceCitation(
                doc_id=best.doc.doc_id, title=best.doc.title, citation=best.doc.citation
            )
        ],
        generated_by_llm=False,
    )
