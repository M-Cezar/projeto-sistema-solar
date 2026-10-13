"""Screen-reader context regressions for the CSS-only solar simulation."""
import unittest
from html.parser import HTMLParser
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")

class ReadableDocument(HTMLParser):
    def __init__(self):
        super().__init__()
        self.heading_depth = 0
        self.headings = []
        self.title_depth = 0
        self.title = ""
        self.styles = []
    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.heading_depth += 1
            self.styles.append(dict(attrs).get("class", ""))
        if tag == "title":
            self.title_depth += 1
    def handle_endtag(self, tag):
        if tag == "h1":
            self.heading_depth -= 1
        if tag == "title":
            self.title_depth -= 1
    def handle_data(self, data):
        if self.heading_depth:
            self.headings.append(data)
        if self.title_depth:
            self.title += data

class SolarAccessibilityTests(unittest.TestCase):
    def test_page_has_descriptive_title(self):
        d = ReadableDocument()
        d.feed(HTML)
        self.assertIn("Sistema Solar", d.title)

    def test_screen_reader_has_meaningful_heading(self):
        d = ReadableDocument()
        d.feed(HTML)
        self.assertEqual(len(d.styles), 1)
        self.assertIn("sr-only", d.styles[0])
        text = " ".join(d.headings)
        for word in ("Sol", "Terra", "Lua"):
            with self.subTest(word=word):
                self.assertIn(word, text)

    def test_heading_is_visually_hidden_without_aria_hidden_or_display_none(self):
        self.assertIn(".sr-only {", HTML)
        self.assertNotIn('aria-hidden="true"', HTML)
        css = HTML.split(".sr-only {", 1)[1].split("}", 1)[0]
        self.assertIn("position: absolute", css)
        self.assertNotIn("display: none", css)
        self.assertNotIn("visibility: hidden", css)

if __name__ == "__main__":
    unittest.main()
