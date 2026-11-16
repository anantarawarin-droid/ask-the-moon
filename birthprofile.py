"""Birth profile panel: Western zodiac, Chinese zodiac (ปีนักษัตร), and the
birth-date (life path) number, each with a short meaning.

Shown beside the tarot answer only. Nothing here is ever sent to the AI:
the tarot answer stays based on the three cards alone.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

CNY: dict[int, tuple[int, int]] = {
    1900: (1, 31), 1901: (2, 19), 1902: (2, 8), 1903: (1, 29), 1904: (2, 16),
    1905: (2, 4), 1906: (1, 25), 1907: (2, 13), 1908: (2, 2), 1909: (1, 22),
    1910: (2, 10), 1911: (1, 30), 1912: (2, 18), 1913: (2, 6), 1914: (1, 26),
    1915: (2, 14), 1916: (2, 3), 1917: (1, 23), 1918: (2, 11), 1919: (2, 1),
    1920: (2, 20), 1921: (2, 8), 1922: (1, 28), 1923: (2, 16), 1924: (2, 5),
    1925: (1, 24), 1926: (2, 13), 1927: (2, 2), 1928: (1, 23), 1929: (2, 10),
    1930: (1, 30), 1931: (2, 17), 1932: (2, 6), 1933: (1, 26), 1934: (2, 14),
    1935: (2, 4), 1936: (1, 24), 1937: (2, 11), 1938: (1, 31), 1939: (2, 19),
    1940: (2, 8), 1941: (1, 27), 1942: (2, 15), 1943: (2, 5), 1944: (1, 25),
    1945: (2, 13), 1946: (2, 2), 1947: (1, 22), 1948: (2, 10), 1949: (1, 29),
    1950: (2, 17), 1951: (2, 6), 1952: (1, 27), 1953: (2, 14), 1954: (2, 3),
    1955: (1, 24), 1956: (2, 12), 1957: (1, 31), 1958: (2, 18), 1959: (2, 8),
    1960: (1, 28), 1961: (2, 15), 1962: (2, 5), 1963: (1, 25), 1964: (2, 13),
    1965: (2, 2), 1966: (1, 21), 1967: (2, 9), 1968: (1, 30), 1969: (2, 17),
    1970: (2, 6), 1971: (1, 27), 1972: (2, 15), 1973: (2, 3), 1974: (1, 23),
    1975: (2, 11), 1976: (1, 31), 1977: (2, 18), 1978: (2, 7), 1979: (1, 28),
    1980: (2, 16), 1981: (2, 5), 1982: (1, 25), 1983: (2, 13), 1984: (2, 2),
    1985: (2, 20), 1986: (2, 9), 1987: (1, 29), 1988: (2, 17), 1989: (2, 6),
    1990: (1, 27), 1991: (2, 15), 1992: (2, 4), 1993: (1, 23), 1994: (2, 10),
    1995: (1, 31), 1996: (2, 19), 1997: (2, 7), 1998: (1, 28), 1999: (2, 16),
    2000: (2, 5), 2001: (1, 24), 2002: (2, 12), 2003: (2, 1), 2004: (1, 22),
    2005: (2, 9), 2006: (1, 29), 2007: (2, 18), 2008: (2, 7), 2009: (1, 26),
    2010: (2, 14), 2011: (2, 3), 2012: (1, 23), 2013: (2, 10), 2014: (1, 31),
    2015: (2, 19), 2016: (2, 8), 2017: (1, 28), 2018: (2, 16), 2019: (2, 5),
    2020: (1, 25), 2021: (2, 12), 2022: (2, 1), 2023: (1, 22), 2024: (2, 10),
    2025: (1, 29), 2026: (2, 17), 2027: (2, 6), 2028: (1, 26), 2029: (2, 13),
    2030: (2, 3), 2031: (1, 23), 2032: (2, 11), 2033: (1, 31), 2034: (2, 19),
    2035: (2, 8), 2036: (1, 28), 2037: (2, 15), 2038: (2, 4), 2039: (1, 24),
    2040: (2, 12),
}

# 1924 is Jia-Zi (Yang Wood Rat), the start of a 60-year cycle.
ANIMALS = [
    ("rat", "Rat", "ชวด (หนู)"),
    ("ox", "Ox", "ฉลู (วัว)"),
    ("tiger", "Tiger", "ขาล (เสือ)"),
    ("rabbit", "Rabbit", "เถาะ (กระต่าย)"),
    ("dragon", "Dragon", "มะโรง (มังกร)"),
    ("snake", "Snake", "มะเส็ง (งู)"),
    ("horse", "Horse", "มะเมีย (ม้า)"),
    ("goat", "Goat", "มะแม (แพะ)"),
    ("monkey", "Monkey", "วอก (ลิง)"),
    ("rooster", "Rooster", "ระกา (ไก่)"),
    ("dog", "Dog", "จอ (สุนัข)"),
    ("pig", "Pig", "กุน (สุกร)"),
]

STEMS = [
    ("wood", "yang", "Wood", "ไม้", "Yang", "หยาง"),
    ("wood", "yin", "Wood", "ไม้", "Yin", "หยิน"),
    ("fire", "yang", "Fire", "ไฟ", "Yang", "หยาง"),
    ("fire", "yin", "Fire", "ไฟ", "Yin", "หยิน"),
    ("earth", "yang", "Earth", "ดิน", "Yang", "หยาง"),
    ("earth", "yin", "Earth", "ดิน", "Yin", "หยิน"),
    ("metal", "yang", "Metal", "ทอง", "Yang", "หยาง"),
    ("metal", "yin", "Metal", "ทอง", "Yin", "หยิน"),
    ("water", "yang", "Water", "น้ำ", "Yang", "หยาง"),
    ("water", "yin", "Water", "น้ำ", "Yin", "หยิน"),
]

ZODIAC: dict[str, dict[str, str]] = {
    "aries": {
        "en": "Aries", "th": "เมษ", "glyph": "♈",
        "element_en": "Fire", "element_th": "ไฟ",
        "modality_en": "Cardinal", "modality_th": "นำ",
        "ruler_en": "Mars", "ruler_th": "อังคาร",
        "dates_en": "Mar 21 – Apr 19", "dates_th": "21 มี.ค. – 19 เม.ย.",
        "trait_en": "bold, pioneering, and quick to begin",
        "trait_th": "กล้าหาญ เป็นผู้บุกเบิก และพร้อมเริ่มต้นเสมอ",
    },
    "taurus": {
        "en": "Taurus", "th": "พฤษภ", "glyph": "♉",
        "element_en": "Earth", "element_th": "ดิน",
        "modality_en": "Fixed", "modality_th": "มั่น",
        "ruler_en": "Venus", "ruler_th": "ศุกร์",
        "dates_en": "Apr 20 – May 20", "dates_th": "20 เม.ย. – 20 พ.ค.",
        "trait_en": "steady, sensual, and loyal to what you love",
        "trait_th": "มั่นคง ละเอียดอ่อนต่อความงาม และซื่อสัตย์ต่อสิ่งที่รัก",
    },
    "gemini": {
        "en": "Gemini", "th": "เมถุน", "glyph": "♊",
        "element_en": "Air", "element_th": "ลม",
        "modality_en": "Mutable", "modality_th": "ปรับ",
        "ruler_en": "Mercury", "ruler_th": "พุธ",
        "dates_en": "May 21 – Jun 20", "dates_th": "21 พ.ค. – 20 มิ.ย.",
        "trait_en": "curious, quick-witted, and born to connect",
        "trait_th": "อยากรู้อยากเห็น ไหวพริบดี และเกิดมาเพื่อเชื่อมโยงผู้คน",
    },
    "cancer": {
        "en": "Cancer", "th": "กรกฎ", "glyph": "♋",
        "element_en": "Water", "element_th": "น้ำ",
        "modality_en": "Cardinal", "modality_th": "นำ",
        "ruler_en": "Moon", "ruler_th": "พระจันทร์",
        "dates_en": "Jun 21 – Jul 22", "dates_th": "21 มิ.ย. – 22 ก.ค.",
        "trait_en": "intuitive, protective, and deeply feeling",
        "trait_th": "มีสัญชาตญาณแรง ปกป้องคนรัก และรู้สึกอย่างลึกซึ้ง",
    },
    "leo": {
        "en": "Leo", "th": "สิงห์", "glyph": "♌",
        "element_en": "Fire", "element_th": "ไฟ",
        "modality_en": "Fixed", "modality_th": "มั่น",
        "ruler_en": "Sun", "ruler_th": "พระอาทิตย์",
        "dates_en": "Jul 23 – Aug 22", "dates_th": "23 ก.ค. – 22 ส.ค.",
        "trait_en": "warm-hearted, creative, and made to shine",
        "trait_th": "ใจอบอุ่น สร้างสรรค์ และเกิดมาเพื่อเปล่งประกาย",
    },
    "virgo": {
        "en": "Virgo", "th": "กันย์", "glyph": "♍",
        "element_en": "Earth", "element_th": "ดิน",
        "modality_en": "Mutable", "modality_th": "ปรับ",
        "ruler_en": "Mercury", "ruler_th": "พุธ",
        "dates_en": "Aug 23 – Sep 22", "dates_th": "23 ส.ค. – 22 ก.ย.",
        "trait_en": "precise, devoted, and gifted at making things better",
        "trait_th": "ละเอียด อุทิศตน และมีพรสวรรค์ในการทำให้สิ่งต่าง ๆ ดีขึ้น",
    },
    "libra": {
        "en": "Libra", "th": "ตุลย์", "glyph": "♎",
        "element_en": "Air", "element_th": "ลม",
        "modality_en": "Cardinal", "modality_th": "นำ",
        "ruler_en": "Venus", "ruler_th": "ศุกร์",
        "dates_en": "Sep 23 – Oct 22", "dates_th": "23 ก.ย. – 22 ต.ค.",
        "trait_en": "graceful, fair-minded, and drawn to harmony",
        "trait_th": "สง่างาม ยุติธรรม และแสวงหาความกลมกลืน",
    },
    "scorpio": {
        "en": "Scorpio", "th": "พิจิก", "glyph": "♏",
        "element_en": "Water", "element_th": "น้ำ",
        "modality_en": "Fixed", "modality_th": "มั่น",
        "ruler_en": "Pluto", "ruler_th": "พลูโต",
        "dates_en": "Oct 23 – Nov 21", "dates_th": "23 ต.ค. – 21 พ.ย.",
        "trait_en": "intense, loyal, and able to transform what you touch",
        "trait_th": "ลึกซึ้ง ซื่อสัตย์ และสามารถพลิกเปลี่ยนสิ่งที่สัมผัสได้",
    },
    "sagittarius": {
        "en": "Sagittarius", "th": "ธนู", "glyph": "♐",
        "element_en": "Fire", "element_th": "ไฟ",
        "modality_en": "Mutable", "modality_th": "ปรับ",
        "ruler_en": "Jupiter", "ruler_th": "พฤหัสบดี",
        "dates_en": "Nov 22 – Dec 21", "dates_th": "22 พ.ย. – 21 ธ.ค.",
        "trait_en": "adventurous, honest, and hungry for meaning",
        "trait_th": "รักการผจญภัย ตรงไปตรงมา และใฝ่หาความหมาย",
    },
    "capricorn": {
        "en": "Capricorn", "th": "มังกร", "glyph": "♑",
        "element_en": "Earth", "element_th": "ดิน",
        "modality_en": "Cardinal", "modality_th": "นำ",
        "ruler_en": "Saturn", "ruler_th": "เสาร์",
        "dates_en": "Dec 22 – Jan 19", "dates_th": "22 ธ.ค. – 19 ม.ค.",
        "trait_en": "ambitious, patient, and built to last",
        "trait_th": "มุ่งมั่น อดทน และสร้างสิ่งที่อยู่ได้นาน",
    },
    "aquarius": {
        "en": "Aquarius", "th": "กุมภ์", "glyph": "♒",
        "element_en": "Air", "element_th": "ลม",
        "modality_en": "Fixed", "modality_th": "มั่น",
        "ruler_en": "Uranus", "ruler_th": "ยูเรนัส",
        "dates_en": "Jan 20 – Feb 18", "dates_th": "20 ม.ค. – 18 ก.พ.",
        "trait_en": "original, humanitarian, and ahead of your time",
        "trait_th": "มีเอกลักษณ์ ใจกว้างต่อเพื่อนมนุษย์ และก้าวล้ำกว่าเวลา",
    },
    "pisces": {
        "en": "Pisces", "th": "มีน", "glyph": "♓",
        "element_en": "Water", "element_th": "น้ำ",
        "modality_en": "Mutable", "modality_th": "ปรับ",
        "ruler_en": "Neptune", "ruler_th": "เนปจูน",
        "dates_en": "Feb 19 – Mar 20", "dates_th": "19 ก.พ. – 20 มี.ค.",
        "trait_en": "imaginative, compassionate, and quietly wise",
        "trait_th": "มีจินตนาการ เมตตา และมีปัญญาอย่างเงียบงาม",
    },
}

ANIMAL_TRAITS = {
    "rat": {
        "en": "clever, resourceful, and quick to spot an opening",
        "th": "ฉลาด มีไหวพริบ และมองเห็นโอกาสได้เร็ว",
    },
    "ox": {
        "en": "steady, hardworking, and quietly strong",
        "th": "มั่นคง ขยัน และเข้มแข็งอย่างสงบ",
    },
    "tiger": {
        "en": "brave, magnetic, and born to lead with heart",
        "th": "กล้าหาญ มีแรงดึงดูด และเกิดมาเพื่อนำด้วยหัวใจ",
    },
    "rabbit": {
        "en": "gentle, elegant, and skilled at keeping the peace",
        "th": "อ่อนโยน สง่างาม และเก่งในการรักษาความสงบ",
    },
    "dragon": {
        "en": "visionary, proud, and larger than life",
        "th": "มีวิสัยทัศน์ ภาคภูมิ และเปล่งประกายเกินใคร",
    },
    "snake": {
        "en": "wise, private, and deeply perceptive",
        "th": "มีปัญญา เก็บตัว และมองอะไรได้ลึก",
    },
    "horse": {
        "en": "free-spirited, energetic, and hungry for the open road",
        "th": "รักอิสระ พลังสูง และใฝ่หาหนทางที่กว้างไกล",
    },
    "goat": {
        "en": "artistic, kind, and moved by beauty",
        "th": "มีศิลปะ ใจดี และซาบซึ้งในความงาม",
    },
    "monkey": {
        "en": "witty, inventive, and impossible to pin down",
        "th": "มีอารมณ์ขัน ช่างประดิษฐ์ และจับให้คงที่ได้ยาก",
    },
    "rooster": {
        "en": "precise, proud, and unafraid to speak the truth",
        "th": "ละเอียด ภูมิใจในตน และไม่กลัวที่จะพูดความจริง",
    },
    "dog": {
        "en": "loyal, just, and fiercely protective of your people",
        "th": "ซื่อสัตย์ รักความถูกต้อง และปกป้องคนของคุณอย่างมั่นคง",
    },
    "pig": {
        "en": "generous, sincere, and lucky in the long run",
        "th": "ใจกว้าง จริงใจ และมักมีโชคในระยะยาว",
    },
}

LIFE_PATH = {
    1: {
        "title_en": "The Pioneer", "title_th": "ผู้บุกเบิก",
        "en": "You are here to begin things. Independence, courage, and a clear voice are your native gifts.",
        "th": "คุณเกิดมาเพื่อเริ่มต้นสิ่งใหม่ ความเป็นตัวของตัวเอง ความกล้า และเสียงที่ชัดเจนคือของขวัญติดตัว",
    },
    2: {
        "title_en": "The Peacemaker", "title_th": "ผู้ประสาน",
        "en": "You are here to bring people together. Sensitivity and partnership are your quiet superpowers.",
        "th": "คุณเกิดมาเพื่อเชื่อมผู้คน ความละเอียดอ่อนและการร่วมมือคือพลังเงียบของคุณ",
    },
    3: {
        "title_en": "The Artist", "title_th": "นักสร้างสรรค์",
        "en": "You are here to express. Joy, language, and creativity want to move through you.",
        "th": "คุณเกิดมาเพื่อแสดงออก ความสุข ภาษา และความคิดสร้างสรรค์อยากไหลผ่านคุณ",
    },
    4: {
        "title_en": "The Builder", "title_th": "ผู้สร้างรากฐาน",
        "en": "You are here to make things last. Patience, skill, and honest work become your temple.",
        "th": "คุณเกิดมาเพื่อสร้างสิ่งที่อยู่ได้นาน ความอดทน ทักษะ และงานจริงจังคือวิหารของคุณ",
    },
    5: {
        "title_en": "The Traveler", "title_th": "นักเดินทาง",
        "en": "You are here to taste freedom. Change, curiosity, and experience are your teachers.",
        "th": "คุณเกิดมาเพื่อลิ้มรสอิสรภาพ การเปลี่ยนแปลง ความอยากรู้ และประสบการณ์คือครูของคุณ",
    },
    6: {
        "title_en": "The Guardian", "title_th": "ผู้พิทักษ์",
        "en": "You are here to care. Home, beauty, and responsibility sit close to your heart.",
        "th": "คุณเกิดมาเพื่อดูแล บ้าน ความงาม และความรับผิดชอบอยู่ใกล้หัวใจคุณ",
    },
    7: {
        "title_en": "The Seeker", "title_th": "ผู้แสวงหา",
        "en": "You are here to understand. Solitude, study, and inner vision sharpen your wisdom.",
        "th": "คุณเกิดมาเพื่อทำความเข้าใจ ความสงบ การเรียนรู้ และวิสัยทัศน์ภายในลับปัญญาของคุณ",
    },
    8: {
        "title_en": "The Achiever", "title_th": "ผู้สำเร็จ",
        "en": "You are here to steward power. Ambition and fairness can build a life of real substance.",
        "th": "คุณเกิดมาเพื่อบริหารพลังและทรัพยากร ความมุ่งมั่นที่มาคู่กับความยุติธรรมจะสร้างชีวิตที่มั่นคงจริง",
    },
    9: {
        "title_en": "The Humanitarian", "title_th": "ผู้เสียสละ",
        "en": "You are here to complete cycles and give back. Compassion is your widest horizon.",
        "th": "คุณเกิดมาเพื่อปิดวงจรและคืนสิ่งดีสู่โลก ความเมตตาคือขอบฟ้าที่กว้างที่สุดของคุณ",
    },
    11: {
        "title_en": "The Illuminator", "title_th": "ผู้จุดแสง",
        "en": "A master number. You are here to inspire. Intuition arrives like lightning — trust it, then ground it.",
        "th": "เลขศาสตร์ระดับปรมาจารย์ คุณเกิดมาเพื่อสร้างแรงบันดาลใจ สัญชาตญาณมาไวเหมือนสายฟ้า — เชื่อมัน แล้วลงมือทำให้เป็นจริง",
    },
    22: {
        "title_en": "The Master Builder", "title_th": "ปรมาจารย์ผู้สร้าง",
        "en": "A master number. You can turn a dream into something the world can stand inside. Think large, build carefully.",
        "th": "เลขศาสตร์ระดับปรมาจารย์ คุณสามารถเปลี่ยนความฝันให้เป็นสิ่งที่โลกยืนอยู่ได้ คิดให้ใหญ่ สร้างอย่างรอบคอบ",
    },
    33: {
        "title_en": "The Master Teacher", "title_th": "ปรมาจารย์ผู้สอน",
        "en": "A rare master number. Your path is loving service — healing, teaching, and lifting others without losing yourself.",
        "th": "เลขศาสตร์ปรมาจารย์ที่หายาก เส้นทางของคุณคือการรับใช้ด้วยความรัก — เยียวยา สอน และยกระดับผู้อื่นโดยไม่ลืมดูแลตัวเอง",
    },
}

ELEMENT_NOTE = {
    "wood": {
        "en": "Wood years grow through kindness and new branches — start something living.",
        "th": "ปีไม้เติบโตด้วยความเมตตาและกิ่งใหม่ — เริ่มสิ่งที่มีชีวิต",
    },
    "fire": {
        "en": "Fire years ask for courage and visibility — let yourself be seen.",
        "th": "ปีไฟเรียกร้องความกล้าและการปรากฏตัว — ยอมให้โลกรู้จักคุณ",
    },
    "earth": {
        "en": "Earth years reward patience and foundation — build slowly, build well.",
        "th": "ปีดินตอบแทนความอดทนและรากฐาน — สร้างช้า สร้างให้ดี",
    },
    "metal": {
        "en": "Metal years refine and cut away excess — choose quality over noise.",
        "th": "ปีทองลับคมและตัดส่วนเกิน — เลือกคุณภาพมากกว่าเสียงรบกวน",
    },
    "water": {
        "en": "Water years deepen intuition and feeling — listen before you leap.",
        "th": "ปีน้ำทำให้สัญชาตญาณลึกขึ้น — ฟังก่อนที่จะกระโดด",
    },
}

HOUR_NOTE = {
    "dawn": {
        "en": "Born at dawn, you carry the first light — beginnings come naturally to you.",
        "th": "เกิดยามรุ่งสาง คุณถือแสงแรกไว้ — การเริ่มต้นเป็นเรื่องธรรมชาติสำหรับคุณ",
    },
    "morning": {
        "en": "A morning birth gives a clear, rising mind — you think best when the day is young.",
        "th": "การเกิดยามเช้ามอบจิตที่แจ่มและพุ่งขึ้น — คุณคิดได้ดีที่สุดเมื่อวันยังใหม่",
    },
    "afternoon": {
        "en": "An afternoon birth warms your will — you gather strength as others fade.",
        "th": "การเกิดยามบ่ายทำให้เจตจำนงอุ่นขึ้น — คุณเก็บแรงเมื่อคนอื่นเริ่มหมด",
    },
    "evening": {
        "en": "An evening birth softens the voice of the heart — you read rooms and feelings well.",
        "th": "การเกิดยามเย็นทำให้น้ำเสียงของหัวใจอ่อนโยน — คุณอ่านบรรยากาศและความรู้สึกได้ดี",
    },
    "night": {
        "en": "A night birth keeps a private moon inside you — dreams and instinct are part of your craft.",
        "th": "การเกิดยามค่ำคืนเก็บพระจันทร์ส่วนตัวไว้ในตัว — ความฝันและสัญชาตญาณเป็นส่วนหนึ่งของฝีมือคุณ",
    },
}

DAYS_EN = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DAYS_TH = ["วันอาทิตย์", "วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์"]


def western_zodiac(d: date) -> str:
    md = (d.month, d.day)
    bounds = [((1, 20), "aquarius"), ((2, 19), "pisces"), ((3, 21), "aries"), ((4, 20), "taurus"),
              ((5, 21), "gemini"), ((6, 21), "cancer"), ((7, 23), "leo"), ((8, 23), "virgo"),
              ((9, 23), "libra"), ((10, 23), "scorpio"), ((11, 22), "sagittarius"), ((12, 22), "capricorn")]
    sign = "capricorn"
    for start, key in bounds:
        if md >= start:
            sign = key
    return sign


def lunar_year(d: date) -> int:
    year = d.year
    if year in CNY:
        m, day = CNY[year]
        if (d.month, d.day) < (m, day):
            return year - 1
        return year
    # Rough fallback outside the table: treat Feb 4 as the cusp.
    if (d.month, d.day) < (2, 4):
        return year - 1
    return year


def chinese_zodiac(d: date) -> dict[str, Any]:
    ly = lunar_year(d)
    # 1924 = Yang Wood Rat = cycle index 0
    idx = (ly - 1924) % 60
    animal = ANIMALS[idx % 12]
    stem = STEMS[idx % 10]
    return {
        "lunarYear": ly,
        "key": animal[0],
        "animal_en": animal[1],
        "animal_th": animal[2],
        "element": stem[0],
        "polarity": stem[1],
        "element_en": stem[2],
        "element_th": stem[3],
        "polarity_en": stem[4],
        "polarity_th": stem[5],
        "label_en": f"{stem[2]} {animal[1]}",
        "label_th": f"{animal[2]} ธาตุ{stem[3]}",
    }


def reduce_number(n: int, keep_master: bool = True) -> int:
    while n > 9 and not (keep_master and n in (11, 22, 33)):
        n = sum(int(ch) for ch in str(n))
    return n


def life_path_number(d: date) -> int:
    total = sum(int(ch) for ch in d.strftime("%Y%m%d"))
    return reduce_number(total, keep_master=True)


def hour_bucket(birth_time: str | None) -> str | None:
    if not birth_time:
        return None
    try:
        hour = int(birth_time.split(":")[0])
        minute = int(birth_time.split(":")[1]) if ":" in birth_time else 0
    except (ValueError, IndexError):
        return None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    if 5 <= hour < 7:
        return "dawn"
    if 7 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 20:
        return "evening"
    return "night"


def format_date_en(d: date) -> str:
    return d.strftime("%B %d, %Y").replace(" 0", " ")


TH_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
]


def format_date_th(d: date) -> str:
    return f"{d.day} {TH_MONTHS[d.month]} พ.ศ. {d.year + 543}"


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def parse_birth(date_str: Any, time_str: Any = None, today: date | None = None) -> tuple[date | None, str | None]:
    """Validate an optional birth date (YYYY-MM-DD) and time (HH:MM). Empty values are fine."""
    ds = str(date_str or "").strip()
    ts = str(time_str or "").strip()[:5]
    if not ds:
        return None, None
    if not DATE_RE.match(ds):
        raise ValueError("Please enter a valid birth date.")
    try:
        d = datetime.strptime(ds, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Please enter a valid birth date.") from None
    if d.year < 1900 or d > (today or date.today()):
        raise ValueError("Please enter a valid birth date.")
    if ts and not TIME_RE.match(ts):
        raise ValueError("Please enter a valid birth time.")
    return d, (ts or None)


HOUR_TH = {"dawn": "รุ่งสาง", "morning": "ยามเช้า", "afternoon": "ยามบ่าย", "evening": "ยามเย็น", "night": "ยามค่ำคืน"}
HOUR_EN = {"dawn": "Dawn", "morning": "Morning", "afternoon": "Afternoon", "evening": "Evening", "night": "Night"}


def build_profile(d: date, birth_time: str | None = None) -> dict[str, Any]:
    """Everything the profile panel shows, in both languages (the page can switch without refetching)."""
    zkey = western_zodiac(d)
    z = ZODIAC[zkey]
    c = chinese_zodiac(d)
    n = life_path_number(d)
    lp = LIFE_PATH[n]
    wd = (d.weekday() + 1) % 7  # Python Monday=0 -> Sunday=0
    hour = hour_bucket(birth_time)
    return {
        "birthDate": d.isoformat(),
        "birthTime": birth_time,
        "dateTh": format_date_th(d),
        "dateEn": format_date_en(d),
        "weekdayTh": DAYS_TH[wd],
        "weekdayEn": DAYS_EN[wd],
        "chinese": {
            "key": c["key"], "lunarYear": c["lunarYear"],
            "th": c["label_th"], "en": c["label_en"],
            "meaningTh": ANIMAL_TRAITS[c["key"]]["th"], "meaningEn": ANIMAL_TRAITS[c["key"]]["en"],
            "elementTh": ELEMENT_NOTE[c["element"]]["th"], "elementEn": ELEMENT_NOTE[c["element"]]["en"],
        },
        "number": {
            "value": n, "master": n in (11, 22, 33),
            "titleTh": lp["title_th"], "titleEn": lp["title_en"],
            "meaningTh": lp["th"], "meaningEn": lp["en"],
        },
        "western": {
            "key": zkey, "glyph": z["glyph"], "th": "ราศี" + z["th"], "en": z["en"],
            "datesTh": z["dates_th"], "datesEn": z["dates_en"],
            "elementTh": "ธาตุ" + z["element_th"], "elementEn": z["element_en"],
            "meaningTh": z["trait_th"], "meaningEn": z["trait_en"],
        },
        "hour": ({"key": hour, "th": HOUR_TH[hour], "en": HOUR_EN[hour],
                  "meaningTh": HOUR_NOTE[hour]["th"], "meaningEn": HOUR_NOTE[hour]["en"]} if hour else None),
    }


