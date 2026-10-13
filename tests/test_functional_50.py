"""Additional behavior, accessibility and structure regressions for the CSS-only solar model."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.open = []
        self.errors = []
        self.elements = []
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag not in {"meta", "link", "br", "img", "hr", "input"}:
            self.open.append(tag)
    def handle_endtag(self, tag):
        if not self.open or self.open[-1] != tag:
            self.errors.append(tag)
        else:
            self.open.pop()

def rule(selector):
    pattern = r"(?<![\w-])" + re.escape(selector) + r"\s*\{([^{}]*)\}"
    matches = re.findall(pattern, HTML, flags=re.I | re.S)
    return "\n".join(matches)

def property_value(css, name):
    matches = re.findall(r"(?:^|;)\s*" + re.escape(name) + r"\s*:\s*([^;]+)", css, flags=re.I)
    return matches[-1].strip() if matches else None

class SolarFunctionalTests(unittest.TestCase):
    def test_01_html_is_balanced(self):
        d = Document(); d.feed(HTML); self.assertEqual(d.errors, []); self.assertEqual(d.open, [])
    def test_02_document_language_is_brazilian_portuguese(self):
        d = Document(); d.feed(HTML)
        self.assertEqual([a.get("lang") for t,a in d.elements if t == "html"], ["pt-BR"])
    def test_03_exactly_one_solar_container(self):
        d = Document(); d.feed(HTML)
        self.assertEqual(sum("container" in a.get("class","").split() for _,a in d.elements), 1)
    def test_04_exactly_one_sun(self):
        d = Document(); d.feed(HTML)
        self.assertEqual(sum("sun" in a.get("class","").split() for _,a in d.elements), 1)
    def test_05_exactly_one_earth(self):
        d = Document(); d.feed(HTML)
        self.assertEqual(sum("earth" in a.get("class","").split() for _,a in d.elements), 1)
    def test_06_exactly_one_moon(self):
        d = Document(); d.feed(HTML)
        self.assertEqual(sum("moon" in a.get("class","").split() for _,a in d.elements), 1)
    def test_07_sun_has_size(self):
        css=rule(".sun")
        self.assertEqual(property_value(css,"width"),"10em"); self.assertEqual(property_value(css,"height"),"10em")
    def test_08_earth_has_size(self):
        css=rule(".earth")
        self.assertEqual(property_value(css,"width"),"30em"); self.assertEqual(property_value(css,"height"),"30em")
    def test_09_moon_has_size(self):
        css=rule(".moon")
        self.assertEqual(property_value(css,"width"),"8em"); self.assertEqual(property_value(css,"height"),"8em")
    def test_10_orbits_use_infinite_animation(self):
        for cls in (".earth",".moon"):
            with self.subTest(cls=cls): self.assertIn("infinite",property_value(rule(cls),"animation") or "")
    def test_11_orbits_use_linear_animation(self):
        for cls in (".earth",".moon"):
            with self.subTest(cls=cls): self.assertIn("linear",property_value(rule(cls),"animation") or "")
    def test_12_earth_orbit_period(self):
        self.assertIn("36.5s",property_value(rule(".earth"),"animation") or "")
    def test_13_moon_orbit_period(self):
        self.assertIn("2.7s",property_value(rule(".moon"),"animation") or "")
    def test_14_animation_keyframes_defined(self):
        self.assertRegex(HTML,r"@keyframes\s+orbit\s*\{")
    def test_15_animation_rotates_full_circle(self):
        self.assertRegex(HTML,r"rotate\s*\(\s*360deg\s*\)")
    def test_16_reduced_motion_disables_both_orbits(self):
        self.assertRegex(HTML,r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{\s*\.earth,\s*\.moon\s*\{\s*animation:\s*none;")
    def test_17_sun_is_round(self):
        self.assertEqual(property_value(rule(".sun"),"border-radius"),"50%")
    def test_18_sun_is_visible(self):
        self.assertEqual(property_value(rule(".sun"),"background-color"),"yellow")
    def test_19_earth_body_is_visible(self):
        self.assertEqual(property_value(rule(".earth::before"),"background-color"),"aqua")
    def test_20_moon_body_is_visible(self):
        self.assertEqual(property_value(rule(".moon::before"),"background-color"),"silver")
    def test_21_solar_container_is_relative(self):
        self.assertEqual(property_value(rule(".container"),"position"),"relative")
    def test_22_sun_is_absolute(self):
        self.assertEqual(property_value(rule(".sun"),"position"),"absolute")
    def test_23_earth_is_absolute(self):
        self.assertEqual(property_value(rule(".earth, .moon"),"position"),"absolute")
    def test_24_earth_body_is_absolute(self):
        self.assertEqual(property_value(rule(".earth::before, .moon::before"),"position"),"absolute")
    def test_25_container_dimensions_match(self):
        css=rule(".container")
        self.assertEqual(property_value(css,"width"),property_value(css,"height"))
    def test_26_body_centers_content(self):
        css=rule("body")
        self.assertEqual(property_value(css,"align-items"),"center")
        self.assertEqual(property_value(css,"justify-content"),"center")
    def test_27_body_is_flex(self):
        self.assertEqual(property_value(rule("body"),"display"),"flex")
    def test_28_page_has_dark_background(self):
        self.assertEqual(property_value(rule("body"),"background-color"),"black")
    def test_29_body_hides_overflow(self):
        self.assertEqual(property_value(rule("body"),"overflow"),"hidden")
    def test_30_no_network_dependent_elements(self):
        d=Document();d.feed(HTML)
        self.assertFalse([t for t,_ in d.elements if t in {"script","iframe","img","video","audio","object","embed"}])
    def test_31_no_navigation(self):
        d=Document();d.feed(HTML);self.assertFalse([t for t,_ in d.elements if t in {"a","form","button"}])
    def test_32_no_external_stylesheets(self):
        d=Document();d.feed(HTML);self.assertFalse([t for t,_ in d.elements if t=="link"])
    def test_33_only_one_style_block(self):
        d=Document();d.feed(HTML);self.assertEqual(sum(t=="style" for t,_ in d.elements),1)
    def test_34_no_inline_style_attributes(self):
        d=Document();d.feed(HTML);self.assertFalse([a for _,a in d.elements if "style" in a])
    def test_35_no_event_handler_attributes(self):
        d=Document();d.feed(HTML);self.assertFalse([a for _,a in d.elements if any(k.lower().startswith("on") for k in a)])
    def test_36_no_duplicate_ids(self):
        d=Document();d.feed(HTML);ids=[a["id"] for _,a in d.elements if "id" in a];self.assertEqual(len(ids),len(set(ids)))
    def test_37_no_duplicate_meta_viewport(self):
        d=Document();d.feed(HTML);self.assertEqual(sum(t=="meta" and a.get("name")=="viewport" for t,a in d.elements),1)
    def test_38_no_duplicate_charset(self):
        d=Document();d.feed(HTML);self.assertEqual(sum(t=="meta" and "charset" in a for t,a in d.elements),1)
    def test_39_no_external_imports(self):
        self.assertNotRegex(HTML,r"@import\b")
    def test_40_no_css_remote_urls(self):
        self.assertNotRegex(HTML,r"url\s*\(\s*['\\"]?https?://")
    def test_41_no_css_expressions(self):
        self.assertNotRegex(HTML,r"expression\s*\(")
    def test_42_no_html_templates(self):
        d=Document();d.feed(HTML);self.assertFalse([t for t,_ in d.elements if t=="template"])
    def test_43_no_untrusted_frames(self):
        d=Document();d.feed(HTML);self.assertFalse([t for t,_ in d.elements if t in {"iframe","frame","frameset"}])
    def test_44_no_form_controls(self):
        d=Document();d.feed(HTML);self.assertFalse([t for t,_ in d.elements if t in {"input","select","textarea"}])
    def test_45_no_meta_refresh(self):
        d=Document();d.feed(HTML);self.assertFalse([a for t,a in d.elements if t=="meta" and a.get("http-equiv","").lower()=="refresh"])
    def test_46_no_base_tag(self):
        d=Document();d.feed(HTML);self.assertFalse([t for t,_ in d.elements if t=="base"])
    def test_47_sun_has_no_animation(self):
        self.assertIsNone(property_value(rule(".sun"),"animation"))
    def test_48_moon_is_nested_in_earth(self):
        self.assertRegex(HTML,r'<div class="earth">\s*<div class="moon"></div>\s*</div>')
    def test_49_sun_is_inside_container(self):
        self.assertRegex(HTML,r'<div class="container">\s*<div class="sun"></div>')
    def test_50_css_orbit_duration_is_positive(self):
        for cls in (".earth",".moon"):
            value=property_value(rule(cls),"animation") or ""
            duration=re.search(r"([0-9]+(?:\.[0-9]+)?)s",value)
            self.assertIsNotNone(duration)
            self.assertGreater(float(duration.group(1)),0)

if __name__ == "__main__":
    unittest.main()
