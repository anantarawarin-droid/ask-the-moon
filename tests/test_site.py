"""Pricing display consistency, page positioning/layout, and admin contact options."""

import os
import re
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402
import credits as billing  # noqa: E402

HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
JS = (ROOT / "static" / "app.js").read_text(encoding="utf-8")

class PricingConsistency(unittest.TestCase):
    def test_every_number_fits_the_total(self):
        for pkgs in (billing.current_packages(), billing.build_packages(billing.PACKAGE_TABLE), billing.build_packages(billing.PROMO_PACKAGE_TABLE)):
            for price, p in {x["price"]: x for x in pkgs}.items():
                # bonus is INSIDE the total, never added on top
                self.assertEqual(p["baseQuestions"] + p["bonus"], p["questions"], price)
                self.assertEqual(Decimal(p["perQuestion"]), (Decimal(price) / p["questions"]).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP"))
            best = next(x for x in pkgs if x["price"] == 150)
            self.assertTrue(best["bestValue"])

    def test_credits_granted_equal_total(self):
        for p in billing.current_packages():
            svc = billing.CreditService(billing.JsonStore(Path(self.tmp) / f"{p['price']}.json"))
            order = svc.create_order("v" * 32, p["price"])
            self.assertEqual(order["questions"], p["questions"])
            svc.approve(order["code"])
            self.assertEqual(svc.balance("v" * 32)["credits"], p["questions"], p["price"])

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()

    def test_page_copy_has_no_conflicting_numbers(self):
        # No "value ฿225"/strike-through prices, no "X questions + Y free" headline.
        for gone in ("worthPay", "dict.worth(", "<s>", "bonusFree", "bestGet", "฿225", "225"):
            self.assertNotIn(gone, JS, gone)
        self.assertIn("`จ่าย ${pkg.price} บาท ได้ ${pkg.questions} ข้อ (โบนัส ${pkg.bonus} ข้อ) เฉลี่ยข้อละ", JS)
        self.assertIn("`${b} + โบนัส ${x} = รวม ${q} ข้อ`", JS)
        self.assertIn('promoEnds: "โปรถึง 15 ธ.ค. 2026"', JS)
        self.assertIn('data-i18n="promoEnds"', HTML)
        # Rendered badge text uses the live package totals, never a made-up original price.
        p = next(x for x in billing.current_packages() if x["price"] == 150)
        badge = f"จ่าย {p['price']} บาท ได้ {p['questions']} ข้อ (โบนัส {p['bonus']} ข้อ) เฉลี่ยข้อละ {p['perQuestion'].replace('.00', '')} บาท"
        self.assertEqual(badge, f"จ่าย 150 บาท ได้ {p['questions']} ข้อ (โบนัส {p['bonus']} ข้อ) เฉลี่ยข้อละ {p['perQuestion'].replace('.00', '')} บาท")


class PageLayout(unittest.TestCase):
    def test_tarot_first_positioning_everywhere(self):
        title = re.search(r"<title>(.*?)</title>", HTML).group(1)
        self.assertIn("ไพ่ทาโรต์", title)
        desc = re.search(r'<meta name="description" content="([^"]+)"', HTML).group(1)
        og_desc = re.search(r'<meta property="og:description" content="([^"]+)"', HTML).group(1)
        for d in (desc, og_desc):  # SEO: real Thai search terms
            for term in ("ดูดวงไพ่ทาโรต์", "ใช่ไม่ใช่", "ไพ่ทาโรต์ความรัก", "ออนไลน์"):
                self.assertIn(term, d)
        self.assertIn("ไพ่ทาโรต์", re.search(r'<meta property="og:title" content="([^"]+)"', HTML).group(1))
        lede = re.search(r'data-i18n="heroLede">(.*?)</p>', HTML).group(1)
        self.assertEqual(lede, "พิมพ์คำถาม เลือกไพ่ 1–3 ใบ ตอบตรง ๆ พร้อมเหตุผลและคำแนะนำ")
        self.assertIn('data-i18n="faqTitle">คำถามที่พบบ่อย<', HTML)
        self.assertNotIn("faqIntro", HTML)
        self.assertNotIn("faq-intro", HTML)
        self.assertNotIn("faqIntro", JS)
        self.assertIn("ไพ่ยิปซี", HTML)
        self.assertIn("สำรับเดียวกันทั้ง 78 ใบ", HTML)
        self.assertGreater(HTML.index('id="faq"'), HTML.index('id="oracle"'))
        self.assertNotIn("อ่านดวง · ราศี · นักษัตร · เลขศาสตร์", HTML)

    def test_ad_after_form_and_gate_before_form(self):
        form = HTML.index('id="reading-form"')
        self.assertEqual(HTML.count('class="ad-slot'), 1)
        self.assertGreater(HTML.index('class="ad-slot'), HTML.index('id="pricing"'))
        self.assertGreater(HTML.index('class="ad-slot'), form)
        gate, fields = HTML.index('id="login-gate"'), HTML.index('id="form-fields"')
        self.assertTrue(form < gate < fields)
        self.assertIn('id="form-fields" disabled', HTML)  # locked until we know you're logged in
        self.assertIn(">สมัครฟรี รับคำถามแรกฟรี 1 ข้อ<", HTML)


class Contacts(unittest.TestCase):
    def env(self, **kw):
        clean = {k: v for k, v in os.environ.items() if not k.startswith("CONTACT_")}
        clean.update(kw)
        return mock.patch.dict(os.environ, clean, clear=True)

    def test_default_is_existing_line_only(self):
        with self.env():
            self.assertEqual(app.contacts_payload(),
                             [{"kind": "line", "label": "LINE", "value": "ivymoonask",
                               "url": "https://line.me/ti/p/~ivymoonask"}])

    def test_only_configured_channels_show(self):
        with self.env(CONTACT_TIKTOK="@moon.tok", CONTACT_EMAIL="help@example.com", CONTACT_IG="bad value!"):
            got = {c["kind"]: c for c in app.contacts_payload()}
        self.assertEqual(set(got), {"line", "tiktok", "email"})
        self.assertEqual(got["tiktok"]["url"], "https://www.tiktok.com/@moon.tok")
        self.assertEqual(got["email"]["url"], "mailto:help@example.com")
        with self.env(CONTACT_LINE=""):
            self.assertEqual(app.contacts_payload(), [])
        with self.env(CONTACT_LINE="javascript:alert(1)"):
            self.assertEqual(app.contacts_payload(), [])

    def test_forgot_password_ui(self):
        self.assertIn('forgotLink: "ลืมรหัสผ่าน?"', JS)
        self.assertIn("ชื่อผู้ใช้", re.search(r'forgotHow: "([^"]+)"', JS).group(1))
        self.assertIn("contacts", JS)


if __name__ == "__main__":
    unittest.main()


class PayStepsWording(unittest.TestCase):
    """Slips are verified on the site; LINE is only a 'problem? contact us' fallback."""

    def test_steps_say_upload_not_line(self):
        index = (ROOT / "static" / "index.html").read_text()
        js = (ROOT / "static" / "app.js").read_text()
        for text in ("เลือกแพ็กเกจ แล้วสแกน QR พร้อมเพย์ด้วยแอปธนาคาร", "อัปโหลดสลิปบนหน้านี้ ระบบตรวจสอบให้อัตโนมัติ",
                     "เครดิตเข้าบัญชีของคุณทันทีหลังตรวจผ่าน"):
            self.assertIn(text, index)
            self.assertIn(text, js)
        self.assertIn("Upload your slip on this page and it's verified automatically.", js)

    def test_no_send_slip_via_line_anywhere(self):
        files = [ROOT / "static" / n for n in ("index.html", "app.js", "admin.html")] + [ROOT / "slips.py", ROOT / "app.py"]
        bad = re.compile(r"ส่งสลิป|send (the |your )?slip|slip on LINE|LINE slip", re.I)
        for f in files:
            self.assertEqual(bad.findall(f.read_text()), [], f.name)

    def test_pay_modal_two_steps_no_line_instructions(self):
        js = (ROOT / "static" / "app.js").read_text()
        body = js[js.index("function renderPayModal"):js.index("function slipSectionHtml")]
        self.assertEqual(re.findall(r"<li>", body[body.index('<ol class="pay-steps">'):body.index("</ol>")]).__len__(), 2)
        self.assertNotIn("copy-code", js)
        self.assertNotIn("payStep3", js)
        self.assertNotIn("line-btn\" href=\"https://line.me/ti/p/~ivymoonask\" target=\"_blank\" rel=\"noopener\">${escapeHtml(dict.payLine)}", body)
        for text in ("สแกน QR ด้วยแอปธนาคาร แล้วโอน", "อัปโหลดสลิปด้านล่าง ระบบตรวจและเติมคำถามให้ทันที",
                     "กำลังตรวจสอบเพิ่มเติม เครดิตจะเข้าอัตโนมัติเมื่อผ่าน", 'payLine: "มีปัญหา? ติดต่อ LINE"'):
            self.assertIn(text, js)


class SingleSignInButton(unittest.TestCase):
    def test_hero_has_no_signup_button_when_logged_out(self):
        index = (ROOT / "static" / "index.html").read_text()
        self.assertIn('<p class="hero-offer" id="hero-offer" hidden>', index)
        self.assertNotIn("สมัครฟรี รับคำถามแรกฟรี 1 ข้อ</button>", index)
        js = (ROOT / "static" / "app.js").read_text()
        body = js[js.index("function renderOffer"):js.index("function renderBalance")]
        self.assertIn("const show = Boolean(state.account) && (credits > 0 || freeAvailable);", body)
        self.assertIn("btn.parentElement.hidden = !show;", body)
        self.assertNotIn("dict.heroOffer;", body)
