"""The 37-card Ask the Moon oracle deck (ไพ่ออราเคิลถามจันทร์).

Background color marks the category:
  black-blue = Time (8 cards), brown = Emotion (19 cards), green = Words (10 cards).
English titles are printed on the cards; Thai names and meanings are shown on the site.
A reading draws one card from each category (Timing, Feeling, Counsel). Cards are not
reversed. The server always draws; the face-down pick UI never chooses identities.
"""

from __future__ import annotations

import secrets
from typing import Any

HEADING_TH = "เวลา · อารมณ์ · คำพูด"
HEADING_EN = "Timing · Feeling · Counsel"
DRAW_COUNT = 3
IMAGE_VERSION = "1"
THUMB_VERSION = "1"
BACK_VERSION = "1"

CATEGORIES = {
    "time": {"en": "Timing", "th": "เวลา"},
    "emotion": {"en": "Feeling", "th": "อารมณ์"},
    "words": {"en": "Counsel", "th": "คำพูด"},
}

POSITIONS = [
    {"id": "time", "nameEn": "Timing", "nameTh": "เวลา"},
    {"id": "emotion", "nameEn": "Feeling", "nameTh": "อารมณ์"},
    {"id": "words", "nameEn": "Counsel", "nameTh": "คำพูด"},
]

