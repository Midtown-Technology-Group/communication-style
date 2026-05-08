from communication_style.focus import filter_by_participants, participant_matches
from communication_style.models import CommunicationSample


def test_participant_matches_whole_name_parts_only():
    assert participant_matches(["Mike Example mike@example.com"], ("mike",))
    assert not participant_matches(["midtown owner@example.com"], ("mike",))


def test_filter_by_participants_uses_metadata_not_text():
    samples = [
        CommunicationSample(
            "teams-chat",
            "1",
            "2026-05-08",
            "c1",
            None,
            "Jack said this was ready.",
            ["Someone Else"],
        ),
        CommunicationSample(
            "teams-chat",
            "2",
            "2026-05-08",
            "c2",
            None,
            "Ready.",
            ["Jack Musick jack@example.com"],
        ),
        CommunicationSample(
            "teams-chat",
            "3",
            "2026-05-08",
            "c3",
            "1:1 w/ Thomas & Steven",
            "Ready.",
            [],
        ),
    ]

    focused = filter_by_participants(samples, ("jack", "jack musick"))

    assert [sample.id for sample in focused] == ["2"]

    focused_by_title = filter_by_participants(samples, ("steven",))

    assert [sample.id for sample in focused_by_title] == ["3"]
