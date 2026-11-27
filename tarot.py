"""The 78-card Rider-Waite-Smith tarot deck with short Thai + English meanings.

Card art: Pamela Colman Smith, 1909 (public domain), from Wikimedia Commons;
see static/tarot/SOURCES.json for the file page of every card.
Cards are drawn without positions: the three are read together as one story.
"""

from __future__ import annotations

import re
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


IMAGE_VERSION = "3"  # bump when the card art changes, so browsers fetch the new files
THUMB_VERSION = "1"  # bump when the thumbnail files are regenerated


def image_path(card_id: str) -> str:
    return f"/tarot/{card_id}.webp?v={IMAGE_VERSION}"


def thumb_path(card_id: str) -> str:
    """Small webp for the /tarot index grid and the own-cards picker."""
    return f"/tarot/{card_id}-thumb.webp?v={THUMB_VERSION}"


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


OWN_MIN = 1
OWN_MAX = 5


def card_from_choice(card_id: str, reversed_: bool) -> dict[str, Any]:
    """The same card shape as draw(), for a card the person chose themselves."""
    card = BY_ID[card_id]
    return {
        "id": card["id"],
        "nameEn": card["nameEn"],
        "nameTh": card["nameTh"],
        "reversed": reversed_,
        "meaningEn": card["revEn"] if reversed_ else card["upEn"],
        "meaningTh": card["revTh"] if reversed_ else card["upTh"],
        "image": image_path(card["id"]),
    }


def parse_own_cards(raw: Any) -> list[dict[str, Any]]:
    """Validate cards the person drew from their own deck: 1-5 real, unique cards in their
    drawn order, each {"id": <one of the 78 ids>, "reversed": true|false}. Raises ValueError."""
    if not isinstance(raw, list) or not OWN_MIN <= len(raw) <= OWN_MAX:
        raise ValueError(f"Please choose {OWN_MIN} to {OWN_MAX} cards.")
    out, seen = [], set()
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Invalid card.")
        cid = item.get("id")
        rev = item.get("reversed", False)
        if not isinstance(cid, str) or cid not in BY_ID:
            raise ValueError("Unknown card.")
        if not isinstance(rev, bool):
            raise ValueError("Invalid card orientation.")
        if cid in seen:
            raise ValueError("Each card can be chosen only once.")
        seen.add(cid)
        out.append(card_from_choice(cid, rev))
    return out


def picker_deck() -> list[dict[str, Any]]:
    """Public card list for the own-cards picker (names and images only)."""
    return [{"id": c["id"], "nameEn": c["nameEn"], "nameTh": c["nameTh"],
             "group": "major" if c["arcana"] == "major" else c["id"].split("-")[0],
             "image": thumb_path(c["id"])} for c in DECK]