# id, category, English name, Thai name, short EN, short TH, long EN, long TH, lean score
# Scores feed a yes/no lean: Time is usually 0 (timing only); "Not Yet Time" pulls toward not-yet.
# Emotion and Words carry the emotional / advisory weight.
_CARDS = [
    ("oracle-01", "time", "Within a Day", "ภายในหนึ่งวัน",
     "This comes to a head within a day — watch for a sign or a move very soon.",
     "เรื่องนี้ใกล้แล้ว อาจมีสัญญาณหรือความเคลื่อนไหวภายในหนึ่งวัน",
     "The situation is already in motion. A message, a meeting, or a clear shift is likely within a day. Stay reachable and notice small signals; this is not a time to wait for a later season.",
     "เรื่องเริ่มขยับแล้ว คำตอบหรือสัญญาณมีโอกาสมาภายในหนึ่งวัน อย่าผลัดไปดูทีหลัง เปิดรับข่าวและสังเกตสิ่งเล็ก ๆ รอบตัวไว้",
     0),
    ("oracle-02", "time", "Within a Week", "ภายในหนึ่งสัปดาห์",
     "Give it about a week — an answer or a change should arrive in that window.",
     "อีกไม่นาน ภายในประมาณหนึ่งสัปดาห์จะมีคำตอบหรือการเปลี่ยนแปลง",
     "The pace is short, not instant. Within about a week something should clarify or move. Plan for that window, and do not rush a decision that still needs a few days to ripen.",
     "ไม่ใช่เรื่องของวันนี้ แต่ก็ไม่ต้องรอนาน ภายในประมาณหนึ่งสัปดาห์เรื่องน่าจะชัดขึ้นหรือขยับ วางแผนให้ทันช่วงนี้ และอย่ารีบตัดสินใจในสิ่งที่ยังต้องรออีกสองสามวัน",
     0),
    ("oracle-03", "time", "Within a Month", "ภายในหนึ่งเดือน",
     "Look to the coming month — this takes a little time, not years.",
     "มองไปที่เดือนข้างหน้า เรื่องนี้ใช้เวลาอีกหน่อย แต่ไม่ได้นานเป็นปี",
     "This will not resolve overnight, but it also is not a long wait. A clearer picture or a real step is likely within a month. Use the weeks to prepare rather than to stall.",
     "เรื่องนี้จะไม่จบในข้ามคืน แต่ก็ไม่ต้องรอนานเป็นปี โดยมากจะเห็นภาพชัดขึ้นหรือได้ก้าวจริงภายในหนึ่งเดือน ใช้ช่วงนี้เตรียมตัว อย่าอ้างเวลานี้แล้วเลื่อนไปเรื่อย",
     0),
    ("oracle-04", "time", "Within 3 Months", "ภายในสามเดือน",
     "Give this about three months — it needs a season, not a moment.",
     "ให้เวลาประมาณสามเดือน เรื่องนี้ต้องใช้ระยะ ไม่จบในชั่วข้ามคืน",
     "This unfolds over a season. Within about three months you should see whether it is taking shape. Patience here is practical, not avoidance: do the work in the meantime and review at that mark.",
     "เรื่องนี้ค่อย ๆ ชัดขึ้นเป็นเดือน ภายในประมาณสามเดือนจะพอเห็นว่ามันไปต่อได้หรือไม่ ความอดทนตรงนี้คือการลงมือไปด้วย ไม่ใช่การหนี ทำสิ่งที่ต้องทำไปพลาง ๆ แล้วค่อยทบทวนเมื่อถึงเวลานั้น",
     0),
    ("oracle-05", "time", "Within 6 Months", "ภายในหกเดือน",
     "This sits on a longer clock — expect movement within about six months.",
     "เรื่องนี้ใช้เวลานานกว่านั้น คาดว่าจะขยับภายในประมาณหกเดือน",
     "The timeline is measured in half a year, not in days. Something real can still happen, but only if the foundations are laid now. Do not abandon it, and do not expect a sudden finish.",
     "นี่ไม่ใช่เรื่องของวันนี้หรือสัปดาห์นี้ แต่เป็นระยะประมาณหกเดือน ยังมีโอกาสเกิดเรื่องจริงได้ถ้าเริ่มวางรากตอนนี้ อย่าทิ้งไปเลย แต่ก็อย่าคาดหวังว่าจะจบเร็ว",
     0),
    ("oracle-06", "time", "A Year From Now", "อีกหนึ่งปี",
     "Look about a year ahead — this belongs to a later chapter, not this week.",
     "มองไปข้างหน้าประมาณหนึ่งปี เรื่องนี้อยู่ในบทถัดไป ยังไม่ใช่สัปดาห์นี้",
     "The heart of this sits about a year from now. What you do in the meantime still matters, but judging it by today's pace will only frustrate you. Think in a longer arc.",
     "จุดสำคัญของเรื่องนี้อยู่ข้างหน้าประมาณหนึ่งปี สิ่งที่ทำตอนนี้ยังสำคัญ แต่ถ้าเอาจังหวะของวันนี้มาวัดจะยิ่งหงุดหงิด มองเป็นเรื่องระยะยาวจะตรงกว่า",
     0),
    ("oracle-07", "time", "Beyond a Year", "นานกว่าหนึ่งปี",
     "This is a long road — farther than a year, not a near-term outcome.",
     "เรื่องนี้ใช้เวลานานกว่าหนึ่งปี ยังไม่ใช่ผลที่เห็นในเร็ว ๆ นี้",
     "What you are asking about lives farther out than a year. It may still be worth building toward, but it will not land soon. Adjust hopes and plans to a long horizon, or choose a nearer goal.",
     "สิ่งที่ถามอยู่นั้นไกลกว่าหนึ่งปี อาจยังคุ้มที่จะค่อย ๆ สร้าง แต่จะไม่เห็นผลในเร็ว ๆ นี้ ปรับความหวังและแผนให้เข้ากับระยะนี้ หรือเลือกเป้าหมายที่ใกล้กว่า",
     0),
    ("oracle-08", "time", "Not Yet Time", "ยังไม่ถึงเวลา",
     "It is not the right time — forcing it now will cost more than waiting.",
     "ยังไม่ถึงจังหวะ ถ้าฝืนตอนนี้จะเสียมากกว่าการรอ",
     "The door is not open yet. Pushing, chasing, or deciding in a hurry is likely to backfire. Step back, tend what is in front of you, and return when the ground has actually changed — not just because you are tired of waiting.",
     "ประตูยังไม่เปิด การผลัก ไล่ตาม หรือรีบตัดสินใจตอนนี้มักจะสวนทาง ถอยหนึ่งก้าว ดูแลสิ่งที่อยู่ตรงหน้า แล้วค่อยกลับมาเมื่อสถานการณ์เปลี่ยนจริง ไม่ใช่แค่เพราะรอไม่ไหว",
     -2),
    ("oracle-09", "emotion", "Loves You, Can't Show It", "รักแต่แสดงออกไม่เป็น",
     "There is real fondness here, but it is held back and poorly shown.",
     "มีความรู้สึกจริง แต่เก็บไว้และแสดงออกได้ไม่ดี",
     "The feeling is there, but it does not travel well. Shyness, fear, pride, or circumstance may be muffling it, so the other person (or you) can look cool, inconsistent, or distant even while they care. Look at what is withheld, not only at what is said out loud.",
     "ความรู้สึกมีอยู่ แต่ส่งออกมาไม่สุด ความเขิน ความกลัว ความภูมิใจ หรือสถานการณ์อาจปิดไว้ จึงดูเย็น ไม่คงที่ หรือห่าง แม้ในใจจะมีรัก ดูที่สิ่งที่ยังไม่ได้แสดง ไม่ใช่แค่คำพูดที่ได้ยิน",
     1),
    ("oracle-10", "emotion", "No Feelings", "ไม่มีความรู้สึก",
     "The warmth you hoped for is not there — this is indifference, not a hidden fire.",
     "ความอบอุ่นที่หวังไว้ไม่มี นี่คือความเฉย ไม่ใช่ไฟที่ซ่อนอยู่",
     "This card is a clear no on the heart of the matter. There is little or no romantic feeling, or the feeling has already gone out. Do not invent a secret love to soften the blow; believing in a fire that is not there will only keep you waiting.",
     "ไพ่ใบนี้ตอบตรงในเรื่องหัวใจ แทบไม่มีความรัก หรือความรู้สึกนั้นดับไปแล้ว อย่าสร้างเรื่องรักลับ ๆ ขึ้นมาเพื่อให้เจ็บน้อยลง ถ้าเชื่อว่ามีไฟทั้งที่ไม่มี จะยิ่งรอไปโดยไม่มีที่สิ้นสุด",
     -2),
    ("oracle-11", "emotion", "Unfinished", "ยังไม่จบ",
     "Something between you is still open — a loose end, not a clean close.",
     "ยังมีอะไรค้างระหว่างกัน เรื่องยังไม่ได้ปิดให้เรียบร้อย",
     "The story has not actually ended. There is unfinished business, a paused conversation, or a bond that was never given a proper close. Until that is faced, it will keep tugging. This is not a promise of a happy return; it is a call to finish what was left hanging.",
     "เรื่องนี้ยังไม่จบจริง ยังมีค้างคา บทสนทนาที่ชะงัก หรือสายสัมพันธ์ที่ยังไม่ได้ปิดอย่างตั้งใจ ถ้ายังไม่หันไปจัดการ มันจะดึงใจต่อไป นี่ไม่ใช่คำสัญญาว่าจะกลับมาอย่างสวยงาม แต่ชวนให้จบสิ่งที่ค้างไว้",
     0),
    ("oracle-12", "emotion", "Unspoken", "ยังไม่พูด",
     "The important words have not been said — silence is doing the talking.",
     "คำสำคัญยังไม่ได้พูด ความเงียบกำลังบอกเรื่องอยู่",
     "Someone is holding back a truth, a confession, or a need. The quiet is heavy, not empty. Until the words come out, guesses and hints will keep hurting. This card asks for honesty, but it does not guarantee that what is said will be easy to hear.",
     "มีคนเก็บความจริง คำสารภาพ หรือความต้องการไว้ ความเงียบนี้หนัก ไม่ใช่ว่างเปล่า จนกว่าจะพูดออกมา การเดาและการใบ้จะยิ่งทำให้เจ็บ ไพ่ใบนี้ชวนให้พูดตรง ๆ แต่ไม่ได้สัญญาว่าสิ่งที่จะได้ยินจะฟังง่าย",
     0),
    ("oracle-13", "emotion", "Hurt Feelings", "เจ็บใจ",
     "Someone is stung — a slight, a harsh word, or a careless act still smarts.",
     "มีคนเจ็บอยู่ คำพูดแรง การมองข้าม หรือความสะเพร่ายังคมอยู่",
     "There is a bruise here. Pride or tenderness was stepped on, and the sting has not faded. If you ignore it, it will harden into distance. If this is your hurt, name it cleanly. If you caused it, a real apology matters more than a quick excuse.",
     "มีรอยช้ำตรงนี้ ความภูมิใจหรือความอ่อนไหวถูกเหยียบ และความเจ็บยังไม่จาง ถ้าปล่อยไว้ มันจะกลายเป็นระยะห่าง ถ้าคุณเป็นคนที่เจ็บ พูดให้ชัด ถ้าคุณเป็นคนทำให้เจ็บ คำขอโทษจริงสำคัญกว่าข้ออ้างเร็ว ๆ",
     -1),
    ("oracle-14", "emotion", "Heartbroken", "อกหัก",
     "This is a broken heart — grief, not a small disappointment.",
     "นี่คืออกหัก เป็นความเจ็บลึก ไม่ใช่แค่ผิดหวังเล็กน้อย",
     "The pain is real and deep. A bond has cracked or ended, and the heart is still in pieces. Do not rush this person (or yourself) back into hope. Healing needs time, gentleness, and honesty about what was lost. Love may come again later; it is not the work of this moment.",
     "ความเจ็บนี้จริงและลึก ความสัมพันธ์ปริหรือจบแล้ว และหัวใจยังไม่หาย อย่ารีบดึงคนนี้หรือตัวเองกลับไปหวัง การเยียวยาต้องใช้เวลา ความอ่อนโยน และความจริงเรื่องสิ่งที่เสียไป รักใหม่อาจมาในภายหลัง แต่ยังไม่ใช่งานของตอนนี้",
     -2),
    ("oracle-15", "emotion", "Anger", "ความโกรธ",
     "Anger is in the room — heat that needs a clean outlet, not a hide.",
     "มีความโกรธอยู่ในเรื่องนี้ เป็นไฟที่ต้องระบายอย่างตรงไปตรงมา ไม่ใช่เก็บกด",
     "Someone is angry, even if they smile over it. The heat may be fair, or it may be spilling onto the wrong target, but it will not vanish if it is swallowed. Name the cause, set a boundary, and do not let the fire run the whole conversation.",
     "มีคนโกรธ แม้จะยิ้มปิดไว้ ไฟนี้อาจมีเหตุผล หรืออาจเล็ดไปโดนคนผิด แต่จะไม่หายเพราะกลืนลงไป พูดให้รู้ว่าอะไรคือต้นเหตุ วางขอบเขต และอย่าให้ความโกรธเป็นคนคุยแทนทั้งหมด",
     -1),
    ("oracle-16", "emotion", "Silence", "ความเงียบ",
     "A wall of quiet — withdrawal, distance, or a refusal to engage.",
     "เป็นกำแพงความเงียบ การถอยห่าง หรือการไม่ยอมคุย",
     "The conversation has stopped, or was never allowed to start. This silence can be protection, punishment, or simple shutdown. You cannot force it open. You can only decide how long you will wait beside a closed door, and what you will do if it stays shut.",
     "บทสนทนาหยุดแล้ว หรือไม่เคยได้เริ่ม ความเงียบนี้อาจเป็นการป้องกัน การลงโทษ หรือการปิดตัว บังคับให้เปิดไม่ได้ สิ่งที่ทำได้คือตัดสินใจว่าจะรออยู่หน้าประตูที่ปิดนานแค่ไหน และจะทำอย่างไรถ้ามันยังไม่เปิด",
     -1),
    ("oracle-17", "emotion", "Disappointed", "ผิดหวัง",
     "Hope met a duller reality — the letdown is already here.",
     "สิ่งที่หวังไว้ไม่ได้เป็นอย่างนั้น ความผิดหวังมาถึงแล้ว",
     "Something hoped for did not arrive as imagined. The feeling is disappointment, which is quieter than heartbreak but just as real. Adjust the picture, say what fell short, and do not keep promising yourself a version of events that already failed.",
     "สิ่งที่หวังไว้ไม่ได้มาอย่างที่คิด ความผิดหวังนี้ไม่แรงเท่าอกหัก แต่ก็จริงไม่แพ้กัน ปรับภาพในใจ พูดให้รู้ว่าอะไรไม่เป็นไปตามที่คิด และอย่าสัญญาอะไรกับตัวเองซ้ำในแบบที่ล้มเหลวแล้ว",
     -1),
    ("oracle-18", "emotion", "Hopeless", "สิ้นหวัง",
     "The heart has run out of hope — this is exhaustion, not a hidden chance.",
     "ใจหมดหวังแล้ว นี่คือความเหนื่อย ไม่ใช่โอกาสที่ซ่อนอยู่",
     "Energy and faith are spent. From this place, pushing harder usually deepens the pit. The honest work is to stop feeding a dead hope, rest, and look for a smaller, truer next step. Hope can return later; it will not be argued back into being today.",
     "แรงและกำลังใจหมดแล้ว ถ้าฝืนผลักจากจุดนี้มักจะยิ่งจม งานตอนนี้คือเลิกยึดความหวังที่หมดแล้ว พัก แล้วค่อยก้าวเล็ก ๆ ที่ทำได้จริง ความหวังอาจกลับมาในภายหลัง แต่วันนี้บังคับให้มันกลับมายังไม่ได้",
     -2),
    ("oracle-19", "emotion", "Acceptance", "ยอมรับ",
     "A calm yes to what is — peace after the fight, not giving up in despair.",
     "ยอมรับสิ่งที่เป็นอยู่ด้วยใจสงบ หลังจากสู้มาแล้ว ไม่ใช่ยอมแพ้เพราะหมดแรง",
     "The struggle to make reality otherwise is easing. This is the quiet strength of accepting what is, so you can live with it or build from it. It is not bitterness and it is not a plea to stay in a bad place; it is a clear-eyed truce with the truth.",
     "การดิ้นรนให้ความจริงเป็นอย่างอื่นเริ่มเบาลง นี่คือการยอมรับสิ่งที่เป็นอย่างสงบ เพื่ออยู่กับมันหรือเริ่มใหม่จากจุดนี้ ไม่ใช่ความขมขื่น และไม่ใช่การขอให้ทนอยู่ในที่แย่ แต่เป็นการมองความจริงตามที่เป็น",
     1),
    ("oracle-20", "emotion", "Love to Give", "รักที่พร้อมให้",
     "There is love ready to be given — warmth, care, and an open hand.",
     "มีความรักที่พร้อมจะให้ ทั้งความอบอุ่น ความห่วงใย และความปรารถนาดี",
     "The heart is generous here. Someone wants to offer care, time, or affection, and the well is not dry. Receive it if it is meant for you, or notice if you are the one overflowing. This is a kind card; just be sure the love is given freely, not used to buy a yes.",
     "หัวใจตรงนี้ใจกว้าง มีคนอยากให้เวลา ความดูแล หรือความเอ็นดู และยังไม่สาย รับไว้ถ้าเป็นของคุณ หรือสังเกตถ้าคุณคือคนที่กำลังให้อยู่ ไพ่ใบนี้ใจดี เพียงให้แน่ใจว่ารักนี้ให้ด้วยความเต็มใจ ไม่ได้ใช้แลกคำตอบว่าใช่",
     2),
    ("oracle-21", "emotion", "Jealous", "หึงหวง",
     "Jealousy is coloring the picture — comparison, fear of loss, or possessiveness.",
     "ความหึงกำลังเข้ามาในเรื่องนี้ ทั้งการเปรียบ ความกลัวจะเสีย หรือความรู้สึกเป็นเจ้าของ",
     "Someone is comparing, watching, or holding too tight. The root is usually fear, not proof. If this is you, tell the truth about the fear before it turns into control. If this is them, take the feeling seriously, but do not accept being owned.",
     "มีคนกำลังเปรียบ เฝ้าดู หรือกำไว้แน่นเกินไป ต้นเหตุมักเป็นความกลัว ไม่ใช่หลักฐาน ถ้าเป็นคุณ พูดความจริงเรื่องความกลัวก่อนที่มันจะกลายเป็นการควบคุม ถ้าเป็นเขา จริงจังกับความรู้สึกนั้นได้ แต่ไม่ต้องยอมให้ใครเป็นเจ้าของ",
     -1),
    ("oracle-22", "emotion", "Worried", "กังวล",
     "Worry is running ahead of the facts — a restless, looping mind.",
     "ความกังวลวิ่งนำหน้าความจริง ใจไม่นิ่งและคิดวน",
     "The mind is rehearsing trouble. Some of the concern may be fair, but much of the weight is imagined futures. Slow down, name the actual problem, and take one practical step. Anxiety is not a prophecy, and sitting in it will not protect you.",
     "ใจกำลังคิดวนเรื่องร้าย บางส่วนอาจมีเหตุ แต่ส่วนที่หนักมักเป็นอนาคตที่คิดเอง ชะลอลง ระบุปัญหาที่มีจริง แล้วเดินหนึ่งก้าวที่ทำได้ ความกังวลไม่ใช่คำทำนาย และการนั่งจมอยู่กับมันจะไม่ได้ช่วยป้องกันอะไร",
     -1),
    ("oracle-23", "emotion", "Sinking Heart", "ใจตก",
     "The heart is dropping — a heavy, sinking feeling that something is off.",
     "ใจกำลังตก รู้สึกหนัก ราวกับมีอะไรไม่ชอบมาพากล",
     "This is the moment the chest tightens and hope dips. You already sense that the news, the silence, or the change is not good. Do not talk yourself out of that signal. Sit with it, check the facts, and then decide — the sinking itself is information.",
     "นี่คือช่วงที่อกแน่นและความหวังลด คุณสัมผัสได้แล้วว่าข่าว ความเงียบ หรือการเปลี่ยนแปลงนี้ไม่ดี อย่าคุยจนตัวเองไม่เชื่อสัญญาณนั้น นั่งกับมัน ตรวจข้อเท็จจริง แล้วค่อยตัดสินใจ ความรู้สึกนี้กำลังบอกอะไรบางอย่าง",
     -1),
    ("oracle-24", "emotion", "Suffering", "ความทุกข์",
     "There is real suffering here — a heavier pain that needs care, not a pep talk.",
     "มีความทุกข์จริงตรงนี้ เจ็บเกินกว่าจะปลอบด้วยคำสวย ๆ และต้องการการดูแล",
     "Someone is carrying more than a passing sadness. The pain may be grief, loneliness, or a wound that has lasted. Meet it with care and, if needed, real help. This card does not ask you to stay in the hurt forever; it asks you not to pretend it is small.",
     "มีคนแบกอะไรที่หนักกว่าความเศร้าธรรมดา อาจเป็นความสูญเสีย ความเหงา หรือแผลที่อยู่นาน ตอบด้วยความดูแล และขอความช่วยเหลือจริงถ้าจำเป็น ไพ่ใบนี้ไม่ได้ให้คุณจมอยู่กับความเจ็บตลอดไป แต่ขออย่าทำเป็นว่ามันเล็ก",
     -2),
    ("oracle-25", "emotion", "Missing You", "คิดถึง",
     "Someone is missing the other — a genuine ache of absence and memory.",
     "มีคนคิดถึงอีกฝ่าย เป็นความรู้สึกขาดที่จริงใจ",
     "Distance, a breakup, or even a busy stretch has left a hole. The missing is real. It can be love, habit, or both. Let the feeling be named, but do not assume that missing someone is the same as being able to return to how it was.",
     "ระยะทาง การจากกัน หรือแม้แค่ช่วงที่ยุ่ง ได้ทิ้งช่องว่างไว้ ความคิดถึงนี้จริง อาจเป็นรัก อาจเป็นความคุ้นชิน หรือทั้งสองอย่าง พูดความรู้สึกนี้ได้อยู่ แต่การคิดถึงไม่เท่ากับการกลับไปเหมือนเดิม",
     1),
    ("oracle-26", "emotion", "Happiness", "ความสุข",
     "Joy is present — a light, genuine happiness the cards want you to trust.",
     "มีความสุขอยู่ตรงนี้ เป็นความเบิกบานจริง ไพ่ชวนให้เชื่อ",
     "This is a bright card. There is real gladness, ease, or a simple good moment that does not need to be argued with. Let yourself (or them) feel it. Happiness here is not a trick; just do not crush it by immediately looking for the catch.",
     "ไพ่ใบนี้สว่าง มีความยินดี ความสบาย หรือช่วงดี ๆ ที่ไม่ต้องเถียงกับมัน ปล่อยให้ตัวเองหรืออีกฝ่ายได้รู้สึก ความสุขตรงนี้ไม่ใช่กลอุบาย เพียงอย่าเพิ่งรีบหาจุดผิดทันที",
     2),
    ("oracle-27", "emotion", "New Beginning", "เริ่มต้นใหม่",
     "A fresh start is opening — a new chapter, not a rerun of the old one.",
     "การเริ่มต้นใหม่กำลังเปิด เป็นบทใหม่ ไม่ใช่การเล่นซ้ำเรื่องเดิม",
     "Something can start again, but it will not be a perfect copy of the past. A door is opening: a new bond, a new way of being, or a clean page after a close. Step through with clear eyes. The gift is the beginning itself, not a guarantee that the old story will be restored.",
     "มีสิ่งที่เริ่มใหม่ได้ แต่จะไม่ใช่สำเนาของอดีต ประตูกำลังเปิด อาจเป็นสายสัมพันธ์ใหม่ วิธีใหม่ในการใช้ชีวิต หรือหน้าใหม่หลังปิดเรื่องเก่า เดินเข้าไปด้วยตาที่ชัด ของขวัญคือจุดเริ่มต้น ไม่ใช่คำสัญญาว่าเรื่องเดิมจะกลับมา",
     2),
    ("oracle-28", "words", "Face the Truth", "เผชิญความจริง",
     "Look straight at what is true — even if it is uncomfortable.",
     "หันไปมองความจริงตรง ๆ แม้จะอึดอัด",
     "Stop circling the story you prefer. The counsel is to face the fact that is already in front of you — a feeling, a pattern, or an outcome you have been softening. Honesty will sting and then clear the air. Delay will only thicken the fog.",
     "เลิกวนอยู่ในเรื่องที่อยากได้ยิน ไพ่ใบนี้ชวนให้เผชิญความจริงที่อยู่ตรงหน้าแล้ว ไม่ว่าจะเป็นความรู้สึก รูปแบบ หรือผลที่คุณพยายามทำให้เบาลง ความจริงอาจเจ็บ แต่แล้วจะโล่งขึ้น การเลื่อนออกไปจะยิ่งทำให้เรื่องพร่ามัว",
     0),
    ("oracle-29", "words", "You Already Know", "รู้ดีอยู่แล้ว",
     "You already know the answer — trust the knowing you have been talking over.",
     "คุณรู้คำตอบอยู่แล้ว เชื่อสิ่งที่ตัวเองรู้อยู่แล้วตั้งแต่ต้น",
     "The reading will not surprise you if you are honest. You have already felt the yes, the no, or the need to leave. This card asks you to stop shopping for a softer opinion and to act on what you know. The work is courage, not more information.",
     "ถ้าซื่อสัตย์กับตัวเอง คำทำนายจะไม่ทำให้แปลกใจ คุณรู้แล้วว่าใช่ ไม่ใช่ หรือว่าต้องไป ไพ่ใบนี้ชวนให้เลิกหาความเห็นที่ฟังสบายกว่า และลงมือตามที่รู้แล้ว งานตรงนี้คือความกล้า ไม่ใช่การหาข้อมูลเพิ่ม",
     0),
    ("oracle-30", "words", "Keep Dreaming, Take Action", "ฝันแล้วลงมือทำ",
     "Keep the dream, and put your feet under it — hope without a step stays a wish.",
     "เก็บความฝันไว้ แต่ต้องลงมือด้วย ความหวังที่ไม่มีก้าวจะเป็นแค่คำอธิษฐาน",
     "The desire is worth keeping, but it will not arrive on longing alone. Take a concrete step: a conversation, a plan, a practice, an application. Dream and movement belong together here. Waiting for a perfect moment is how the dream goes stale.",
     "ความอยากนั้นคุ้มที่จะเก็บ แต่จะไม่สำเร็จแค่เพราะคิดถึง ลงมือให้เป็นชิ้นเป็นอัน ไม่ว่าจะเป็นการคุย วางแผน ฝึกฝน หรือสมัคร ฝันกับการลงมือต้องไปด้วยกัน การรอจังหวะเพอร์เฟกต์คือทางที่ความฝันจะค้างอยู่แค่ฝัน",
     1),
    ("oracle-31", "words", "Love Yourself", "รักตัวเอง",
     "Turn the care inward — your own heart is the one that needs tending now.",
     "หันมาดูแลตัวเอง หัวใจของตัวเองคือสิ่งที่ต้องการการดูแลตอนนี้",
     "The counsel is not to abandon others, but to stop abandoning yourself. Rest, dignity, and kind limits belong to you first. If you keep pouring out from an empty cup, both the relationship and your health will pay. Choose the action that respects you.",
     "ไพ่ใบนี้ไม่ได้ให้ทิ้งคนอื่น แต่ให้เลิกทิ้งตัวเอง พักผ่อน ศักดิ์ศรี และขอบเขตที่เหมาะสมเป็นของคุณก่อน ถ้าให้จากถ้วยที่ยังว่าง ทั้งความสัมพันธ์และสุขภาพจะตามไปด้วย เลือกสิ่งที่ให้เกียรติตัวเอง",
     1),
    ("oracle-32", "words", "Time Will Tell", "เวลาจะบอกเอง",
     "Some of this can only be proven in time — watch what happens, not just what is promised.",
     "บางอย่างพิสูจน์ได้ด้วยเวลาเท่านั้น ดูสิ่งที่เกิดขึ้นจริง ไม่ใช่แค่ที่ถูกสัญญา",
     "You cannot force a final answer today. Let events show you the truth: consistency, follow-through, and how someone behaves when it counts. This is not an excuse to do nothing forever. Set a fair window, live your life, and let time be the test.",
     "วันนี้ยังบังคับคำตอบสุดท้ายไม่ได้ ให้เหตุการณ์เป็นคนพิสูจน์ ดูความสม่ำเสมอ การทำตามคำพูด และพฤติกรรมตอนที่สำคัญ นี่ไม่ใช่ข้ออ้างให้ไม่ทำอะไรเลย กำหนดช่วงเวลาที่พอดี ใช้ชีวิตต่อไป และให้เวลาเป็นบททดสอบ",
     0),
    ("oracle-33", "words", "Rest, Don't Overdo It", "พักก่อน อย่าหักโหม",
     "Stop pushing so hard — rest is the useful move, not another late night of effort.",
     "หยุดฝืนขนาดนี้ การพักต่างหากที่เป็นทางที่ดี ไม่ใช่การตรากตรำอีกคืน",
     "You (or they) are running past the point of wisdom. More messages, more work, more proving will thin you out. Step back, sleep, eat, and let the nervous system settle. The situation will be clearer after rest than after one more forced push.",
     "คุณหรืออีกฝ่ายฝืนมาเกินพอแล้ว การส่งข้อความเพิ่ม ทำงานเพิ่ม หรือพิสูจน์ตัวเพิ่มจะยิ่งทำให้หมดแรง ถอย พัก นอน กิน ให้ร่างกายและใจได้สงบ เรื่องจะชัดหลังได้พัก มากกว่าหลังฝืนอีกครั้ง",
     0),
    ("oracle-34", "words", "Make a Choice", "ต้องเลือก",
     "The fork is here — standing still is also a choice, and it is costing you.",
     "ทางแยกมาถึงแล้ว การยืนนิ่งก็เป็นการเลือก และกำลังมีราคา",
     "Two (or more) paths are open, and the cards will not walk them for you. Pick, even if the pick is imperfect. Delayed choosing is leaking time, energy, and other people's trust. Name the options, choose one, and stand by it long enough to see it through.",
     "มีสองทางหรือมากกว่าเปิดอยู่ และไพ่จะไม่เดินแทนคุณ ต้องเลือก แม้การเลือกนั้นจะไม่สมบูรณ์แบบ การเลื่อนเลือกคือการเสียเวลา แรง และความไว้ใจของคนอื่น ดูทางที่มี เลือกหนึ่งทาง แล้วเดินตามทางนั้นนานพอให้ได้เห็นผล",
     0),
    ("oracle-35", "words", "Care for Your Body", "ดูแลร่างกาย",
     "Your body needs attention now — sleep, food, rest, or a real check-in.",
     "ร่างกายต้องการความใส่ใจตอนนี้ ทั้งการนอน อาหาร การพัก หรือการตรวจที่จริงจัง",
     "The counsel is physical, not only emotional. Exhaustion, skipped meals, or ignored symptoms are part of this story. Soften the pace and take care of the body that has to live the answer. A clear mind is hard to find in a depleted body.",
     "ไพ่ใบนี้พูดเรื่องร่างกาย ไม่ใช่แค่ใจ ความเหนื่อย การอดข้าว หรืออาการที่ถูกละเลยเป็นส่วนของเรื่องนี้ ชะลอลงและดูแลร่างที่ต้องไปใช้ชีวิตกับคำตอบนั้น ใจที่ชัดหาได้ยากเมื่อร่างหมดแรง",
     0),
    ("oracle-36", "words", "Guard Your Heart", "ระวังหัวใจ",
     "Protect your heart — be kind, but do not hand it over unguarded.",
     "ระวังหัวใจ ใจดีได้ แต่ยังไม่ต้องมอบให้อย่างไม่มีข้อแม้",
     "Warmth is fine; being unguarded is not wise right now. Watch for mixed signals, old patterns, or a charm that moves faster than trust. You can stay open-eyed and still be warm. Boundaries here are care, not coldness.",
     "อบอุ่นได้ แต่การเปิดใจโดยไม่มีขอบเขตตอนนี้ยังไม่ฉลาด สังเกตสัญญาณที่ไปคนละทาง รูปแบบเก่า หรือเสน่ห์ที่มาเร็วกว่าความไว้ใจ ลืมตาไว้และยังใจดีได้ เส้นแบ่งตรงนี้คือการดูแลตัวเอง ไม่ใช่ความเย็นชา",
     0),
    ("oracle-37", "words", "Stay Mindful", "มีสติ",
     "Stay present and awake — do not sleepwalk through this.",
     "อยู่กับปัจจุบันและรู้ตัว อย่าปล่อยให้เรื่องนี้ผ่านไปโดยไม่ทันคิด",
     "The counsel is to keep your wits about you. Notice what you feel, what you agree to, and what you are about to say. Mindfulness here is practical: fewer impulsive messages, fewer borrowed stories, more attention to the moment you are actually in.",
     "ไพ่ใบนี้ชวนให้รู้ตัว สังเกตว่าตัวเองรู้สึกอะไร กำลังยอมรับอะไร และกำลังจะพูดอะไร สติตรงนี้ใช้ได้จริง ส่งข้อความด้วยอารมณ์ให้น้อยลง อย่าไปยึดเรื่องของคนอื่นมาเป็นของตัวเอง และใส่ใจกับขณะที่กำลังอยู่ให้มากขึ้น",
     1),
]


