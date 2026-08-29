"""
Retrieval regression tests.

These call the real retrieve_chunks() against the live Pinecone index (no
mocks) — they're a cheap way to catch a silent ingestion regression (e.g. a
crawler selector breaking and returning near-empty content) by checking that
obvious queries still surface the page they should. Costs a handful of
OpenAI embedding calls per run; not meant to run on every commit, but is a
good fit as a post-ingestion check.

Run:
    pytest test_retriever.py
"""

import pytest

from retriever import retrieve_chunks

# Each case: a realistic user query, and a fragment we expect to see in at
# least one of the top-k retrieved sources' URLs.
RETRIEVAL_CASES = [
    ("Do you repair rock chips in my windshield?", "chip-repair"),
    ("What is ADAS calibration and do you offer it?", "adas-recalibration"),
    ("Can you replace a cracked back window?", "back-glass-replacement"),
    ("Do you come to my house to fix my windshield?", "mobile-glass-repair"),
    ("What areas or cities do you serve?", "serving-area"),
]


@pytest.mark.parametrize("query, expected_source_fragment", RETRIEVAL_CASES)
def test_retrieve_chunks_surfaces_relevant_page(query, expected_source_fragment):
    chunks = retrieve_chunks(query, top_k=5)

    assert chunks, f"No chunks retrieved for query: {query!r}"

    sources = [chunk["source"] for chunk in chunks]
    assert any(expected_source_fragment in source for source in sources), (
        f"Expected a source containing {expected_source_fragment!r} for "
        f"query {query!r}, got: {sources}"
    )
