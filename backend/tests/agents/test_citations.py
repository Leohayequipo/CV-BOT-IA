from app.agents.citations import CitationStream
from app.agents.sources import Source, profile_sources
from app.schemas.chat import CitationEvent, TokenEvent

RESULTS = Source(
    id="servime#results",
    label="ServiME · Results",
    source="case-studies/servime.md",
    section="Results",
)


def stream() -> CitationStream:
    return CitationStream({**profile_sources(), RESULTS.id: RESULTS})


def run(*pieces: str) -> list[TokenEvent | CitationEvent]:
    citations = stream()
    events = [event for piece in pieces for event in citations.feed(piece)]
    return events + citations.flush()


def text_of(events: list[TokenEvent | CitationEvent]) -> str:
    return "".join(event.text for event in events if isinstance(event, TokenEvent))


def test_a_marker_becomes_a_number_and_its_citation_comes_first() -> None:
    events = run("He led a team [profile:experience].")

    assert [type(event) for event in events] == [
        TokenEvent,
        CitationEvent,
        TokenEvent,
        TokenEvent,
    ]
    citation = events[1]
    assert isinstance(citation, CitationEvent)
    assert (citation.id, citation.label, citation.source, citation.section) == (
        1,
        "Profile · Experience",
        "profile.yaml",
        "Experience",
    )
    assert text_of(events) == "He led a team [1]."


def test_the_same_source_keeps_its_number_and_is_announced_once() -> None:
    events = run("A [profile:experience] B [servime#results] C [profile:experience]")

    assert text_of(events) == "A [1] B [2] C [1]"
    assert [event.id for event in events if isinstance(event, CitationEvent)] == [1, 2]


def test_a_marker_split_across_pieces_is_still_recognised() -> None:
    events = run("Result [servime", "#res", "ults] done")

    assert text_of(events) == "Result [1] done"
    assert [event.id for event in events if isinstance(event, CitationEvent)] == [1]


def test_a_citation_the_model_invented_is_dropped() -> None:
    events = run("He won an award [profile:awards] and [1] and [made-up#id].")

    assert not [event for event in events if isinstance(event, CitationEvent)]
    assert text_of(events) == "He won an award  and  and ."


def test_brackets_that_are_not_source_ids_stay_as_text() -> None:
    assert text_of(run("Use [Laravel] or [B1 level] here")) == "Use [Laravel] or [B1 level] here"


def test_a_bracket_that_never_closes_is_shown_when_the_answer_ends() -> None:
    assert text_of(run("He knows [PHP")) == "He knows [PHP"


def test_a_long_unclosed_bracket_is_released_as_text() -> None:
    long_text = "[" + "x" * 100

    assert text_of(run(long_text, " more")) == long_text + " more"


def test_cited_lists_the_sources_in_order_of_first_use() -> None:
    citations = stream()
    citations.feed("[servime#results] then [profile:skills]")

    assert [source.id for source in citations.cited] == ["servime#results", "profile:skills"]
