from fastapi import APIRouter

from app.legislation.qa import answer_legislation_question
from app.legislation.retrieval import LegislationRetriever
from app.legislation.schemas import LegislationAnswer, LegislationQuestion

router = APIRouter()

# Built once at import time - the corpus is small and static per deployment;
# rebuilding the TF-IDF matrix per request would be wasteful.
_retriever = LegislationRetriever()


@router.post("/legislation/ask", response_model=LegislationAnswer, tags=["legislation"])
async def ask_legislation_question(payload: LegislationQuestion) -> LegislationAnswer:
    return await answer_legislation_question(payload.question, _retriever)