def prompt_lines(cards: list[dict[str, Any]]) -> str:
    lines = []
    for c in cards:
        orient = "reversed / กลับหัว" if c["reversed"] else "upright / ตั้งตรง"
        lines.append(f"- {c['nameEn']} — {c['nameTh']}, {orient}. Meaning: {c['meaningEn']} / {c['meaningTh']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Direct answers: how the three cards lean, used by the AI prompt and the fallback.
# ---------------------------------------------------------------------------
STRONG_POSITIVE = {"major-19", "major-21", "major-17", "major-10", "major-06", "major-03",
                   "cups-01", "cups-02", "cups-09", "cups-10", "wands-01", "wands-04", "wands-06",
                   "pentacles-01", "pentacles-09", "pentacles-10"}
CHALLENGING = {"major-12", "major-13", "major-15", "major-18", "swords-02", "swords-05", "swords-07",
               "swords-08", "cups-05", "cups-07", "cups-08", "pentacles-05", "wands-05", "wands-10"}
STRONG_CHALLENGING = {"major-16", "swords-03", "swords-09", "swords-10"}


def card_score(card: dict[str, Any]) -> float:
    """How one card leans: + favourable, - unfavourable.

    Every card's reversed score is the exact mirror of its upright score
    (a reversed hard card is relief, a reversed bright card is a setback), so
    with a fair 50/50 orientation the verdicts are symmetric by construction:
    P(yes) == P(no) and P(likely) == P(unlikely). Major Arcana weigh a little more.
    """
    cid = card["id"]
    if cid in STRONG_CHALLENGING:
        base = -2.0
    elif cid in CHALLENGING:
        base = -1.0
    elif cid in STRONG_POSITIVE:
        base = 2.0
    elif cid.startswith("major-"):
        base = 1.5
    else:
        base = 1.0
    return -base if card["reversed"] else base


VERDICTS = ["no", "unlikely", "not_yet", "likely", "yes"]
YES_AT = 3.0     # score >= 3        -> yes      (mirror: <= -3 -> no)
LIKELY_AT = 1.0  # 1 <= score < 3    -> likely   (mirror: -3 < score <= -1 -> unlikely)


def verdict(cards: list[dict[str, Any]]) -> str:
    return verdict_for_score(sum(card_score(c) for c in cards))


def verdict_scaled(cards: list[dict[str, Any]]) -> str:
    """Lean for any number of cards on the same scale as a 3-card draw (score * 3 / n),
    so 1 or 5 chosen cards are judged like the usual three. Equals verdict() for 3 cards."""
    if not cards:
        return "not_yet"
    return verdict_for_score(sum(card_score(c) for c in cards) * DRAW_COUNT / len(cards))


def verdict_for_score(score: float) -> str:
    if score >= YES_AT:
        return "yes"
    if score >= LIKELY_AT:
        return "likely"
    if score > -LIKELY_AT:
        return "not_yet"
    if score > -YES_AT:
        return "unlikely"
    return "no"


VERDICT_HINT_EN = {
    "yes": "clearly YES / clearly positive",
    "likely": "LIKELY YES, with a condition the person must act on",
    "not_yet": "NOT YET / not now: it isn't ripe, it needs time or a change first",
    "unlikely": "LIKELY NO / mostly unfavourable",
    "no": "clearly NO / clearly unfavourable",
}

_YESNO_TH = ("ไหม", "มั้ย", "หรือไม่", "หรือเปล่า", "รึเปล่า", "ป่าว", "ไม๊", "มัย", "ใช่ไหม", "หรือยัง")
_YESNO_EN = ("will ", "is ", "are ", "should ", "can ", "could ", "does ", "do ", "did ", "would ", "am ", "has ", "have ")


def is_yes_no(question: str) -> bool:
    q = (question or "").strip().lower().rstrip("?？!. ")
    return any(q.endswith(e) for e in _YESNO_TH) or q.startswith(_YESNO_EN)


ANSWER_TH = {
    True: {
        "yes": "คำตอบคือ ใช่ค่ะ ไพ่ทั้งสามใบไปในทางบวกชัดเจน",
        "likely": "คำตอบคือ มีแนวโน้มสูงว่าใช่ค่ะ แต่ต้องลงมือเองด้วย ไม่ใช่รอเฉย ๆ",
        "not_yet": "คำตอบคือ ยังไม่ใช่ตอนนี้ค่ะ เรื่องนี้ยังไม่สุก ต้องรออีกระยะหรือเปลี่ยนบางอย่างก่อน",
        "unlikely": "คำตอบคือ มีแนวโน้มว่าไม่ค่ะ ไพ่ส่วนใหญ่ยังไม่เป็นใจกับเรื่องนี้",
        "no": "คำตอบตรง ๆ คือ ไม่ค่ะ ไพ่ชี้ชัดว่าเรื่องนี้ไม่เป็นไปตามที่หวัง",
    },
    False: {
        "yes": "ไพ่ตอบชัดว่าเรื่องนี้ไปในทางที่ดีมากค่ะ",
        "likely": "ไพ่ตอบว่าเรื่องนี้ไปในทางที่ดี แต่ต้องลงมือเองด้วยค่ะ",
        "not_yet": "ไพ่ตอบว่าเรื่องนี้ยังไม่ถึงเวลาค่ะ ตอนนี้ยังไม่ชัดและยังไม่ควรเร่ง",
        "unlikely": "ไพ่ตอบตรง ๆ ว่าเรื่องนี้ยังไม่เป็นใจค่ะ มีอุปสรรคมากกว่าแรงหนุน",
        "no": "ไพ่ตอบชัดว่าเรื่องนี้ไม่ไปในทางที่หวังค่ะ",
    },
}
ANSWER_EN = {
    True: {
        "yes": "The answer is yes. All three cards lean clearly positive.",
        "likely": "The answer is most likely yes, but you have to act on it, not just wait.",
        "not_yet": "The answer is not yet. This isn't ripe; it needs more time or a change first.",
        "unlikely": "The answer is most likely no. Most of the cards are against it right now.",
        "no": "The honest answer is no. The cards clearly show this won't go the way you hope.",
    },
    False: {
        "yes": "The cards say this is heading somewhere very good.",
        "likely": "The cards say this goes well, as long as you take action yourself.",
        "not_yet": "The cards say it isn't time yet; nothing is settled, so don't force it.",
        "unlikely": "The cards say plainly that this isn't favoured; there are more obstacles than support.",
        "no": "The cards clearly say this won't go the way you hope.",
    },
}

# One concrete action per suit (taken from the strongest card's suit).
ACTION = {
    "wands": ("ลงมือก่อนภายในสัปดาห์นี้ ติดต่อหรือเริ่มขั้นแรกเอง อย่ารอให้อีกฝ่ายขยับ",
              "Make the first move this week: reach out or start step one yourself."),
    "cups": ("พูดความรู้สึกหรือความต้องการของคุณออกไปตรง ๆ หนึ่งครั้ง แล้วดูว่าอีกฝ่ายตอบอย่างไร",
             "Say what you feel or want plainly, once, and watch how the other side responds."),
    "swords": ("หาข้อมูลให้ครบแล้วตัดสินใจให้ชัด อย่าปล่อยให้ความคิดวนอยู่ที่เดิม",
               "Get the facts straight and make a clear decision; don't let it keep circling in your head."),
    "pentacles": ("วางแผนเป็นขั้นตอนเรื่องเงินและเวลา ทำทีละขั้นแบบสม่ำเสมอ",
                  "Make a step-by-step plan for money and time, and keep at it steadily."),
    "major": ("ตั้งใจให้ชัดว่าต้องการอะไรจริง ๆ แล้วตัดสิ่งที่ไม่ใช่ออก",
              "Get clear on what you truly want and cut what isn't it."),
}

TIMING = {
    "wands": ("เร็ว ภายในไม่กี่วันถึง 2 สัปดาห์", "fast, within days to two weeks"),
    "swords": ("เร็วแต่ต้องตัดสินใจก่อน ภายใน 1–3 สัปดาห์", "quick once a decision is made, 1–3 weeks"),
    "cups": ("ประมาณ 2–6 สัปดาห์", "around 2–6 weeks"),
    "pentacles": ("ช้าแต่มั่นคง ประมาณ 1–3 เดือน", "slow but steady, about 1–3 months"),
    "major": ("เป็นจังหวะชีวิตครั้งใหญ่ ใช้เวลาหลายเดือน", "a bigger life chapter, over several months"),
}
DAYS = {"wands": ("วันอังคาร", "Tuesday"), "cups": ("วันจันทร์", "Monday"), "swords": ("วันพุธ", "Wednesday"),
        "pentacles": ("วันศุกร์", "Friday"), "major": ("วันอาทิตย์", "Sunday")}
COLORS = {
    "wands": {"th": "ส้มไฟ", "en": "Flame orange", "hex": "#f08a3c"},
    "cups": {"th": "ฟ้าน้ำทะเล", "en": "Sea blue", "hex": "#5aa9e6"},
    "swords": {"th": "เงินหมอก", "en": "Mist silver", "hex": "#c9d1de"},
    "pentacles": {"th": "เขียวมรกต", "en": "Emerald", "hex": "#3fa36b"},
    "major": {"th": "ม่วงลาเวนเดอร์", "en": "Lavender", "hex": "#b79cff"},
}


def suit_of(card_id: str) -> str:
    return card_id.split("-")[0]


def card_number(card_id: str) -> int:
    return int(card_id.split("-")[1])


def _short(card: dict[str, Any], lang: str) -> str:
    if lang == "th":
        return "ไพ่" + re.sub(r"\s*\(.*\)$", "", card["nameTh"]) + (" กลับหัว" if card["reversed"] else "")
    return card["nameEn"] + (" reversed" if card["reversed"] else "")


def best_and_worst(cards: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    ranked = sorted(cards, key=card_score)
    return ranked[-1], ranked[0]


def dominant_suit(cards: list[dict[str, Any]]) -> str:
    best, _ = best_and_worst(cards)
    suits = [suit_of(c["id"]) for c in cards]
    for s in suits:
        if suits.count(s) >= 2:
            return s
    return suit_of(best["id"])


def fallback_reading(name: str, question: str, topic_th: str, topic_en: str,
                     cards: list[dict[str, Any]], lang: str, lean: str | None = None) -> str:
    """Direct, cards-only answer used when the AI is unavailable."""
    v = lean or verdict(cards)
    yn = is_yes_no(question)
    best, worst = best_and_worst(cards)
    act_th, act_en = ACTION[suit_of(best["id"])]
    th = lang == "th"
    if th:
        about = f"เรื่อง «{question}»" if question else "ในภาพรวมตอนนี้"
        p1 = f"{name}ค่ะ {about} — {ANSWER_TH[yn][v]}"
        cards_txt = " · ".join(f"{_short(c, 'th')}: {c['meaningTh']}" for c in cards)
        if v in ("yes", "likely"):
            link = f"แรงหนุนหลักมาจาก{_short(best, 'th')} ซึ่งชี้ว่าคุณมีโอกาสจริง"
        elif v == "not_yet":
            link = f"มีทั้งแรงหนุนและแรงฉุด โดยเฉพาะ{_short(worst, 'th')} ที่ทำให้เรื่องนี้ยังค้างอยู่"
        else:
            link = f"ตัวที่ฉุดไว้ชัดที่สุดคือ{_short(worst, 'th')} ซึ่งยังไม่คลี่คลายง่าย ๆ"
        p2 = f"ไพ่ที่ออก: {cards_txt}. เมื่ออ่านรวมกัน {link}."
        m = worst["meaningTh"]
        caution = (f"ระวัง{m}" if m.startswith("เรื่อง") else f"ระวังเรื่อง{m}") if card_score(worst) < 0 \
            else "อย่าประมาทแม้ทิศทางจะดี"
        if v in ("unlikely", "no"):
            act_th = "ถ้ายังอยากผลักดันเรื่องนี้ " + act_th + " แต่ควรเตรียมทางเลือกอื่นไว้ด้วย"
        p3 = f"คำแนะนำ: 1) {act_th} 2) {caution}."
        return "\n\n".join([p1, p2, p3])
    about = f"about “{question}”" if question else "about your life right now"
    p1 = f"{name}, {about}: {ANSWER_EN[yn][v]}"
    cards_txt = " · ".join(f"{_short(c, 'en')}: {c['meaningEn']}" for c in cards)
    if v in ("yes", "likely"):
        link = f"the main support comes from {_short(best, 'en')}, which shows a real opening for you"
    elif v == "not_yet":
        link = f"there is support and resistance, and {_short(worst, 'en')} is what keeps this unsettled"
    else:
        link = f"the clearest block is {_short(worst, 'en')}, and it won't lift easily"
    p2 = f"The cards: {cards_txt}. Read together, {link}."
    caution = f"watch out for {worst['meaningEn']}" if card_score(worst) < 0 else "don't get careless even though it looks good"
    if v in ("unlikely", "no"):
        act_en = "If you still want to push for it: " + act_en[0].lower() + act_en[1:] + " Keep another option ready too."
    p3 = f"Advice: 1) {act_en} 2) {caution[0].upper() + caution[1:]}."
    return "\n\n".join([p1, p2, p3])


def premium_from_cards(cards: list[dict[str, Any]], lang: str) -> dict[str, Any]:
    """The deep (paid) section, built only from the drawn cards."""
    th = lang == "th"
    best, worst = best_and_worst(cards)
    suit = dominant_suit(cards)
    slow = sum(c["reversed"] for c in cards) >= 2
    timing_th, timing_en = TIMING[suit]
    if slow:
        timing_th += " (ไพ่กลับหัวหลายใบ อาจช้ากว่านั้น)"
        timing_en += " (several reversed cards: possibly slower)"
    nums = []
    for c in cards:
        n = card_number(c["id"]) or 22
        if n not in nums:
            nums.append(n)
    total = sum(nums)
    while total > 9 and total not in (11, 22):
        total = sum(int(d) for d in str(total))
    if total not in nums:
        nums.append(total)
    colors, seen = [], set()
    for c in cards:
        s = suit_of(c["id"])
        if s not in seen:
            seen.add(s)
            colors.append(COLORS[s])
    act_th, act_en = ACTION[suit]
    return {
        "forecast": timing_th if th else timing_en,
        "gift": f"{_short(best, lang)} — {best['meaningTh'] if th else best['meaningEn']}",
        "shadow": f"{_short(worst, lang)} — {worst['meaningTh'] if th else worst['meaningEn']}",
        "compatibility": act_th if th else act_en,
        "numbers": nums,
        "colors": colors,
        "day": DAYS[suit][0 if th else 1],
    }
