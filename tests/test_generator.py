from communication_style.generator import build_human_report, build_style_markdown
from communication_style.eras import build_eras
from communication_style.models import CommunicationSample


def test_build_style_markdown_includes_source_counts():
    samples = [
        CommunicationSample(
            "sent-mail",
            "1",
            "2026-05-08",
            "c1",
            "Subject",
            "Please check this and let me know what blocks it.",
        ),
        CommunicationSample(
            "teams-chat",
            "2",
            "2026-05-08",
            "c2",
            None,
            "I think this is likely the smallest useful next step.",
        ),
    ]

    markdown = build_style_markdown(samples)

    assert "Samples analyzed: 2" in markdown
    assert "Sent email samples: 1" in markdown
    assert "Teams chat samples: 1" in markdown
    assert "Separate evidence from inference." in markdown


def test_build_human_report_includes_profile_language():
    samples = [
        CommunicationSample(
            "sent-mail",
            "1",
            "2026-05-08",
            "c1",
            "Subject",
            "Please check this and let me know what blocks it.",
        ),
        CommunicationSample(
            "teams-chat",
            "2",
            "2026-05-08",
            "c2",
            None,
            "I think this is likely the smallest useful next step.",
        ),
    ]

    markdown = build_human_report(samples)

    assert "Communication Style Guide" in markdown
    assert "Core Voice" in markdown
    assert "Tone Cheat Sheet" in markdown
    assert "Total authored samples: 2" in markdown


def test_build_eras_groups_old_and_return_periods():
    samples = [
        CommunicationSample(
            "teams-chat", "1", "2021-01-01T00:00:00Z", "c1", None, "Old note."
        ),
        CommunicationSample(
            "sent-mail", "2", "2026-05-08T00:00:00Z", "c2", None, "Return note."
        ),
    ]

    eras = {era.slug: len(era.samples) for era in build_eras(samples)}

    assert eras["old-tenure-2018-2023"] == 1
    assert eras["return-period-2026"] == 1
