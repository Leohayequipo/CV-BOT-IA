from app.content.privacy import find_contact_details


def test_email_addresses_are_found() -> None:
    assert find_contact_details("Write to someone@example.com today.") == ["someone@example.com"]


def test_phone_numbers_are_found() -> None:
    # +44 20 7946 0xxx is reserved by the UK regulator for fiction.
    assert find_contact_details("Call +44 20 7946 0958 after lunch.") == ["+44 20 7946 0958"]


def test_years_and_counts_are_not_phone_numbers() -> None:
    text = "From 2017 - 2022 he led 8 developers serving 7+ areas, with 10+ years of experience."

    assert find_contact_details(text) == []
