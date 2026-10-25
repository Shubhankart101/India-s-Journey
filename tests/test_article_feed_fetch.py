import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from scripts.rss_utils import fetch_rss


class FeedResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.body


class FeedFetchTests(unittest.TestCase):
    @patch("scripts.rss_utils.time.sleep")
    @patch("scripts.rss_utils.urlopen")
    def test_retries_transient_network_error(self, urlopen, sleep):
        urlopen.side_effect = [
            URLError("temporary network error"),
            FeedResponse(b"<rss><channel /></rss>"),
        ]

        root = fetch_rss("https://example.test/feed", "test-agent")

        self.assertIsNotNone(root.find("channel"))
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(1)

    @patch("scripts.rss_utils.time.sleep")
    @patch("scripts.rss_utils.urlopen")
    def test_retries_temporary_http_status(self, urlopen, sleep):
        urlopen.side_effect = [
            HTTPError("https://example.test/feed", 503, "Unavailable", None, None),
            FeedResponse(b"<rss><channel /></rss>"),
        ]

        fetch_rss("https://example.test/feed", "test-agent")

        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(1)

    @patch("scripts.rss_utils.time.sleep")
    @patch("scripts.rss_utils.urlopen")
    def test_does_not_retry_permanent_http_status(self, urlopen, sleep):
        urlopen.side_effect = HTTPError(
            "https://example.test/feed", 403, "Forbidden", None, None
        )

        with self.assertRaises(HTTPError):
            fetch_rss("https://example.test/feed", "test-agent")

        urlopen.assert_called_once()
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
