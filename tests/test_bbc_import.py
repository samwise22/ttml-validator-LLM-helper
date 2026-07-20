import unittest

from app.bbc_import import BBCImportError, _bbc_page_url, _caption_url, _extract_page_media


class BBCImportTests(unittest.TestCase):
    def test_extracts_primary_media_from_news_page_data(self):
        page = (
            r'\"media\":{\"pid\":\"p0nztvgw\",'
            r'\"items\":[{\"id\":\"p0nzvlc5\",\"idType\":\"versionID\",'
            r'\"kind\":\"programme\",\"title\":\"Example video\",'
            r'\"duration\":101,\"orientation\":\"landscape\"}]}'
        )
        self.assertEqual(
            _extract_page_media(page),
            ("p0nztvgw", "p0nzvlc5", "Example video", "landscape"),
        )

    def test_selects_https_caption_connection(self):
        response = {"media": [{
            "kind": "captions",
            "connection": [
                {"protocol": "http", "href": "http://example/sub.xml"},
                {"protocol": "https", "href": "https://vod-sub-uk-live.akamaized.net/sub.xml"},
            ],
        }]}
        self.assertEqual(
            _caption_url(response),
            "https://vod-sub-uk-live.akamaized.net/sub.xml",
        )

    def test_rejects_non_bbc_or_unsupported_page(self):
        for url in ("https://example.com/news/videos/test", "http://www.bbc.co.uk/news/test",
                    "https://www.bbc.co.uk/weather"):
            with self.assertRaises(BBCImportError):
                _bbc_page_url(url)


if __name__ == "__main__":
    unittest.main()
