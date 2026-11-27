"""Server-rendered /oracle page: all 37 Ask the Moon oracle cards and their meanings."""

from __future__ import annotations

from typing import Any

import oracle
import tarot_pages

SITE = tarot_pages.SITE
_e = tarot_pages._e
_head = tarot_pages._head
_breadcrumb = tarot_pages._breadcrumb

PATHS = ["/oracle"]

CAT_BLURB = {
    "time": (
        "ชุดเวลา (พื้นหลังน้ำเงินดำ) · 8 ใบ",
        "ไพ่ชุดนี้บอกจังหวะ — เรื่องจะสุกเมื่อไหร่ และควรเร่งหรือควรรอ",
    ),
    "emotion": (
        "ชุดอารมณ์ (พื้นหลังน้ำตาล) · 19 ใบ",
        "ไพ่ชุดนี้บอกอารมณ์ที่อยู่ในเรื่อง — ของคุณ หรือของอีกฝ่าย ตามคำถามที่ถาม",
    ),
    "words": (
        "ชุดคำพูด (พื้นหลังเขียว) · 10 ใบ",
        "ไพ่ชุดนี้เป็นคำแนะนำหรือข้อความจากไพ่ — สิ่งที่ควรทำหรือควรระวังตอนนี้",
    ),
}

FOOT = """  </main>
  <footer class="m-foot">
    <p>ความหมายไพ่ออราเคิลเขียนโดยถามจันทร์ เพื่อเป็นแนวทางในการอ่านไพ่ ไม่ใช่คำแนะนำทางการแพทย์ กฎหมาย หรือการเงิน</p>
    <p>ภาพไพ่: สำรับออราเคิลถามจันทร์ 37 ใบ · ถามจันทร์ / Ask the Moon</p>
    <p><a href="/">หน้าแรก</a> · <a href="/oracle">ไพ่ออราเคิล 37 ใบ</a> · <a href="/tarot">ความหมายไพ่ทาโรต์ทั้ง 78 ใบ</a> · <a href="/privacy">นโยบายความเป็นส่วนตัว</a> · <a href="/terms">ข้อกำหนดการใช้งาน</a></p>
  </footer>
</body>
</html>
"""


def _thumb_size() -> tuple[int, int]:
    return 150, 204  # 480×654 displayed at 150 wide


def render_index() -> bytes:
    title = "ไพ่ออราเคิลถามจันทร์ 37 ใบ ความหมายภาษาไทยและอังกฤษ | ถามจันทร์"
    desc = (
        "สำรับไพ่ออราเคิลถามจันทร์ 37 ใบ แบ่งเป็นชุดเวลา อารมณ์ และคำพูด "
        "อ่านความหมายครบทั้งไทยและอังกฤษ แล้วถามไพ่ออนไลน์ที่ถามจันทร์ สมัครฟรี ถามฟรี 1 ข้อ"
    )
    ld = [
        _breadcrumb([("หน้าแรก", "/"), ("ไพ่ออราเคิล 37 ใบ", "/oracle")]),
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": title,
            "description": desc,
            "url": SITE + "/oracle",
            "inLanguage": "th",
        },
    ]
    tw, th = _thumb_size()
    out = [_head(title, desc, "/oracle", "/og-image.jpg", ld)]
    out.append("""    <nav class="m-crumb"><a href="/">หน้าแรก</a> › <span>ไพ่ออราเคิล 37 ใบ</span></nav>
    <h1>ไพ่ออราเคิลถามจันทร์ 37 ใบ</h1>
    <p class="m-lede">สำรับออราเคิลของถามจันทร์มี 37 ใบ ชื่อบนไพ่เป็นภาษาอังกฤษ ความหมายภาษาไทยอยู่ที่หน้านี้ และในคำทำนายหลังจั่วไพ่ พื้นหลังบอกหมวด: น้ำเงินดำคือเวลา น้ำตาลคืออารมณ์ เขียวคือคำพูด เลือกได้ 1–3 ใบจากทั้งสำรับต่อหนึ่งคำถาม</p>
    <nav class="m-jump">
      <a href="#time">เวลา</a>
      <a href="#emotion">อารมณ์</a>
      <a href="#words">คำพูด</a>
    </nav>
""")
    for cat in ("time", "emotion", "words"):
        label, blurb = CAT_BLURB[cat]
        out.append(f'    <section class="m-suit" id="{cat}">\n      <h2>{_e(label)}</h2>\n      <p class="m-blurb">{_e(blurb)}</p>\n')
        for card in oracle.BY_CATEGORY[cat]:
            cid = card["id"]
            src = oracle.thumb_path(cid)
            out.append(f"""      <article class="m-oracle" id="{_e(cid)}">
        <img src="{_e(src)}" alt="ไพ่{_e(card['nameTh'])} ({_e(card['nameEn'])})" width="{tw}" height="{th}" loading="lazy" />
        <div>
          <p class="m-kicker">{_e(str(card['number']).zfill(2))} · {_e(oracle.CATEGORIES[cat]['th'])}</p>
          <h3>{_e(card['nameTh'])}<small>{_e(card['nameEn'])}</small></h3>
          <p>{_e(card['textTh'])}</p>
          <p class="m-en">{_e(card['textEn'])}</p>
        </div>
      </article>
""")
        out.append("    </section>\n")
    out.append("""    <section class="m-cta">
      <p class="m-cta-title">อยากให้ออราเคิลถามจันทร์ตอบคำถามของคุณ?</p>
      <p>พิมพ์คำถาม แล้วเลือกไพ่ 1–3 ใบ · สมัครฟรี ถามฟรี 1 ข้อ</p>
      <a class="m-btn" href="/?deck=oracle#oracle">ถามไพ่ออราเคิลที่ foolmoon.lol</a>
    </section>
""")
    out.append(FOOT)
    return "".join(out).encode("utf-8")
