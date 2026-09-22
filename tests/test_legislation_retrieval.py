from app.legislation.retrieval import LegislationRetriever


def test_retrieves_relevant_doc_for_matching_question():
    retriever = LegislationRetriever()
    results = retriever.retrieve("What is the AOW threshold for the tax brackets?")
    assert len(results) > 0
    assert any("aow" in r.doc.doc_id for r in results)


def test_retrieves_employer_premium_doc_for_whk_question():
    retriever = LegislationRetriever()
    results = retriever.retrieve("What is the Whk premium rate?")
    assert results[0].doc.doc_id == "nl-employer-premiums-2026"


def test_empty_question_returns_no_results():
    retriever = LegislationRetriever()
    assert retriever.retrieve("") == []


def test_unrelated_question_returns_nothing_or_low_scores():
    retriever = LegislationRetriever()
    results = retriever.retrieve("What's the weather like in Amsterdam today?")
    # Either nothing matches, or whatever matches has a low similarity score -
    # this corpus has no weather content, so nothing should score highly.
    assert all(r.score < 0.3 for r in results)


def test_results_are_ranked_by_score_descending():
    retriever = LegislationRetriever()
    results = retriever.retrieve("tax credit for labor income arbeidskorting")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_top_k_limits_result_count():
    retriever = LegislationRetriever()
    results = retriever.retrieve("tax brackets premium credit income", top_k=2)
    assert len(results) <= 2
