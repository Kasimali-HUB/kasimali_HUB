from pydantic import BaseModel


class LegislationQuestion(BaseModel):
    question: str


class SourceCitation(BaseModel):
    doc_id: str
    title: str
    citation: str


class LegislationAnswer(BaseModel):
    question: str
    answer: str
    sources: list[SourceCitation]
    generated_by_llm: bool  # False means this is an extractive fallback, not a synthesized answer
