"""Language default: saved preference, ?lang=, then Thai browser vs English fallback."""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402

HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
JS = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")


def _extract_preferred_lang() -> str:
    start = JS.index("function preferredLang(")
    i = JS.index("{", start)
    depth = 0
    for j, ch in enumerate(JS[i:], i):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return JS[start:j + 1]
    raise AssertionError("could not extract preferredLang")


HARNESS = r"""
const localStorageStore = Object.create(null);
const localStorage = {
  getItem: (k) => (k in localStorageStore ? localStorageStore[k] : null),
  setItem: (k, v) => { localStorageStore[k] = String(v); },
  clear() { for (const k of Object.keys(localStorageStore)) delete localStorageStore[k]; },
};
const location = { search: "" };
const navigator = { languages: [], language: "" };
FUNCTION
function run(saved, search, languages, language) {
  localStorage.clear();
  if (saved !== null) localStorage.setItem("duang-lang", saved);
  location.search = search;
  navigator.languages = languages;
  navigator.language = language;
  const lang = preferredLang();
  return { lang, saved: localStorage.getItem("duang-lang") };
}
const cases = [
  // saved preference wins
  { saved: "en", search: "?lang=th", languages: ["th"], language: "th-TH", expect: "en", savedAfter: "en" },
  { saved: "th", search: "?lang=en", languages: ["en"], language: "en", expect: "th", savedAfter: "th" },
  // URL param when no (valid) saved pref, and it is persisted
  { saved: null, search: "?lang=en", languages: ["th"], language: "th", expect: "en", savedAfter: "en" },
  { saved: null, search: "?lang=th", languages: ["es"], language: "es", expect: "th", savedAfter: "th" },
  { saved: null, search: "?lang=EN", languages: ["th"], language: "th", expect: "en", savedAfter: "en" },
  { saved: "nope", search: "?lang=en", languages: ["th"], language: "th", expect: "en", savedAfter: "en" },
  { saved: null, search: "?lang=es", languages: ["es"], language: "es", expect: "en", savedAfter: null },
  // browser Thai (any list entry starting with th)
  { saved: null, search: "", languages: ["th-TH", "en"], language: "en", expect: "th", savedAfter: null },
  { saved: null, search: "", languages: [], language: "th", expect: "th", savedAfter: null },
  { saved: null, search: "", languages: ["en-TH"], language: "en-TH", expect: "en", savedAfter: null },
  // otherwise English
  { saved: null, search: "", languages: ["es-ES", "en"], language: "es", expect: "en", savedAfter: null },
  { saved: null, search: "", languages: [], language: "", expect: "en", savedAfter: null },
];
const fails = [];
for (const c of cases) {
  const got = run(c.saved, c.search, c.languages, c.language);
  if (got.lang !== c.expect || got.saved !== c.savedAfter) {
    fails.push({ c, got });
  }
}
if (fails.length) {
  console.error(JSON.stringify(fails, null, 2));
  process.exit(1);
}
console.log("ok", cases.length);
"""


class HtmlStaysThai(unittest.TestCase):
    def test_source_and_served_index_keep_html_lang_th(self):
        self.assertIn('<html lang="th">', HTML)
        self.assertEqual(len(re.findall(r"<html\b[^>]*>", HTML)), 1)
        served = app.index_html().decode("utf-8")
        self.assertIn('<html lang="th">', served)
        self.assertNotIn('<html lang="en">', HTML)
        self.assertNotIn('<html lang="en">', served)

    def test_boot_script_and_toggle(self):
        self.assertIn('data-boot-lang", "en"', HTML)
        self.assertIn('localStorage.getItem("duang-lang")', HTML)
        self.assertIn("navigator.languages", HTML)
        self.assertIn('class="lang-globe"', HTML)
        self.assertIn('id="lang-en"', HTML)
        self.assertIn("google-site-verification", HTML)
        self.assertIn("html[data-boot-lang=\"en\"] [data-i18n]", CSS)
        self.assertIn(".lang-globe", CSS)


class PreferredLang(unittest.TestCase):
    def test_app_js_uses_preferred_lang(self):
        self.assertIn("function preferredLang()", JS)
        self.assertIn("lang: preferredLang()", JS)
        self.assertIn('document.documentElement.removeAttribute("data-boot-lang")', JS)
        self.assertNotIn('lang: localStorage.getItem("duang-lang") || "th"', JS)

    def test_preferred_lang_cases(self):
        fn = _extract_preferred_lang()
        self.assertIn("localStorage.getItem", fn)
        self.assertIn("URLSearchParams", fn)
        self.assertIn("navigator.languages", fn)
        script = HARNESS.replace("FUNCTION", fn)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(script)
            path = fh.name
        result = subprocess.run(["node", path], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ok 12", result.stdout)


if __name__ == "__main__":
    unittest.main()
