"""Server-rendered, crawlable tarot meaning pages: /tarot and /tarot/<slug>.

Card names and images come from tarot.DECK; the long Thai meanings live in
tarot_meanings.py. Pages are plain HTML (no JS needed) so search engines can
read them. Reading logic and randomness are not touched here.
"""

from __future__ import annotations

import html
import json
import re
from typing import Any

import tarot
from tarot_meanings import MEANINGS

SITE = "https://foolmoon.lol"
SUIT_ORDER = [
    ("major", "ไพ่ชุดใหญ่ (Major Arcana)", "22 ใบ ว่าด้วยบทเรียนสำคัญและจุดเปลี่ยนของชีวิต"),
    ("wands", "ชุดไม้เท้า (Wands)", "ธาตุไฟ: แรงบันดาลใจ ความกล้า การลงมือทำ"),
    ("cups", "ชุดถ้วย (Cups)", "ธาตุน้ำ: ความรัก อารมณ์ ความสัมพันธ์"),
    ("swords", "ชุดดาบ (Swords)", "ธาตุลม: ความคิด การสื่อสาร ความขัดแย้ง"),
    ("pentacles", "ชุดเหรียญ (Pentacles)", "ธาตุดิน: เงิน งาน ความมั่นคง"),
]


def slugify(name_en: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name_en.lower()).strip("-")


def short_th(card: dict[str, Any]) -> str:
    return re.sub(r"\s*\(.*\)$", "", card["nameTh"])


CARDS = list(tarot.DECK)
BY_SLUG = {slugify(c["nameEn"]): c for c in CARDS}
SLUGS = [slugify(c["nameEn"]) for c in CARDS]
PATHS = ["/tarot"] + [f"/tarot/{s}" for s in SLUGS]


def group_of(card: dict[str, Any]) -> str:
    return "major" if card["id"].startswith("major") else card["id"].split("-")[0]


def _e(s: str) -> str:
    return html.escape(s, quote=True)


def _head(title: str, desc: str, path: str, image: str, ld: list[dict[str, Any]]) -> str:
    url = SITE + path
    lds = "\n".join(
        f'  <script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld
    )
    return f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="theme-color" content="#0a0614" />
  <title>{_e(title)}</title>
  <meta name="description" content="{_e(desc)}" />
  <link rel="canonical" href="{url}" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="ถามจันทร์ · foolmoon.lol" />
  <meta property="og:locale" content="th_TH" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{_e(title)}" />
  <meta property="og:description" content="{_e(desc)}" />
  <meta property="og:image" content="{SITE}{image}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{_e(title)}" />
  <meta name="twitter:description" content="{_e(desc)}" />
  <meta name="twitter:image" content="{SITE}{image}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Cormorant+Garamond:wght@500;600&family=Noto+Sans+Thai:wght@400;500;600;700&family=Noto+Serif+Thai:wght@500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/meanings.css" />
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
{lds}
</head>
<body>
  <header class="m-top">
    <a class="m-brand" href="/"><img src="/favicon.svg" alt="" width="34" height="34" /> <span>ถามจันทร์</span> <small>foolmoon.lol</small></a>
    <a class="m-ask" href="/#oracle">ถามไพ่</a>
  </header>
  <main class="m-main">
"""


FOOT = """  </main>
  <footer class="m-foot">
    <p>ความหมายไพ่เขียนโดยถามจันทร์ เพื่อเป็นแนวทางในการอ่านไพ่ ไม่ใช่คำแนะนำทางการแพทย์ กฎหมาย หรือการเงิน</p>
    <p>ภาพไพ่: สำรับ Rider-Waite-Smith (ค.ศ. 1909) วาดโดย Pamela Colman Smith · สาธารณสมบัติ จาก Wikimedia Commons</p>
    <p><a href="/">หน้าแรก</a> · <a href="/tarot">ความหมายไพ่ทาโรต์ทั้ง 78 ใบ</a> · <a href="/privacy">นโยบายความเป็นส่วนตัว</a> · <a href="/terms">ข้อกำหนดการใช้งาน</a></p>
  </footer>
</body>
</html>
"""


def _cta(text: str) -> str:
    return f"""    <section class="m-cta">
      <p class="m-cta-title">{_e(text)}</p>
      <p>พิมพ์คำถามของคุณ แล้วให้ถามจันทร์เปิดไพ่ 3 ใบ บอกคำตอบตรง ๆ พร้อมเหตุผลจากไพ่ · สมัครฟรี ถามฟรี 1 ข้อ</p>
      <a class="m-btn" href="/#oracle">ถามไพ่ทาโรต์ที่ foolmoon.lol</a>
    </section>
"""


def _breadcrumb(items: list[tuple[str, str]]) -> dict[str, Any]:
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + path}
        for i, (name, path) in enumerate(items)]}


def render_index() -> bytes:
    title = "ความหมายไพ่ทาโรต์ทั้ง 78 ใบ ภาษาไทย ไพ่ปกติและไพ่กลับหัว | ถามจันทร์"
    desc = ("รวมความหมายไพ่ทาโรต์ Rider-Waite-Smith ครบ 78 ใบ ภาษาไทย ทั้งไพ่ชุดใหญ่และชุดเล็ก "
            "ความหมายไพ่ปกติ ไพ่กลับหัว ความรัก การงาน การเงิน พร้อมถามไพ่ออนไลน์ฟรีที่ foolmoon.lol")
    ld = [_breadcrumb([("หน้าแรก", "/"), ("ความหมายไพ่ทาโรต์", "/tarot")]),
          {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc,
           "url": SITE + "/tarot", "inLanguage": "th"}]
    out = [_head(title, desc, "/tarot", "/og-image.png", ld)]
    out.append("""    <nav class="m-crumb"><a href="/">หน้าแรก</a> › <span>ความหมายไพ่ทาโรต์</span></nav>
    <h1>ความหมายไพ่ทาโรต์ทั้ง 78 ใบ</h1>
    <p class="m-lede">ความหมายไพ่ทาโรต์สำรับ Rider-Waite-Smith ภาษาไทย ครบทุกใบ ทั้งความหมายเมื่อไพ่ปกติและไพ่กลับหัว พร้อมแนวทางเรื่องความรัก การงาน และการเงิน แตะที่ไพ่เพื่ออ่านความหมายเต็ม</p>
