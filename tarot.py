"""The 78-card Rider-Waite-Smith tarot deck with short Thai + English meanings.

Card art: Pamela Colman Smith, 1909 (public domain), from Wikimedia Commons;
see static/tarot/SOURCES.json for the file page of every card.
Cards are drawn without positions: the three are read together as one story.
"""

from __future__ import annotations

import secrets
from typing import Any

HEADING_TH = "ให้ไพ่เล่าเรื่องราว"
HEADING_EN = "Let the cards tell the story"
DRAW_COUNT = 3

# id, English name, Thai name, upright EN, reversed EN, upright TH, reversed TH
MAJOR = [
    ("major-00", "The Fool", "คนโง่ (The Fool)",
     "a fresh start, trust, and a leap of faith", "recklessness or fear of taking the first step",
     "การเริ่มต้นใหม่ ความกล้า และการก้าวออกไปด้วยใจเปิด", "ความประมาท หรือความกลัวจนไม่กล้าเริ่ม"),
    ("major-01", "The Magician", "นักมายากล (The Magician)",
     "willpower, skill, and turning ideas into reality", "scattered energy or untapped talent",
     "พลังใจ ความสามารถ และการทำความคิดให้เป็นจริง", "พลังกระจัดกระจาย หรือศักยภาพที่ยังไม่ได้ใช้"),
    ("major-02", "The High Priestess", "นักบวชหญิง (The High Priestess)",
     "intuition, inner knowing, and quiet secrets", "ignoring your inner voice",
     "สัญชาตญาณ ปัญญาภายใน และความลับที่ค่อย ๆ เผย", "การมองข้ามเสียงในใจตัวเอง"),
    ("major-03", "The Empress", "จักรพรรดินี (The Empress)",
     "abundance, nurturing, and creativity", "neglecting self-care or creative block",
     "ความอุดมสมบูรณ์ การโอบอุ้ม และความคิดสร้างสรรค์", "การละเลยการดูแลตัวเอง หรือความคิดสร้างสรรค์ติดขัด"),
    ("major-04", "The Emperor", "จักรพรรดิ (The Emperor)",
     "structure, leadership, and stability", "rigidity or struggles over control",
     "ความมั่นคง ความเป็นผู้นำ และระเบียบวินัย", "ความแข็งตัวเกินไป หรือการแย่งอำนาจควบคุม"),
    ("major-05", "The Hierophant", "พระสังฆราช (The Hierophant)",
     "tradition, guidance, and shared values", "breaking convention to find your own way",
     "ขนบธรรมเนียม ผู้ชี้แนะ และคุณค่าที่ยึดถือร่วมกัน", "การแหกกรอบเดิมเพื่อหาทางของตัวเอง"),
    ("major-06", "The Lovers", "คนรัก (The Lovers)",
     "love, harmony, and a heartfelt choice", "imbalance or a choice made against your values",
     "ความรัก ความกลมเกลียว และการเลือกด้วยหัวใจ", "ความไม่สมดุล หรือการเลือกที่ขัดกับใจตัวเอง"),
    ("major-07", "The Chariot", "รถศึก (The Chariot)",
     "determination, momentum, and victory", "losing direction or pulling in two ways",
     "ความมุ่งมั่น แรงขับเคลื่อน และชัยชนะ", "การหลงทิศ หรือแรงที่ดึงไปคนละทาง"),
    ("major-08", "Strength", "พลัง (Strength)",
     "gentle courage, patience, and inner strength", "self-doubt or low energy",
     "ความกล้าที่อ่อนโยน ความอดทน และพลังภายใน", "ความไม่มั่นใจในตัวเอง หรือพลังที่อ่อนล้า"),
    ("major-09", "The Hermit", "ฤๅษี (The Hermit)",
     "reflection, solitude, and seeking inner truth", "isolation or avoiding needed reflection",
     "การใคร่ครวญ ความสงบ และการค้นหาความจริงภายใน", "การแยกตัวมากเกินไป หรือหลีกเลี่ยงการทบทวนตัวเอง"),
    ("major-10", "Wheel of Fortune", "กงล้อแห่งโชคชะตา (Wheel of Fortune)",
     "turning luck, cycles, and destiny in motion", "a pause in luck or resisting change",
     "โชคที่หมุนเวียน วัฏจักร และโชคชะตาที่กำลังเคลื่อน", "โชคชะลอตัว หรือการต้านความเปลี่ยนแปลง"),
    ("major-11", "Justice", "ความยุติธรรม (Justice)",
     "fairness, truth, and cause and effect", "imbalance or avoiding accountability",
     "ความยุติธรรม ความจริง และผลของการกระทำ", "ความไม่เป็นธรรม หรือการเลี่ยงความรับผิดชอบ"),
    ("major-12", "The Hanged Man", "คนแขวน (The Hanged Man)",
     "surrender, a new perspective, and a meaningful pause", "stalling or resisting what must be let go",
     "การปล่อยวาง มุมมองใหม่ และการหยุดพักที่มีความหมาย", "การยื้อเวลา หรือไม่ยอมปล่อยสิ่งที่ควรปล่อย"),
    ("major-13", "Death", "ความตาย (Death)",
     "an ending that clears the way for transformation", "fear of change or holding on to the past",
     "การสิ้นสุดเพื่อเปิดทางสู่การเปลี่ยนแปลงครั้งใหม่ (ไม่ใช่ความตายจริง)", "ความกลัวการเปลี่ยนแปลง หรือการยึดติดอดีต"),
    ("major-14", "Temperance", "ความพอดี (Temperance)",
     "balance, moderation, and healing", "excess or impatience",
     "ความสมดุล ความพอดี และการเยียวยา", "ความสุดโต่ง หรือความใจร้อน"),
    ("major-15", "The Devil", "ปีศาจ (The Devil)",
     "temptation, attachment, and patterns that bind", "breaking free and reclaiming your power",
     "สิ่งยั่วยุ การยึดติด และนิสัยที่พันธนาการ", "การหลุดพ้นและเรียกพลังของตัวเองกลับคืน"),
    ("major-16", "The Tower", "หอคอย (The Tower)",
     "sudden change and a revelation that frees", "avoiding a needed shake-up",
     "การเปลี่ยนแปลงฉับพลัน และความจริงที่เผยออกมาเพื่อปลดปล่อย", "การเลี่ยงความเปลี่ยนแปลงที่จำเป็น"),
    ("major-17", "The Star", "ดวงดาว (The Star)",
     "hope, renewal, and calm inspiration", "lost faith or discouragement",
     "ความหวัง การฟื้นฟู และแรงบันดาลใจอันสงบ", "ความท้อแท้ หรือหมดศรัทธาชั่วคราว"),
    ("major-18", "The Moon", "ดวงจันทร์ (The Moon)",
     "dreams, intuition, and the unknown", "confusion lifting and truth coming to light",
     "ความฝัน สัญชาตญาณ และสิ่งที่ยังไม่ชัดเจน", "ความสับสนคลี่คลาย ความจริงเริ่มปรากฏ"),
    ("major-19", "The Sun", "ดวงอาทิตย์ (The Sun)",
     "joy, success, and warm vitality", "temporary clouds over happiness",
     "ความสุข ความสำเร็จ และพลังชีวิตที่สดใส", "เมฆบดบังความสุขชั่วคราว"),
    ("major-20", "Judgement", "การพิพากษา (Judgement)",
     "awakening, renewal, and an inner calling", "self-doubt or ignoring the call",
     "การตื่นรู้ การเริ่มใหม่ และเสียงเรียกจากภายใน", "ความลังเลสงสัยในตัวเอง หรือการเมินเสียงเรียก"),
    ("major-21", "The World", "โลก (The World)",
     "completion, fulfillment, and wholeness", "unfinished business or a delayed ending",
     "ความสำเร็จสมบูรณ์ การบรรลุ และความครบถ้วน", "เรื่องที่ยังค้างคา หรือบทสรุปที่ล่าช้า"),
]

