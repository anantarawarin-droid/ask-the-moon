"""In-app browser (X, LINE, IG, FB, TikTok, webviews) detection and the login notice.

Google refuses sign-in inside these webviews (disallowed_useragent), so the login box
must guide people to Safari/Chrome instead of showing a Google button that goes blank.
"""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
NODE = shutil.which("node")

UAS = {
    "x_ios": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Twitter for iPhone/10.70",
    "x_ios_bare": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "x_android": "Mozilla/5.0 (Linux; Android 14; SM-S918B Build/UP1A; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0 Mobile Safari/537.36 TwitterAndroid",
    "line_ios": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari Line/14.9.0",
    "ig": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 330.0.0.0 (iPhone14,2; iOS 17_5; th_TH)",
    "fb": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBAV/470.0]",
    "tiktok": "Mozilla/5.0 (Linux; Android 13; wv) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36 musical_ly_2023",
    "android_wv": "Mozilla/5.0 (Linux; Android 13; Pixel 7; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0 Mobile Safari/537.36",
    "safari_ios": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "chrome_ios": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0 Mobile/15E148 Safari/604.1",
    "chrome_android": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Mobile Safari/537.36",
    "chrome_desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    "safari_mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
}


def run_js(expr_by_key):
    start = JS.index("function inAppBrowser(")
    end = JS.index("async function copyText(")
    src = JS[start:end]
    prog = (
        "const navigator = { maxTouchPoints: 5 };\n"
        "const location = { href: 'https://foolmoon.lol/?v=2#oracle' };\n"
        + src
        + "\nconst UAS = " + json.dumps(UAS) + ";\n"
        + "const out = {};\nfor (const [k, ua] of Object.entries(UAS)) out[k] = "
        + expr_by_key + ";\nconsole.log(JSON.stringify(out));"
    )
    res = subprocess.run([NODE, "-e", prog], capture_output=True, text=True, timeout=20)
    if res.returncode:
        raise AssertionError(res.stderr)
    return json.loads(res.stdout)


@unittest.skipUnless(NODE, "node not installed")
class Detection(unittest.TestCase):
    def test_in_app_browsers_detected(self):
        got = run_js("inAppBrowser(ua)")
        for k in ("x_ios", "x_ios_bare", "x_android", "line_ios", "ig", "fb", "tiktok", "android_wv"):
            self.assertIsNotNone(got[k], k)
        self.assertEqual(got["x_ios"]["app"], "X")
        self.assertEqual(got["line_ios"]["app"], "LINE")
        self.assertEqual(got["ig"]["app"], "Instagram")
        self.assertEqual(got["fb"]["app"], "Facebook")

    def test_real_browsers_not_flagged(self):
        got = run_js("inAppBrowser(ua)")
        for k in ("safari_ios", "chrome_ios", "chrome_android", "chrome_desktop", "safari_mac"):
            self.assertIsNone(got[k], k)

    def test_external_open_urls(self):
        got = run_js("externalOpenUrl(ua)")
        self.assertIn("openExternalBrowser=1", got["line_ios"])
        self.assertTrue(got["line_ios"].startswith("https://foolmoon.lol/"))
        self.assertTrue(got["x_android"].startswith("intent://foolmoon.lol/"))
        self.assertIn("package=com.android.chrome", got["x_android"])
        self.assertIn("S.browser_fallback_url=https%3A%2F%2Ffoolmoon.lol", got["x_android"])
        self.assertTrue(got["x_ios"].startswith("x-safari-https://foolmoon.lol/"))
        for k in ("line_ios", "x_android", "x_ios"):
            self.assertIn("login=1", got[k], k)
            self.assertNotIn("#oracle", got[k].split("S.browser_fallback_url")[0] if "intent" in got[k] else got[k])


class Wiring(unittest.TestCase):
    def test_google_button_always_first_with_quiet_hint(self):
        self.assertIn("inAppBrowser(navigator.userAgent)", JS)
        self.assertIn('<div class="g-btn" id="g-btn">', JS)
        self.assertIn('${inApp ? inAppHintHtml(dict, inApp) : ""}', JS)
        self.assertRegex(JS, r"mountGoogleButton\(\);\s*if \(inApp\) wireInAppHint\(\);")
        self.assertNotIn("inapp-note", JS)  # no warning box / big button / numbered steps
        self.assertNotIn("inapp-steps", JS)

    def test_both_languages_have_hint_strings(self):
        for key in ("iaHintX", "iaHint", "iaHintOpen", "iaOpenLink", "iaCopy", "iaCopied", "iaCopiedShort"):
            self.assertEqual(len(re.findall(r"\b" + key + r":", JS)), 2, key)
        self.assertIn("ถ้ากดแล้วขึ้นหน้าขาว ให้กด ⋮ ข้างชื่อเว็บด้านล่าง แล้วเลือก “Open in browser”", JS)

    def test_resume_login_after_switching_browser(self):
        self.assertIn("loadAuthConfig().then(maybeResumeLogin)", JS)

    def test_site_verification_meta_kept(self):
        self.assertIn('name="google-site-verification"', HTML)


class FreshAssets(unittest.TestCase):
    def test_index_versions_assets_and_revalidates(self):
        import sys
        sys.path.insert(0, str(ROOT))
        import app
        html = app.index_html().decode("utf-8")
        self.assertRegex(html, r'src="/app\.js\?v=[0-9a-f]{10}"')
        self.assertRegex(html, r'href="/styles\.css\?v=[0-9a-f]{10}"')
        self.assertRegex(html, r'/og-image\.jpg\?v=[0-9a-f]{10}')
        self.assertIn('name="google-site-verification"', html)
        self.assertTrue({"/", "/index.html"} <= app.REVALIDATE_PATHS)
        self.assertNotIn("/app.js", app.REVALIDATE_PATHS)
        self.assertNotIn("/styles.css", app.REVALIDATE_PATHS)
        self.assertNotIn("/vendor/qrcode.js", html)


if __name__ == "__main__":
    unittest.main()