""")
    out.append('    <nav class="m-jump">' + " ".join(
        f'<a href="#{key}">{_e(label.split(" (")[0])}</a>' for key, label, _ in SUIT_ORDER) + "</nav>\n")
    for key, label, blurb in SUIT_ORDER:
        cards = [c for c in CARDS if group_of(c) == key]
        out.append(f'    <section class="m-suit" id="{key}">\n      <h2>{_e(label)}</h2>\n      <p class="m-blurb">{_e(blurb)}</p>\n      <ul class="m-grid">\n')
        for c in cards:
            s = slugify(c["nameEn"])
            out.append(f'        <li><a href="/tarot/{s}"><img src="{tarot.image_path(c["id"])}" alt="ไพ่{_e(short_th(c))} ({_e(c["nameEn"])})" width="150" height="259" loading="lazy" /><b>{_e(short_th(c))}</b><small>{_e(c["nameEn"])}</small></a></li>\n')
        out.append("      </ul>\n    </section>\n")
    out.append(_cta("อยากรู้ว่าไพ่จะตอบคำถามของคุณว่าอย่างไร?"))
    out.append(FOOT)
    return "".join(out).encode("utf-8")


def render_card(slug: str) -> bytes | None:
    card = BY_SLUG.get(slug)
    if card is None:
        return None
    up, rev, love, work, money = MEANINGS[card["id"]]
    th = short_th(card)
    en = card["nameEn"]
    title = f"ความหมายไพ่{th} ({en}) ไพ่ทาโรต์ ปกติ กลับหัว ความรัก การงาน การเงิน | ถามจันทร์"
    desc = f"ความหมายไพ่{th} ({en}) ไพ่ปกติ: {card['upTh']} · ไพ่กลับหัว: {card['revTh']} · อ่านแนวทางความรัก การงาน การเงิน และถามไพ่ออนไลน์ที่ foolmoon.lol"
    path = f"/tarot/{slug}"
    img = tarot.image_path(card["id"])
    ld = [_breadcrumb([("หน้าแรก", "/"), ("ความหมายไพ่ทาโรต์", "/tarot"), (f"ไพ่{th}", path)]),
          {"@context": "https://schema.org", "@type": "Article", "headline": f"ความหมายไพ่{th} ({en})",
           "description": desc, "inLanguage": "th", "image": SITE + img, "url": SITE + path,
           "author": {"@type": "Organization", "name": "ถามจันทร์"},
           "publisher": {"@type": "Organization", "name": "ถามจันทร์ · foolmoon.lol",
                         "logo": {"@type": "ImageObject", "url": SITE + "/icon-512.png"}}}]
    i = SLUGS.index(slug)
    prev_c, next_c = CARDS[i - 1], CARDS[(i + 1) % len(CARDS)]
    group_label = next(label for key, label, _ in SUIT_ORDER if key == group_of(card))
    out = [_head(title, desc, path, img, ld)]
    out.append(f"""    <nav class="m-crumb"><a href="/">หน้าแรก</a> › <a href="/tarot">ความหมายไพ่ทาโรต์</a> › <span>ไพ่{_e(th)}</span></nav>
    <article class="m-card">
      <div class="m-hero">
        <img class="m-art" src="{img}" alt="ไพ่ทาโรต์{_e(th)} ({_e(en)}) สำรับ Rider-Waite-Smith" width="300" height="518" />
        <div class="m-intro">
          <p class="m-kicker">{_e(group_label)}</p>
          <h1>ความหมายไพ่{_e(th)}<small>{_e(en)}</small></h1>
          <dl class="m-keys">
            <div><dt>ไพ่ปกติ</dt><dd>{_e(card['upTh'])}</dd></div>
            <div><dt>ไพ่กลับหัว</dt><dd>{_e(card['revTh'])}</dd></div>
          </dl>
        </div>
      </div>
      <section><h2>ความหมายไพ่{_e(th)} (ไพ่ปกติ)</h2><p>{_e(up)}</p></section>
      <section><h2>ความหมายไพ่{_e(th)} กลับหัว</h2><p>{_e(rev)}</p></section>
      <div class="m-topics">
        <section><h3>💗 ความรัก</h3><p>{_e(love)}</p></section>
        <section><h3>💼 การงาน</h3><p>{_e(work)}</p></section>
        <section><h3>💰 การเงิน</h3><p>{_e(money)}</p></section>
      </div>
    </article>
""")
    out.append(_cta(f"ได้ไพ่{th}แล้วสงสัยว่าหมายถึงอะไรกับเรื่องของคุณ?"))
    out.append(f"""    <nav class="m-pager">
      <a href="/tarot/{slugify(prev_c['nameEn'])}">‹ ไพ่{_e(short_th(prev_c))}</a>
      <a href="/tarot">ไพ่ทั้งหมด</a>
      <a href="/tarot/{slugify(next_c['nameEn'])}">ไพ่{_e(short_th(next_c))} ›</a>
    </nav>
""")
    out.append(FOOT)
    return "".join(out).encode("utf-8")
