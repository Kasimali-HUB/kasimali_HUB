"""
Retrieval for the legislation corpus.

Deliberately simple: TF-IDF + cosine similarity, computed locally, over a
small, curated corpus. No embeddings API call, no external service - this
keeps retrieval itself on the safe side of the boundary too, not just the
generation step. If the corpus grows large enough that TF-IDF stops being
good enough, swap the vectorizer here without touching qa.py's interface.
"""

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.legislation.corpus import LegislationDoc, NL_LEGISLATION_CORPUS


@dataclass(frozen=True)
class RetrievedDoc:
    doc: LegislationDoc
    score: float


class LegislationRetriever:
    def __init__(self, corpus: tuple[LegislationDoc, ...] = NL_LEGISLATION_CORPUS):
        self.corpus = corpus
        self._vectorizer = TfidfVectorizer(stop_words="english")
        corpus_texts = [f"{d.title}. {d.text}" for d in corpus]
        self._matrix = self._vectorizer.fit_transform(corpus_texts)

    def retrieve(self, question: str, top_k: int = 3) -> list[RetrievedDoc]:
        if not question.strip():
            return []

        query_vector = self._vectorizer.transform([question])
        scores = cosine_similarity(query_vector, self._matrix)[0]

        ranked = sorted(
            zip(self.corpus, scores, strict=True), key=lambda pair: pair[1], reverse=True
        )
        return [
            RetrievedDoc(doc=doc, score=round(float(score), 4))
            for doc, score in ranked[:top_k]
            if score > 0
        ]
