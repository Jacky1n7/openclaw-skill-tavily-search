import importlib.util
import io
import json
import pathlib
import ssl
import unittest
import urllib.error
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tavily-search" / "scripts" / "tavily_search.py"
SPEC = importlib.util.spec_from_file_location("tavily_search", SCRIPT)
tavily = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tavily)


class FakeResponse:
    def __init__(self, payload):
        self.buffer = io.BytesIO(payload)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, size=-1):
        return self.buffer.read(size)


class TavilySearchTests(unittest.TestCase):
    def setUp(self):
        self.environment = mock.patch.dict(
            "os.environ", {"TAVILY_API_KEY": "tvly-test-secret"}, clear=True
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    @mock.patch.object(tavily.urllib.request, "urlopen")
    def test_uses_bearer_auth_without_putting_key_in_body(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"results": []}')

        result = tavily.tavily_search("agent skills", 5, False, "basic")

        self.assertEqual(result, {"query": "agent skills", "results": []})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer tvly-test-secret")
        self.assertNotIn("api_key", json.loads(request.data))
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 30)

    @mock.patch.object(tavily.urllib.request, "urlopen")
    def test_forwards_search_filters_and_preserves_score(self, urlopen):
        urlopen.return_value = FakeResponse(
            json.dumps(
                {
                    "answer": "Current answer",
                    "results": [
                        {
                            "title": "Primary source",
                            "url": "https://example.org/source",
                            "content": "Evidence",
                            "score": 0.91,
                        }
                    ],
                }
            ).encode()
        )

        result = tavily.tavily_search(
            "latest result",
            3,
            True,
            "fast",
            topic="news",
            time_range="week",
            include_domains=["Example.org", "example.org"],
            exclude_domains=["spam.example"],
            timeout=12,
        )

        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload["include_domains"], ["example.org"])
        self.assertEqual(payload["exclude_domains"], ["spam.example"])
        self.assertEqual(payload["search_depth"], "fast")
        self.assertEqual(payload["topic"], "news")
        self.assertEqual(payload["time_range"], "week")
        self.assertEqual(result["results"][0]["score"], 0.91)

    @mock.patch.object(tavily.urllib.request, "urlopen")
    def test_reports_authentication_error_without_key_value(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError(
            tavily.TAVILY_URL, 401, "Unauthorized", {}, io.BytesIO(b"{}")
        )

        with self.assertRaisesRegex(
            tavily.TavilySearchError, "authentication failed"
        ) as caught:
            tavily.tavily_search("query", 5, False, "basic")

        self.assertNotIn("tvly-test-secret", str(caught.exception))

    @mock.patch.object(tavily, "_certifi_context", return_value=None)
    @mock.patch.object(tavily.urllib.request, "urlopen")
    def test_reports_tls_failure_without_disabling_verification(
        self, urlopen, _certifi
    ):
        certificate_error = ssl.SSLCertVerificationError("missing issuer")
        urlopen.side_effect = urllib.error.URLError(certificate_error)

        with self.assertRaisesRegex(
            tavily.TavilySearchError, "SSL_CERT_FILE"
        ) as caught:
            tavily.tavily_search("query", 5, False, "basic")

        self.assertIn("was not disabled", str(caught.exception))

    @mock.patch.object(tavily.urllib.request, "urlopen")
    def test_rejects_oversized_response(self, urlopen):
        urlopen.return_value = FakeResponse(b"x" * (tavily.MAX_RESPONSE_BYTES + 1))
        with self.assertRaisesRegex(tavily.TavilySearchError, "safety limit"):
            tavily.tavily_search("query", 5, False, "basic")

    def test_utf8_reconfiguration_handles_windows_console_text(self):
        buffer = io.BytesIO()
        stream = io.TextIOWrapper(buffer, encoding="gbk")
        tavily.configure_utf8_stream(stream)
        stream.write("OpenClaw \U0001f99e 中文")
        stream.flush()
        self.assertEqual(buffer.getvalue().decode("utf-8"), "OpenClaw \U0001f99e 中文")

    def test_brave_and_markdown_formats(self):
        raw = {
            "query": "q",
            "answer": "answer",
            "results": [
                {
                    "title": "Title",
                    "url": "https://example.org",
                    "content": "Snippet",
                    "score": 0.8,
                }
            ],
        }
        brave = tavily.to_brave_like(raw)
        self.assertEqual(brave["results"][0]["snippet"], "Snippet")
        self.assertEqual(brave["results"][0]["score"], 0.8)
        self.assertIn("https://example.org", tavily.to_markdown(raw))

    def test_missing_key_and_empty_query_fail_clearly(self):
        with mock.patch.dict("os.environ", {}, clear=True):  # noqa: SIM117
            with mock.patch.object(
                tavily.pathlib.Path,
                "home",
                side_effect=RuntimeError("home is unavailable"),
            ):
                with self.assertRaisesRegex(
                    tavily.TavilySearchError, "Missing TAVILY_API_KEY"
                ):
                    tavily.tavily_search("query", 5, False, "basic")
        with self.assertRaisesRegex(tavily.TavilySearchError, "must not be empty"):
            tavily.tavily_search("  ", 5, False, "basic")

    def test_country_requires_general_topic(self):
        with self.assertRaisesRegex(tavily.TavilySearchError, "general topic"):
            tavily.tavily_search(
                "query", 5, False, "basic", topic="news", country="china"
            )


if __name__ == "__main__":
    unittest.main()
