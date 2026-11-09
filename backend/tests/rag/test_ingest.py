from collections.abc import Callable

from app.content.models import CaseStudy, Content
from app.rag.ingest import ingest
from tests.rag.conftest import FakeEmbedder, InMemoryStore

MakeContent = Callable[..., Content]
MakeCaseStudy = Callable[..., CaseStudy]

DEMO_CHUNK_IDS = [
    "demo#summary",
    "demo#context-and-problem",
    "demo#leonardo-s-role",
    "demo#architecture",
    "demo#key-decisions-and-trade-offs",
    "demo#results",
]


def test_the_first_run_adds_every_chunk(make_content: MakeContent) -> None:
    store = InMemoryStore()

    report = ingest(make_content(), FakeEmbedder(), store)

    assert (report.added, report.updated, report.removed, report.unchanged) == (6, 0, 0, 0)
    assert sorted(store.rows) == sorted(DEMO_CHUNK_IDS)


def test_running_it_twice_embeds_nothing_the_second_time(make_content: MakeContent) -> None:
    store = InMemoryStore()
    ingest(make_content(), FakeEmbedder(), store)
    embedder = FakeEmbedder()

    report = ingest(make_content(), embedder, store)

    assert embedder.embedded == []
    assert (report.added, report.updated, report.removed, report.unchanged) == (0, 0, 0, 6)


def test_only_the_edited_section_is_embedded_again(
    make_content: MakeContent, make_case_study: MakeCaseStudy
) -> None:
    store = InMemoryStore()
    ingest(make_content(), FakeEmbedder(), store)
    embedder = FakeEmbedder()

    report = ingest(make_content(make_case_study(Results="A new result.")), embedder, store)

    assert embedder.embedded == ["Demo - Results\n\nA new result."]
    assert (report.updated, report.unchanged) == (1, 5)
    assert store.chunk("demo#results").content == "A new result."


def test_chunks_of_a_deleted_section_or_case_study_are_removed(
    make_content: MakeContent, make_case_study: MakeCaseStudy
) -> None:
    store = InMemoryStore()
    before = make_content(make_case_study(Challenges="Hard bits."), make_case_study("other"))
    ingest(before, FakeEmbedder(), store)

    report = ingest(make_content(make_case_study()), FakeEmbedder(), store)

    assert report.removed == 7
    assert sorted(store.rows) == sorted(DEMO_CHUNK_IDS)


def test_changing_the_embedding_model_embeds_everything_again(make_content: MakeContent) -> None:
    store = InMemoryStore()
    ingest(make_content(), FakeEmbedder("model-a"), store)
    embedder = FakeEmbedder("model-b")

    report = ingest(make_content(), embedder, store)

    assert len(embedder.embedded) == 6
    assert report.updated == 6
