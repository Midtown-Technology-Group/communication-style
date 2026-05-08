from communication_style.text import html_to_text, normalize_text


def test_html_to_text_strips_tags_and_reply_chain():
    raw = "<p>Thanks for checking.<br>Let's use the smaller scope.</p><p>From: Someone</p><p>Old text</p>"

    assert html_to_text(raw) == "Thanks for checking. Let's use the smaller scope."


def test_normalize_text_strips_signature():
    raw = "This is the useful part.\n\nThanks,\nThomas Bray\nMidtown"

    assert normalize_text(raw) == "This is the useful part."