_RNG = secrets.SystemRandom()


def _build() -> list[dict[str, Any]]:
    out = []
    for cid, cat, en, th, short_en, short_th, long_en, long_th, score in _CARDS:
        out.append({
            "id": cid,
            "category": cat,
            "nameEn": en,
            "nameTh": th,
            "meaningEn": short_en,
            "meaningTh": short_th,
            "textEn": long_en,
            "textTh": long_th,
            "score": score,
            "number": int(cid.split("-")[1]),
        })
    return out


DECK: list[dict[str, Any]] = _build()
BY_ID = {c["id"]: c for c in DECK}
BY_CATEGORY: dict[str, list[dict[str, Any]]] = {
    cat: [c for c in DECK if c["category"] == cat] for cat in CATEGORIES
}


def image_path(card_id: str) -> str:
    return f"/oracle/{card_id}.webp?v={IMAGE_VERSION}"


def thumb_path(card_id: str) -> str:
    return f"/oracle/{card_id}-thumb.webp?v={THUMB_VERSION}"


def back_path() -> str:
    return f"/oracle/card-back.webp?v={BACK_VERSION}"


def back_thumb_path() -> str:
    return f"/oracle/card-back-thumb.webp?v={BACK_VERSION}"


def public_card(card: dict[str, Any], *, thumb: bool = False) -> dict[str, Any]:
    """Shape used in a reading or on the public list (no internal score)."""
    return {
        "id": card["id"],
        "nameEn": card["nameEn"],
        "nameTh": card["nameTh"],
        "category": card["category"],
        "categoryEn": CATEGORIES[card["category"]]["en"],
        "categoryTh": CATEGORIES[card["category"]]["th"],
        "meaningEn": card["meaningEn"],
        "meaningTh": card["meaningTh"],
        "image": thumb_path(card["id"]) if thumb else image_path(card["id"]),
        "reversed": False,
    }


