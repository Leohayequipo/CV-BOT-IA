from collections.abc import Callable

from app.content.models import CaseStudy
from app.rag.chunking import chunk_case_study


def test_each_section_becomes_one_chunk(make_case_study: Callable[..., CaseStudy]) -> None:
    chunks = chunk_case_study(make_case_study())

    assert [chunk.section for chunk in chunks] == [
        "Summary",
        "Context and problem",
        "Leonardo's role",
        "Architecture",
        "Key decisions and trade-offs",
        "Results",
    ]


def test_chunk_ids_are_stable_and_unique(make_case_study: Callable[..., CaseStudy]) -> None:
    ids = [chunk.id for chunk in chunk_case_study(make_case_study())]

    assert ids[2] == "demo#leonardo-s-role"
    assert len(set(ids)) == len(ids)
    assert ids == [chunk.id for chunk in chunk_case_study(make_case_study())]


def test_the_embedded_text_names_the_project_and_the_section(
    make_case_study: Callable[..., CaseStudy],
) -> None:
    architecture = chunk_case_study(make_case_study())[3]

    assert architecture.text == "Demo - Architecture\n\nHow Demo works."


def test_empty_optional_sections_are_skipped(make_case_study: Callable[..., CaseStudy]) -> None:
    chunks = chunk_case_study(make_case_study(Challenges=""))

    assert "Challenges" not in [chunk.section for chunk in chunks]


def test_the_hash_changes_with_the_text_and_with_the_model(
    make_case_study: Callable[..., CaseStudy],
) -> None:
    before = chunk_case_study(make_case_study())[0]
    edited = chunk_case_study(make_case_study(Summary="Something else."))[0]

    assert before.content_hash("model-a") == before.content_hash("model-a")
    assert before.content_hash("model-a") != before.content_hash("model-b")
    assert before.content_hash("model-a") != edited.content_hash("model-a")