SUITS = {
    "wands": ("Wands", "ไม้เท้า"),
    "cups": ("Cups", "ถ้วย"),
    "swords": ("Swords", "ดาบ"),
    "pentacles": ("Pentacles", "เหรียญ"),
}
RANKS = {
    1: ("Ace", "เอซ"), 2: ("Two", "สอง"), 3: ("Three", "สาม"), 4: ("Four", "สี่"), 5: ("Five", "ห้า"),
    6: ("Six", "หก"), 7: ("Seven", "เจ็ด"), 8: ("Eight", "แปด"), 9: ("Nine", "เก้า"), 10: ("Ten", "สิบ"),
    11: ("Page", "เพจ"), 12: ("Knight", "อัศวิน"), 13: ("Queen", "ราชินี"), 14: ("King", "ราชา"),
}

# (upright EN, reversed EN, upright TH, reversed TH) per suit, ranks 1..14
MINOR = {
    "wands": [
        ("a spark of inspiration and new passion", "delays or a creative spark that fades",
         "ประกายแรงบันดาลใจและไฟแห่งความหลงใหลใหม่", "ความล่าช้า หรือไฟที่มอดลงก่อนเริ่ม"),
        ("planning ahead and choosing a direction", "fear of the unknown or poor planning",
         "การวางแผนและเลือกเส้นทางข้างหน้า", "ความกลัวสิ่งที่ไม่รู้ หรือแผนที่ยังไม่รัดกุม"),
        ("expansion and opportunities on the horizon", "obstacles or slow progress",
         "การขยายตัวและโอกาสที่กำลังมาถึง", "อุปสรรค หรือความคืบหน้าที่ช้า"),
        ("celebration, home, and harmony", "tension at home or a postponed celebration",
         "การเฉลิมฉลอง ความอบอุ่นในบ้าน และความกลมเกลียว", "ความตึงเครียดในบ้าน หรืองานฉลองที่เลื่อนออกไป"),
        ("healthy competition and clashing ideas", "avoiding conflict or inner tension",
         "การแข่งขันและความคิดที่ปะทะกัน", "การหลีกเลี่ยงความขัดแย้ง หรือความตึงเครียดในใจ"),
        ("recognition and well-earned success", "self-doubt or waiting for praise",
         "การได้รับการยอมรับและความสำเร็จที่สมควร", "ความไม่มั่นใจ หรือการรอคำชมจากผู้อื่น"),
        ("standing your ground with courage", "feeling overwhelmed or giving up",
         "การยืนหยัดปกป้องจุดยืนอย่างกล้าหาญ", "ความรู้สึกถูกกดดันจนอยากยอมแพ้"),
        ("swift movement and news arriving fast", "delays or frustration",
         "ความเคลื่อนไหวรวดเร็วและข่าวที่มาไว", "ความล่าช้าหรือความหงุดหงิด"),
        ("resilience and the last push before success", "exhaustion or defensiveness",
         "ความอดทนและแรงฮึดสุดท้ายก่อนสำเร็จ", "ความเหนื่อยล้าหรือการตั้งการ์ดมากเกินไป"),
        ("carrying heavy responsibility", "learning to delegate and lighten the load",
         "ภาระความรับผิดชอบที่หนักอึ้ง", "การเรียนรู้ที่จะแบ่งเบาและวางภาระลง"),
        ("enthusiasm, curiosity, and exciting news", "scattered ideas or hesitation",
         "ความกระตือรือร้น ความอยากรู้ และข่าวดีที่น่าตื่นเต้น", "ความคิดกระจัดกระจายหรือความลังเล"),
        ("bold action and adventure", "impulsiveness or haste",
         "การลงมือทำอย่างกล้าหาญและการผจญภัย", "ความหุนหันพลันแล่นหรือความรีบร้อน"),
        ("confidence, warmth, and determination", "jealousy or low self-confidence",
         "ความมั่นใจ ความอบอุ่น และความมุ่งมั่น", "ความอิจฉาหรือความมั่นใจที่ลดลง"),
        ("visionary leadership", "high expectations or impatience",
         "ผู้นำที่มีวิสัยทัศน์", "การคาดหวังสูงเกินไปหรือความใจร้อน"),
    ],
    "cups": [
        ("new love and an open heart", "holding back feelings",
         "ความรักครั้งใหม่และหัวใจที่เปิดกว้าง", "การเก็บกดความรู้สึก"),
        ("partnership and mutual attraction", "imbalance in a relationship",
         "ความสัมพันธ์คู่และแรงดึงดูดซึ่งกันและกัน", "ความไม่สมดุลในความสัมพันธ์"),
        ("friendship and celebration", "too much indulgence or gossip",
         "มิตรภาพและการเฉลิมฉลอง", "การหลงระเริงหรือเรื่องซุบซิบ"),
        ("contemplation and reconsidering offers", "new awareness and accepting offers",
         "การทบทวนและพิจารณาข้อเสนอใหม่อีกครั้ง", "การตื่นรู้และยอมรับโอกาสที่ยื่นมา"),
        ("grief over a loss", "acceptance and moving on",
         "ความเสียใจกับสิ่งที่สูญเสีย", "การยอมรับและก้าวต่อไป"),
        ("sweet memories and innocence", "living too much in the past",
         "ความทรงจำที่อบอุ่นและความไร้เดียงสา", "การจมอยู่กับอดีตมากเกินไป"),
        ("many choices and daydreams", "clarity and a firm decision",
         "ทางเลือกมากมายและความฝันกลางวัน", "ความชัดเจนและการตัดสินใจอย่างหนักแน่น"),
        ("walking away to seek deeper meaning", "fear of change or staying too long",
         "การเดินจากไปเพื่อค้นหาความหมายที่ลึกซึ้งกว่า", "ความกลัวการเปลี่ยนแปลงหรืออยู่นานเกินควร"),
        ("wishes fulfilled and contentment", "inner happiness over material wishes",
         "ความปรารถนาที่สมหวังและความพอใจ", "ความสุขภายในสำคัญกว่าความต้องการทางวัตถุ"),
        ("emotional fulfillment and family harmony", "disconnection at home",
         "ความสุขสมบูรณ์ทางใจและครอบครัวที่กลมเกลียว", "ความห่างเหินภายในบ้าน"),
        ("a sweet message and creative intuition", "emotional immaturity or a creative block",
         "ข่าวดีทางใจและสัญชาตญาณสร้างสรรค์", "อารมณ์ที่ยังไม่มั่นคงหรือความคิดสร้างสรรค์ติดขัด"),
        ("romance, charm, and following your heart", "moodiness or unrealistic hopes",
         "ความโรแมนติก เสน่ห์ และการทำตามหัวใจ", "อารมณ์แปรปรวนหรือความหวังที่เกินจริง"),
        ("compassion, calm, and emotional wisdom", "self-care needed or emotional overwhelm",
         "ความเมตตา ความสงบ และปัญญาทางอารมณ์", "ถึงเวลาดูแลใจตัวเอง หรืออารมณ์ท่วมท้น"),
        ("emotional balance and generosity", "moodiness or suppressed feelings",
         "ความสมดุลทางอารมณ์และความเอื้อเฟื้อ", "อารมณ์แปรปรวนหรือการเก็บกดความรู้สึก"),
    ],
    "swords": [
        ("a breakthrough and mental clarity", "confusion or misused words",
         "ความคิดที่ทะลุปรุโปร่งและความชัดเจน", "ความสับสนหรือคำพูดที่ใช้ผิดทาง"),
        ("a difficult choice or a stalemate", "information coming out and indecision easing",
         "ทางเลือกที่ยากหรือภาวะชะงักงัน", "ข้อมูลเริ่มเผยและความลังเลค่อย ๆ คลาย"),
        ("heartache and painful truth", "healing and forgiveness",
         "ความเจ็บปวดทางใจและความจริงที่ปวดร้าว", "การเยียวยาและการให้อภัย"),
        ("rest, recovery, and stillness", "restlessness or burnout",
         "การพักผ่อน ฟื้นฟู และความสงบนิ่ง", "ความกระสับกระส่ายหรือหมดไฟ"),
        ("conflict and winning at a cost", "reconciliation and letting go of a grudge",
         "ความขัดแย้งและชัยชนะที่ต้องแลกมา", "การคืนดีและปล่อยวางความขุ่นเคือง"),
        ("transition toward calmer waters", "unfinished business or resistance to moving",
         "การเปลี่ยนผ่านไปสู่ช่วงที่สงบกว่า", "เรื่องที่ยังค้างคาหรือไม่อยากขยับ"),
        ("strategy and acting discreetly", "coming clean or rethinking a plan",
         "กลยุทธ์และการเดินเกมอย่างแนบเนียน", "การเปิดเผยความจริงหรือทบทวนแผนใหม่"),
        ("feeling stuck by your own thoughts", "release and new perspectives",
         "ความรู้สึกติดกับดักความคิดของตัวเอง", "การปลดปล่อยและมุมมองใหม่"),
        ("worry and sleepless nights", "hope returning and fears easing",
         "ความกังวลและคืนที่นอนไม่หลับ", "ความหวังกลับมาและความกลัวค่อย ๆ จางลง"),
        ("a painful ending, the bottom before rising", "recovery and regeneration",
         "จุดจบที่เจ็บปวด จุดต่ำสุดก่อนจะลุกขึ้นใหม่", "การฟื้นตัวและการเริ่มต้นใหม่"),
        ("curiosity and fresh ideas", "gossip or hasty words",
         "ความอยากรู้และความคิดใหม่ ๆ", "คำนินทาหรือคำพูดที่รีบร้อน"),
        ("ambition and fast action", "rushing or scattered focus",
         "ความทะเยอทะยานและการลงมืออย่างรวดเร็ว", "ความรีบร้อนหรือสมาธิกระเจิง"),
        ("clear boundaries and honest insight", "coldness or harsh judgement",
         "ขอบเขตที่ชัดเจนและความคิดที่ตรงไปตรงมา", "ความเย็นชาหรือการตัดสินที่รุนแรง"),
        ("clear thinking, truth, and authority", "manipulation or misused power",
         "ความคิดที่แจ่มชัด ความจริง และอำนาจที่ชอบธรรม", "การบงการหรือใช้อำนาจผิดทาง"),
    ],
    "pentacles": [
        ("a new financial or career opportunity", "a missed chance or poor planning",
         "โอกาสใหม่ด้านการเงินหรือการงาน", "โอกาสที่หลุดมือหรือการวางแผนไม่รอบคอบ"),
        ("balancing priorities and adaptability", "overload or disorganization",
         "การจัดสมดุลหลายเรื่องและความยืดหยุ่น", "ภาระล้นมือหรือความไม่เป็นระเบียบ"),
        ("teamwork and skilled collaboration", "lack of teamwork",
         "การทำงานเป็นทีมและความร่วมมือที่ลงตัว", "ทีมขาดความร่วมมือ"),
        ("saving and security", "holding on too tightly or overspending",
         "การเก็บออมและความมั่นคง", "การยึดติดเกินไปหรือใช้จ่ายเกินตัว"),
        ("hard times and feeling left out", "recovery from hardship",
         "ช่วงลำบากและความรู้สึกถูกทอดทิ้ง", "การฟื้นตัวจากความยากลำบาก"),
        ("generosity and giving and receiving", "debt or one-sided giving",
         "ความเอื้อเฟื้อ การให้และการรับ", "หนี้สินหรือการให้ที่ไม่สมดุล"),
        ("patience and long-term investment", "impatience over results",
         "ความอดทนและการลงทุนระยะยาว", "ความใจร้อนอยากเห็นผลเร็ว"),
        ("diligence and mastering a craft", "perfectionism or a lack of focus",
         "ความขยันและการฝึกฝนฝีมือ", "ความสมบูรณ์แบบเกินไปหรือขาดสมาธิ"),
        ("independence and self-made comfort", "overwork or financial setbacks",
         "ความเป็นอิสระและความสบายที่สร้างด้วยตัวเอง", "การทำงานหนักเกินไปหรือการเงินสะดุด"),
        ("wealth, family, and lasting legacy", "family or money disputes",
         "ความมั่งคั่ง ครอบครัว และมรดกที่ยั่งยืน", "ความขัดแย้งเรื่องครอบครัวหรือเงินทอง"),
        ("an eager student and a new venture", "procrastination",
         "ผู้ใฝ่เรียนรู้และการเริ่มกิจการใหม่", "การผัดวันประกันพรุ่ง"),
        ("steady progress and reliability", "boredom or stagnation",
         "ความก้าวหน้าอย่างมั่นคงและความน่าเชื่อถือ", "ความเบื่อหน่ายหรือการหยุดนิ่ง"),
        ("nurturing practicality and abundance", "work-life imbalance",
         "ความอบอุ่นที่ใช้ได้จริงและความอุดมสมบูรณ์", "ชีวิตกับงานไม่สมดุล"),
        ("abundance, security, and success", "greed or rigidity with money",
         "ความมั่งคั่ง ความมั่นคง และความสำเร็จ", "ความโลภหรือความตระหนี่เรื่องเงิน"),
    ],
}