def _drawn(card: dict[str, Any], position: dict[str, str]) -> dict[str, Any]:
    out = public_card(card, thumb=False)
    out["position"] = position["id"]
    out["positionEn"] = position["nameEn"]
    out["positionTh"] = position["nameTh"]
    return out


def draw() -> list[dict[str, Any]]:
    """One random card from each category, in Timing / Feeling / Counsel order.

    OS randomness; no reversals; the client cannot choose identities.
    """
    out = []
    for pos in POSITIONS:
        card = _RNG.choice(BY_CATEGORY[pos["id"]])
        out.append(_drawn(card, pos))
    return out


def catalog() -> list[dict[str, Any]]:
    """Public list for the meanings page and any client catalog (thumbs + long text)."""
    out = []
    for card in DECK:
        item = public_card(card, thumb=True)
        item["textEn"] = card["textEn"]
        item["textTh"] = card["textTh"]
        item["number"] = card["number"]
        out.append(item)
    return out


def prompt_lines(cards: list[dict[str, Any]]) -> str:
    lines = []
    for c in cards:
        pos = f"{c.get('positionEn', '')} / {c.get('positionTh', '')}".strip(" /")
        cat = f"{c.get('categoryEn', '')} / {c.get('categoryTh', '')}".strip(" /")
        prefix = f"{pos} ({cat}): " if pos else ""
        lines.append(
            f"- {prefix}{c['nameEn']} — {c['nameTh']}. "
            f"Meaning: {c['meaningEn']} / {c['meaningTh']}"
        )
    return "\n".join(lines)


