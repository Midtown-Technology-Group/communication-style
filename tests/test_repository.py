from communication_style.repository import CommunicationRepository


class SyntheticGraph:
    BASE_URL = "https://synthetic.invalid"

    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def _request_with_retry(self, method, url, *, params):
        self.calls.append((url, params))
        payload = self.pages[url]

        class Response:
            def json(self):
                return payload

        return Response()


def message(message_id, sender, text="Synthetic note."):
    return {
        "id": message_id,
        "from": {"user": {"id": sender}},
        "body": {"content": text},
    }


def test_chat_limit_counts_authored_nonempty_samples_across_pages_and_chats():
    base = SyntheticGraph.BASE_URL
    graph = SyntheticGraph(
        {
            f"{base}/me/chats": {"value": [{"id": "one"}, {"id": "two"}]},
            f"{base}/me/chats/one/messages": {
                "value": [message("other", "other"), message("empty", "self", "")],
                "@odata.nextLink": f"{base}/next",
            },
            f"{base}/next": {"value": [message("mine-one", "self")]},
            f"{base}/me/chats/two/messages": {
                "value": [
                    message("other-two", "other"),
                    message("mine-two", "self"),
                    message("over-limit", "self"),
                ],
                "@odata.nextLink": f"{base}/must-not-fetch",
            },
        }
    )

    samples = CommunicationRepository(graph).authored_chat_messages(
        user_id="self", message_limit=2
    )

    assert [sample.id for sample in samples] == ["mine-one", "mine-two"]
    assert len(graph.calls) == 4
    assert graph.calls[2][1] is None


def test_unlimited_chat_collection_keeps_only_authored_nonempty_messages():
    base = SyntheticGraph.BASE_URL
    graph = SyntheticGraph(
        {
            f"{base}/me/chats": {"value": [{"id": "one"}]},
            f"{base}/me/chats/one/messages": {
                "value": [message("other", "other"), message("mine", "self")],
            },
        }
    )
    samples = CommunicationRepository(graph).authored_chat_messages(
        user_id="self", message_limit=None
    )
    assert [sample.id for sample in samples] == ["mine"]