def _build_deck() -> list[dict[str, Any]]:
    deck = []
    for cid, en, th, ue, re_, ut, rt in MAJOR:
        deck.append({"id": cid, "nameEn": en, "nameTh": th, "arcana": "major",
                     "upEn": ue, "revEn": re_, "upTh": ut, "revTh": rt})
    for suit, (suit_en, suit_th) in SUITS.items():
        for rank, (ue, re_, ut, rt) in enumerate(MINOR[suit], start=1):
            r_en, r_th = RANKS[rank]
            en = f"{r_en} of {suit_en}"
            deck.append({"id": f"{suit}-{rank:02d}", "nameEn": en, "nameTh": f"{r_th}{suit_th} ({en})",
                         "arcana": "minor", "upEn": ue, "revEn": re_, "upTh": ut, "revTh": rt})
    return deck


DECK: list[dict[str, Any]] = _build_deck()
BY_ID = {c["id"]: c for c in DECK}
_RNG = secrets.SystemRandom()


def image_path(card_id: str) -> str:
    return f"/tarot/{card_id}.webp"


def draw(count: int = DRAW_COUNT) -> list[dict[str, Any]]:
    """Draw distinct cards with OS randomness; each is upright or reversed. No positions."""
    out = []
    for card in _RNG.sample(DECK, count):
        reversed_ = secrets.randbelow(2) == 1
        out.append({
            "id": card["id"],
            "nameEn": card["nameEn"],
            "nameTh": card["nameTh"],
            "reversed": reversed_,
            "meaningEn": card["revEn"] if reversed_ else card["upEn"],
            "meaningTh": card["revTh"] if reversed_ else card["upTh"],
            "image": image_path(card["id"]),
        })
    return out