def card_score(card: dict[str, Any]) -> float:
    raw = BY_ID.get(card["id"], {})
    return float(raw.get("score", 0))


# Same bands as the tarot verdict, so yes/likely/not_yet/unlikely/no stay familiar.
YES_AT = 2.4
LIKELY_AT = 1.0


def verdict(cards: list[dict[str, Any]]) -> str:
    score = sum(card_score(c) for c in cards)
    # "Not Yet Time" in the timing seat should not be talked past as a clear yes.
    if any(c["id"] == "oracle-08" for c in cards) and score >= LIKELY_AT:
        return "not_yet"
    if score >= YES_AT:
        return "yes"
    if score >= LIKELY_AT:
        return "likely"
    if score > -LIKELY_AT:
        return "not_yet"
    if score > -YES_AT:
        return "unlikely"
    return "no"


ANSWER_TH = {
    "yes": "คำตอบคือ ใช่ค่ะ ไพ่ออราเคิลไปในทางบวกชัดเจน",
    "likely": "คำตอบคือ มีแนวโน้มสูงว่าใช่ค่ะ แต่ยังมีเงื่อนไขที่ต้องทำ ไม่ใช่รอเฉย ๆ",
    "not_yet": "คำตอบคือ ยังไม่ใช่ตอนนี้ค่ะ จังหวะยังไม่สุก หรือเรื่องยังต้องเปลี่ยนก่อน",
    "unlikely": "คำตอบคือ มีแนวโน้มว่าไม่ค่ะ ไพ่ส่วนใหญ่ยังไม่เป็นใจกับเรื่องนี้",
    "no": "คำตอบตรง ๆ คือ ไม่ค่ะ ไพ่ชี้ชัดว่าเรื่องนี้ไม่เป็นไปตามที่หวัง",
}
ANSWER_EN = {
    "yes": "The answer is yes — the oracle cards lean clearly in favour.",
    "likely": "The answer is likely yes, but there is a condition you must act on; do not just wait.",
    "not_yet": "The answer is not yet — the timing is not ripe, or something still has to change.",
    "unlikely": "The answer is likely no — most of these cards are not on the side of this hope.",
    "no": "The direct answer is no — the cards are clear that this is not going as hoped.",
}


