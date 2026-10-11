"""30 executable security checks for the intentionally static solar-system page."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
WF = (ROOT / ".github/workflows/security.yml").read_text(encoding="utf-8")

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))

P = Parser()
P.feed(HTML)
def meta(name):
    return [a.get("content", "") for t,a in P.attrs if t == "meta" and (a.get("name") == name or a.get("http-equiv") == name)]
def absent(pattern):
    return re.search(pattern, HTML, re.I) is None

class StaticSecurityTests(unittest.TestCase):
    def test_01_doctype(self): self.assertTrue(HTML.lstrip().lower().startswith("<!doctype html>"))
    def test_02_html(self): self.assertEqual(P.tags.count("html"), 1)
    def test_03_head(self): self.assertEqual(P.tags.count("head"), 1)
    def test_04_body(self): self.assertEqual(P.tags.count("body"), 1)
    def test_05_charset(self): self.assertEqual(meta("charset"), []) if False else self.assertTrue(any(a.get("charset")=="utf-8" for t,a in P.attrs if t=="meta"))
    def test_06_viewport(self): self.assertTrue(meta("viewport"))
    def test_07_referrer(self): self.assertEqual(meta("referrer"), ["no-referrer"])
    def test_08_csp_exists(self): self.assertEqual(len(meta("Content-Security-Policy")), 1)
    def test_09_default_deny(self): self.assertIn("default-src 'none'", meta("Content-Security-Policy")[0])
    def test_10_no_connections(self): self.assertIn("connect-src 'none'", meta("Content-Security-Policy")[0])
    def test_11_no_forms(self): self.assertIn("form-action 'none'", meta("Content-Security-Policy")[0])
    def test_12_no_objects(self): self.assertIn("object-src 'none'", meta("Content-Security-Policy")[0])
    def test_13_no_base(self): self.assertIn("base-uri 'none'", meta("Content-Security-Policy")[0])
    def test_14_no_frames(self): self.assertIn("frame-src 'none'", meta("Content-Security-Policy")[0])
    def test_15_no_images(self): self.assertIn("img-src 'none'", meta("Content-Security-Policy")[0])
    def test_16_no_scripts(self): self.assertNotIn("script", P.tags)
    def test_17_no_iframes(self): self.assertNotIn("iframe", P.tags)
    def test_18_no_forms_elements(self): self.assertNotIn("form", P.tags)
    def test_19_no_inputs(self): self.assertNotIn("input", P.tags)
    def test_20_no_remote_links(self): self.assertTrue(all(not re.match(r"(?i)https?://|//",a.get("href","")) for t,a in P.attrs if t in ("link","a")))
    def test_21_no_external_assets(self): self.assertTrue(all(not re.match(r"(?i)https?://|//",a.get("src","")) for t,a in P.attrs))
    def test_22_no_inline_handlers(self): self.assertTrue(all(not any(k.lower().startswith("on") for k in a) for t,a in P.attrs))
    def test_23_no_eval(self): self.assertTrue(absent(r"\beval\s*\("))
    def test_24_no_js_protocol(self): self.assertTrue(absent(r"javascript\s*:"))
    def test_25_no_secret_keys(self): self.assertTrue(absent(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"))
    def test_26_no_github_tokens(self): self.assertTrue(absent(r"github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{30,}"))
    def test_27_no_merge_conflicts(self): self.assertTrue(absent(r"(?m)^(?:<<<<<<< |>>>>>>> |=======$)"))
    def test_28_reduced_motion(self): self.assertIn("prefers-reduced-motion: reduce", HTML)
    def test_29_ci_on_pr_and_main(self): self.assertIn("pull_request:", WF); self.assertIn("branches: [main]", WF)
    def test_30_ci_read_only_and_pinned(self): self.assertRegex(WF, r"contents:\s*read"); self.assertRegex(WF, r"actions/checkout@[a-f0-9]{40}")

if __name__ == "__main__":
    unittest.main()