def prompt_lines(cards: list[dict[str, Any]]) -> str:
    lines = []
    for c in cards:
        orient = "reversed / กลับหัว" if c["reversed"] else "upright / ตั้งตรง"
        lines.append(f"- {c['nameEn']} — {c['nameTh']}, {orient}. Meaning: {c['meaningEn']} / {c['meaningTh']}")
    return "\n".join(lines)


def template_paragraph(cards: list[dict[str, Any]], lang: str) -> str:
    """One flowing story from the cards, for the offline/template reading."""
    if lang == "th":
        names = ", ".join(f"ไพ่{c['nameTh']}{' กลับหัว' if c['reversed'] else ''}" for c in cards)
        ms = [c["meaningTh"] for c in cards]
        themes = ms[0] if len(ms) == 1 else " ประสานกับ".join(ms[:-1]) + " และ" + ms[-1]
        return (f"✦ ไพ่ทาโรต์ที่ปรากฏสำหรับคุณคือ {names}. "
                f"เมื่ออ่านรวมกันเป็นเรื่องเดียว ไพ่บอกถึง{themes} "
                f"— ทั้งหมดนี้กำลังพาคุณไปสู่คำตอบที่ใจคุณรู้อยู่แล้ว ขอให้เชื่อในจังหวะของตัวเองและก้าวไปอย่างอ่อนโยน.")
    names = ", ".join(f"{c['nameEn']}{' reversed' if c['reversed'] else ''}" for c in cards)
    themes = "; ".join(c["meaningEn"] for c in cards)
    return (f"✦ The tarot cards that came to you are {names}. "
            f"Read together as one story, they speak of {themes} "
            f"— all of it leading you toward an answer your heart already knows. Trust your own timing and step forward gently.")