def fallback_reading(name: str, question: str, topic_th: str, topic_en: str,
                     cards: list[dict[str, Any]], lang: str) -> str:
    """A direct three-paragraph reading when the AI is unavailable."""
    lean = verdict(cards)
    th = lang == "th"
    by_pos = {c.get("position"): c for c in cards}
    time_c, feel_c, word_c = by_pos.get("time") or cards[0], by_pos.get("emotion") or cards[1], by_pos.get("words") or cards[2]
    q = (question or "").strip()
    if th:
        lead = ANSWER_TH[lean]
        if q:
            p1 = f"{name}ค่ะ {lead} สำหรับคำถามที่ว่า «{q}»"
        else:
            p1 = f"{name}ค่ะ {lead} ในเรื่อง{topic_th}"
        p2 = (
            f"เวลาคือ «{time_c['nameTh']}»: {time_c['meaningTh']} "
            f"อารมณ์ที่ไพ่ชี้คือ «{feel_c['nameTh']}»: {feel_c['meaningTh']} "
            f"คำพูดจากไพ่คือ «{word_c['nameTh']}»: {word_c['meaningTh']}"
        )
        p3 = (
            f"คำแนะนำที่ใช้ได้เลย: รับความหมายของไพ่ «{word_c['nameTh']}» ไปลงมือ "
            f"และให้จังหวะ «{time_c['nameTh']}» เป็นกรอบ อย่าฝืนเรื่องที่ยังไม่สุก และอย่าทิ้งสิ่งที่ไพ่ชี้ชัดแล้ว"
        )
        return "\n\n".join([p1, p2, p3])
    lead = ANSWER_EN[lean]
    if q:
        p1 = f"{name}, {lead} To the question “{q}”"
        if not p1.endswith("."):
            p1 += "."
    else:
        p1 = f"{name}, {lead} About your {topic_en}."
    p2 = (
        f"The timing is “{time_c['nameEn']}”: {time_c['meaningEn']} "
        f"The feeling the cards show is “{feel_c['nameEn']}”: {feel_c['meaningEn']} "
        f"The counsel is “{word_c['nameEn']}”: {word_c['meaningEn']}"
    )
    p3 = (
        f"Advice you can use now: act on “{word_c['nameEn']}”, "
        f"and let “{time_c['nameEn']}” be the timeframe. Do not force what is not ripe, "
        f"and do not ignore what the cards have already made clear."
    )
    return "\n\n".join([p1, p2, p3])


def premium_from_cards(cards: list[dict[str, Any]], lang: str) -> dict[str, Any]:
    """Paid deep section built only from the three oracle cards (no invented lucky numbers)."""
    th = lang == "th"
    by_pos = {c.get("position"): c for c in cards}
    time_c = by_pos.get("time") or cards[0]
    feel_c = by_pos.get("emotion") or cards[1]
    word_c = by_pos.get("words") or cards[2]
    scored = sorted(cards, key=lambda c: card_score(c))
    low, high = scored[0], scored[-1]
    colors = [
        {"en": "Midnight blue", "th": "น้ำเงินกรมท่า", "hex": "#14244a", "cat": "time"},
        {"en": "Warm brown", "th": "น้ำตาลอุ่น", "hex": "#6b3f24", "cat": "emotion"},
        {"en": "Deep green", "th": "เขียวเข้ม", "hex": "#174a32", "cat": "words"},
    ]
    present = {c["category"] for c in cards}
    return {
        "forecast": (f"{time_c['nameTh']} — {time_c['meaningTh']}" if th
                     else f"{time_c['nameEn']} — {time_c['meaningEn']}"),
        "gift": (f"{high['nameTh']} — {high['meaningTh']}" if th
                 else f"{high['nameEn']} — {high['meaningEn']}"),
        "shadow": (f"{low['nameTh']} — {low['meaningTh']}" if th
                   else f"{low['nameEn']} — {low['meaningEn']}"),
        "compatibility": (f"{word_c['nameTh']} — {word_c['meaningTh']}" if th
                          else f"{word_c['nameEn']} — {word_c['meaningEn']}"),
        "numbers": [],
        "colors": [c for c in colors if c["cat"] in present],
        "day": "",
        "kind": "oracle",
    }
