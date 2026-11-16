#!/usr/bin/env python3
"""ถามจันทร์ (Ask the Moon) — destiny reading server.

Serves the static web app, POST /api/reading, the question-credit and
PromptPay order API (see credits.py), and a token-protected /admin page.
Uses an OpenAI-compatible LLM when OPENAI_API_KEY is set; otherwise a
template generator so the demo works offline. Never invents an API key.
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
import traceback
import urllib.error
import urllib.request
from datetime import date, datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import credits as billing

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
PORT = int(os.environ.get("PORT", "5050"))
HOST = os.environ.get("HOST", "0.0.0.0")
DATA_DIR = os.environ.get("DATA_DIR") or str(ROOT / "data")
SERVICE, STORE_KIND, STORE_PROBLEM = billing.make_service(DATA_DIR)

# First day of each Chinese lunar year (Gregorian month, day).
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

ZODIAC_ORDER = [
    ("capricorn", 12, 22, "aquarius"),
    ("aquarius", 1, 20, "pisces"),
    ("pisces", 2, 19, "aries"),
    ("aries", 3, 21, "taurus"),
    ("taurus", 4, 20, "gemini"),
    ("gemini", 5, 21, "cancer"),
    ("cancer", 6, 21, "leo"),
    ("leo", 7, 23, "virgo"),
    ("virgo", 8, 23, "libra"),
    ("libra", 9, 23, "scorpio"),
    ("scorpio", 10, 23, "sagittarius"),
    ("sagittarius", 11, 22, "capricorn"),
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
        "th": "ฉลาด มีไหวพริธ และมองเห็นโอกาสได้เร็ว",
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

# Fix the typo I accidentally left in ox th - I'll fix after writing
# "อย่าง Conditionallyสงบ" should be "อย่างสงบ"

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
        "th": "คุณเกิดมาเพื่อดูแลพลัง อำนาจ ความมุ่งมั่นและความยุติธรรมสร้างชีวิตที่มีสาระจริง",
    },
    9: {
        "title_en": "The Humanitarian", "title_th": "ผู้เสียสละ",
        "en": "You are here to complete cycles and give back. Compassion is your widest horizon.",
        "th": "คุณเกิดมาเพื่อปิดวงจรและคืนสิ่งดีสู่โลก ความเมตตาคือขอบฟ้าที่กว้างที่สุดของคุณ",
    },
    11: {
        "title_en": "The Illuminator", "title_th": "ผู้จุดแสง",
        "en": "A master number. You are here to inspire. Intuition arrives like lightning — trust it, then ground it.",
        "th": "เลขศาสตร์ระดับปรมาจารย์ คุณเกิดมาเพื่อสร้างแรงบันดาลใจ สัญชาตญาณมาเหมือนสายฟ้า — วางใจ แล้วลงสู่พื้นดิน",
    },
    22: {
        "title_en": "The Master Builder", "title_th": "ปรมาจารย์ผู้สร้าง",
        "en": "A master number. You can turn a dream into something the world can stand inside. Think large, build carefully.",
        "th": "เลขศาสตร์ระดับปรมาจารย์ คุณสามารถเปลี่ยนความฝันให้เป็นสิ่งที่โลกยืนอยู่ได้ คิดให้ใหญ่ สร้างอย่างรอบคอบ",
    },
    33: {
        "title_en": "The Master Teacher", "title_th": "ปรมาจารย์ผู้สอน",
        "en": "A rare master number. Your path is loving service — healing, teaching, and lifting others without losing yourself.",
        "th": "เลขศาสตร์ปรมาจารย์ที่หายาก เส้นทางของคุณคือการรับใช้ด้วยความรัก — เยียวยา สอน และยกระดับผู้อื่นโดยไม่ทำลายตัวเอง",
    },
}

TOPICS = {
    "love": {"en": "love", "th": "ความรัก"},
    "career": {"en": "career", "th": "การงาน"},
    "money": {"en": "money", "th": "การเงิน"},
    "life_path": {"en": "life path", "th": "เส้นทางชีวิต"},
}

TOPIC_GUIDE = {
    "love": {
        "en": (
            "In love, your {sign} heart wants a bond that feels safe enough to be true. "
            "The {animal} in you stays loyal once trust is earned, but you must not hide your needs "
            "behind silence. This chapter asks you to name what you feel before the other person has to guess. "
            "A relationship that honors both tenderness and freedom will grow; one that asks you to shrink will fade."
        ),
        "th": (
            "ในเรื่องรัก หัวใจ{sign}ของคุณต้องการความผูกพันที่ปลอดภัยพอจะเป็นตัวเองได้ "
            "พลังปี{animal}ทำให้คุณซื่อสัตย์เมื่อความไว้ใจเกิดแล้ว แต่ห้ามเก็บความต้องการไว้เงียบเกินไป "
            "ช่วงนี้ชวนให้คุณเอ่ยความรู้สึกก่อนที่อีกฝ่ายจะต้องเดา "
            "ความสัมพันธ์ที่ให้ทั้งความอ่อนโยนและอิสระจะงอกงาม ส่วนที่ให้คุณต้องหดตัวจะจางไปเอง"
        ),
    },
    "career": {
        "en": (
            "At work, your {sign} nature wants a role with meaning, not only a title. "
            "The {animal} year of your birth favors {career_style}. "
            "Doors open when you show a finished piece of work, not just a plan. "
            "In the next cycle, one quiet skill you already have becomes more valuable than a brand-new start."
        ),
        "th": (
            "เรื่องงาน ธรรมชาติ{sign}ของคุณต้องการบทบาทที่มีความหมาย ไม่ใช่แค่ตำแหน่ง "
            "ปี{animal}ที่คุณเกิดเกื้อหนุนให้{career_style} "
            "ประตูจะเปิดเมื่อคุณโชว์ผลงานที่เสร็จแล้ว ไม่ใช่แค่แผน "
            "ในรอบถัดไป ทักษะเงียบที่คุณมีอยู่แล้วจะมีค่ากว่าการเริ่มนับหนึ่งใหม่"
        ),
    },
    "money": {
        "en": (
            "Money follows the way you treat your energy. As a {sign} with a {animal} imprint, "
            "you do better when income is tied to something you can stand behind. "
            "Avoid bargains that feel hurried. A slower, cleaner stream — a skill, a small offer, a trusted partner — "
            "will outgrow a sudden windfall. Keep a reserve; luck likes a prepared pocket."
        ),
        "th": (
            "เงินเดินตามวิธีที่คุณใช้พลังงาน ในฐานะ{sign}ที่มีรอยปี{animal} "
            "คุณจะรุ่งเมื่อรายได้ผูกกับสิ่งที่ยืนอยู่ข้างได้ "
            "หลีกเลี่ยงข้อเสนอที่เร่งรีบ ลำธารที่ช้าแต่ใส — ทักษะ ข้อเสนอเล็ก ๆ หรือหุ้นส่วนที่ไว้ใจได้ — "
            "จะโตกว่าโชคใหญ่ที่มาฉับพลัน เก็บเงินสำรองไว้ โชคชอบกระเป๋าที่พร้อม"
        ),
    },
    "life_path": {
        "en": (
            "Your wider path is not a straight road; it is a constellation. "
            "Being {sign}, born in a {animal} year, you grow by trusting both instinct and craft. "
            "The question is not 'Who should I become?' but 'What am I already carrying that wants a larger stage?' "
            "Give that gift a daily practice, and the map will keep revealing itself."
        ),
        "th": (
            "เส้นทางกว้างของคุณไม่ใช่ถนนตรง แต่เป็นกลุ่มดาว "
            "การเป็น{sign} ผู้เกิดปี{animal} คุณเติบโตเมื่อเชื่อทั้งสัญชาตญาณและฝีมือ "
            "คำถามไม่ใช่ 'ฉันควรเป็นใคร' แต่คือ 'ฉันถืออะไรอยู่แล้วที่อยากได้เวทีที่ใหญ่กว่านี้' "
            "มอบของขวัญนั้นให้กับการฝึกฝนทุกวัน แผนที่จะค่อย ๆ เผยตัวเอง"
        ),
    },
}

CAREER_STYLE = {
    "rat": {"en": "clever timing and well-chosen collaborations", "th": "จังหวะที่ฉลาดและการร่วมมือที่คัดมาดี"},
    "ox": {"en": "steady craft and long-term reputation", "th": "ฝีมือที่สะสมและความน่าเชื่อถือระยะยาว"},
    "tiger": {"en": "brave moves and visible leadership", "th": "ก้าวที่กล้าและการนำที่มองเห็นได้"},
    "rabbit": {"en": "diplomacy, taste, and careful positioning", "th": "การเจรจา รสนิยม และการวางตัวที่ประณีต"},
    "dragon": {"en": "bold vision and work that can be seen from afar", "th": "วิสัยทัศน์ใหญ่และงานที่มองเห็นได้แต่ไกล"},
    "snake": {"en": "strategy, research, and quiet influence", "th": "กลยุทธ์ การค้นคว้า และอิทธิพลอย่างเงียบ"},
    "horse": {"en": "movement, sales of ideas, and independent paths", "th": "การเคลื่อนไหว การขายไอเดีย และเส้นทางอิสระ"},
    "goat": {"en": "creative work and sincere care for clients", "th": "งานสร้างสรรค์และความเอาใจใส่ลูกค้าอย่างจริงใจ"},
    "monkey": {"en": "invention, problem-solving, and playful skill", "th": "การประดิษฐ์ การแก้ปัญหา และทักษะที่คล่องแคล่ว"},
    "rooster": {"en": "high standards and clear, public competence", "th": "มาตรฐานสูงและความสามารถที่ชัดเจนต่อสาธารณะ"},
    "dog": {"en": "trustworthy service and causes you believe in", "th": "บริการที่ไว้ใจได้และงานที่คุณเชื่อจริง"},
    "pig": {"en": "generous offers and sincere, lasting networks", "th": "ข้อเสนอที่ใจกว้างและเครือข่ายจริงใจที่อยู่ได้นาน"},
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

CLOSINGS = {
    "en": [
        "The stars do not command you; they describe the weather. Walk with them, not under them.",
        "May this reading be a lantern, not a cage. Your choices remain the brightest star.",
        "Hold what resonates, and leave the rest to the night sky. You already know more than you think.",
    ],
    "th": [
        "ดวงดาวไม่ได้บัญชาคุณ แต่เล่าอากาศของเส้นทาง เดินกับมัน ไม่ใช่เดินใต้เงามัน",
        "ขอให้อ่านดวงนี้เป็นโคมไฟ ไม่ใช่กรงขัง ทางเลือกของคุณยังคงเป็นดาวที่สว่างที่สุด",
        "เก็บสิ่งที่สั่นใจ และปล่อยที่เหลือคืนสู่ท้องฟ้า คุณรู้อยู่แล้วมากกว่าที่คิด",
    ],
}

LUCKY_COLORS = {
    "fire": [{"en": "gold", "th": "ทอง", "hex": "#d4af37"}, {"en": "crimson", "th": "แดงกำมะหยี่", "hex": "#8b1e3f"}],
    "earth": [{"en": "olive", "th": "เขียวมะกอก", "hex": "#6b7a3a"}, {"en": "sand", "th": "ทรายทอง", "hex": "#c4a574"}],
    "air": [{"en": "sky blue", "th": "ฟ้าอ่อน", "hex": "#7ec8e3"}, {"en": "silver", "th": "เงิน", "hex": "#c0c0c0"}],
    "water": [{"en": "moon white", "th": "ขาวจันทร์", "hex": "#f2efe9"}, {"en": "sea teal", "th": "เขียวน้ำทะเล", "hex": "#1f6f6a"}],
    "wood": [{"en": "jade", "th": "หยก", "hex": "#2e8b6f"}, {"en": "leaf green", "th": "เขียวใบไม้", "hex": "#3d6b4f"}],
    "metal": [{"en": "ivory", "th": "งาช้าง", "hex": "#f5f0e6"}, {"en": "bronze", "th": "ทองแดงเก่า", "hex": "#b08d57"}],
}

DAYS_EN = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DAYS_TH = ["วันอาทิตย์", "วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์"]


def western_zodiac(d: date) -> str:
    month, day = d.month, d.day
    for i, (sign, start_m, start_d, _nxt) in enumerate(ZODIAC_ORDER):
        prev_sign = ZODIAC_ORDER[i - 1][0]
        if (month == start_m and day >= start_d) or (
            month == (start_m % 12) + 1 and day < ZODIAC_ORDER[(i + 1) % 12][2] and start_m != 12
        ):
            # clearer logic below
            pass
    # Straightforward boundary check
    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "capricorn"
    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "aquarius"
    if (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "pisces"
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "aries"
    if (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "taurus"
    if (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "gemini"
    if (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "cancer"
    if (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "leo"
    if (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "virgo"
    if (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "libra"
    if (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "scorpio"
    return "sagittarius"


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


def lucky_set(d: date, path: int, animal_key: str, element: str) -> dict[str, Any]:
    seed = f"{d.isoformat()}|{path}|{animal_key}"
    rng = random.Random(seed)
    numbers = {path, d.day, reduce_number(d.month + d.day, keep_master=False)}
    while len(numbers) < 5:
        numbers.add(rng.randint(1, 9) if rng.random() < 0.6 else rng.randint(10, 28))
    ordered = sorted(numbers)
    west_el = ZODIAC[western_zodiac(d)]["element_en"].lower()
    colors = (LUCKY_COLORS.get(west_el) or []) + (LUCKY_COLORS.get(element) or [])
    # unique by hex
    seen = set()
    uniq = []
    for c in colors:
        if c["hex"] not in seen:
            uniq.append(c)
            seen.add(c["hex"])
    day_idx = (path + d.day) % 7
    return {
        "numbers": ordered[:5],
        "colors": uniq[:3],
        "day_en": DAYS_EN[day_idx],
        "day_th": DAYS_TH[day_idx],
    }


def pick(rng: random.Random, items: list[str]) -> str:
    return rng.choice(items)


def template_reading(chart: dict[str, Any], topic: str, question: str, lang: str) -> str:
    rng = random.Random(chart["seed"])
    z = chart["zodiac"]
    c = chart["chinese"]
    p = chart["path"]
    lp = LIFE_PATH[p]
    name = chart["name"]
    sign = z["th"] if lang == "th" else z["en"]
    animal = c["animal_th"] if lang == "th" else c["animal_en"]
    trait_z = z["trait_th"] if lang == "th" else z["trait_en"]
    trait_a = ANIMAL_TRAITS[c["key"]]["th" if lang == "th" else "en"]
    path_text = lp["th" if lang == "th" else "en"]
    path_title = lp["title_th" if lang == "th" else "title_en"]
    elem_note = ELEMENT_NOTE[c["element"]]["th" if lang == "th" else "en"]
    guide = TOPIC_GUIDE[topic]["th" if lang == "th" else "en"].format(
        sign=sign,
        animal=animal,
        career_style=CAREER_STYLE[c["key"]]["th" if lang == "th" else "en"],
    )
    hour = chart.get("hour")
    hour_line = ""
    if hour:
        hour_line = HOUR_NOTE[hour]["th" if lang == "th" else "en"]

    if lang == "th":
        opening = (
            f"{name} นักเดินทางใต้ท้องฟ้า ดวงของคุณในวันนี้ถูกจัดเรียงจากวันเกิด "
            f"{chart['birth_fmt_th']} "
            f"คุณเกิดภายใต้ราศี{z['th']} {z['glyph']} ธาตุ{z['element_th']} "
            f"ซึ่งโดยธรรมชาติแล้วคุณ{trait_z}."
        )
        chinese = (
            f"ในปฏิทินจันทรคติ คุณเกิดปี{c['label_th']} "
            f"— {trait_a}. "
            f"{elem_note}"
        )
        path_para = (
            f"เลขศาสตร์เส้นทางชีวิตของคุณคือ {p} · {path_title}. {path_text}"
        )
        q_para = ""
        if question:
            q_para = (
                f"ต่อคำถามที่คุณวางไว้ใต้ดาว — «{question}» — "
                f"ดวงชี้ว่าคำตอบไม่ได้อยู่นอกตัว แต่มาจากการที่คุณยอมใช้คุณภาพของราศี{z['th']} "
                f"และพลังปี{c['animal_th']} อย่างตรงไปตรงมา "
                f"อย่ารอสัญญาณที่สมบูรณ์แบบ เริ่มจากก้าวเล็กที่สั่นใจแล้วดูว่าประตูบานไหนเปิดเอง."
            )
        close = pick(rng, CLOSINGS["th"])
        parts = [opening, chinese, path_para]
        if hour_line:
            parts.append(hour_line)
        parts.append(guide)
        if q_para:
            parts.append(q_para)
        parts.append(close)
        return "\n\n".join(parts)

    opening = (
        f"{name}, traveler under the open sky, your chart is drawn from {chart['birth_fmt_en']}. "
        f"You were born under {z['en']} {z['glyph']}, a {z['element_en']} sign, "
        f"and by nature you are {trait_z}."
    )
    chinese = (
        f"In the lunar calendar you arrived in the year of the {c['label_en']} — {trait_a}. "
        f"{elem_note}"
    )
    path_para = f"Your numerology life path is {p} · {path_title}. {path_text}"
    q_para = ""
    if question:
        q_para = (
            f"To the question you laid beneath the stars — “{question}” — "
            f"the chart answers that the way through is not outside you. "
            f"It lives in using your {z['en']} nature and {c['animal_en']} strength without apology. "
            f"Do not wait for a perfect sign. Take the small step that already hums, and watch which door opens by itself."
        )
    close = pick(rng, CLOSINGS["en"])
    parts = [opening, chinese, path_para]
    if hour_line:
        parts.append(hour_line)
    parts.append(guide)
    if q_para:
        parts.append(q_para)
    parts.append(close)
    return "\n\n".join(parts)


def premium_teaser(chart: dict[str, Any], luck: dict[str, Any], lang: str) -> dict[str, Any]:
    z = chart["zodiac"]
    c = chart["chinese"]
    p = chart["path"]
    if lang == "th":
        forecast = (
            f"พยากรณ์ 12 เดือนสำหรับราศี{z['th']} ปี{c['label_th']} "
            f"ชี้ว่าช่วงต้นปีเป็นเวลาเก็บแรง กลางปีมีข่าวเรื่องพันธมิตร "
            f"และปลายปีเหมาะแก่การเก็บเกี่ยวผลจากเลข {p}. "
            f"รายละเอียดวันดี เดือนควรระวัง และคำแนะนำเฉพาะบุคคลถูกล็อกไว้ในบทอ่านลึก."
        )
        gift = f"ของขวัญซ่อนเร้นของเลข {p} คือความสามารถที่คนรอบตัวพึ่งพาได้ โดยที่คุณเองอาจมองข้าม"
        shadow = "บททดสอบซ่อนเร้นคือการไม่ลดค่าตัวเองเพื่อรักษาความสงบ"
        compat = f"เข้ากันได้ดีกับพลังน้ำและดิน โดยเฉพาะผู้ที่เกิดปีที่เกื้อกูลกับปี{c['animal_th']}"
    else:
        forecast = (
            f"A 12-month forecast for {z['en']} born in a {c['label_en']} year "
            f"points to a quiet gathering in the first season, a partnership message at midyear, "
            f"and a harvest toward the end that rewards life path {p}. "
            f"Exact fortunate dates, months to tread softly, and a personal counsel stay inside the deep reading."
        )
        gift = f"The hidden gift of path {p} is a talent others already lean on, even when you overlook it."
        shadow = "The hidden test is refusing to shrink yourself just to keep the peace."
        compat = f"You harmonize with Water and Earth, especially those born in years that support the {c['animal_en']}."
    return {
        "forecast": forecast,
        "gift": gift,
        "shadow": shadow,
        "compatibility": compat,
        "numbers": luck["numbers"],
        "colors": luck["colors"],
        "day": luck["day_th"] if lang == "th" else luck["day_en"],
    }


LLM_TIMEOUT = 20


def _log_llm_failure(exc: Exception) -> None:
    # Never log request headers, bodies, or the API key.
    if isinstance(exc, urllib.error.HTTPError):
        try:
            exc.read()
        except Exception:
            pass
        print(f"LLM request failed (HTTP {exc.code}); using template generator.", file=sys.stderr)
    elif isinstance(exc, TimeoutError) or isinstance(getattr(exc, "reason", None), TimeoutError):
        print("LLM request timed out; using template generator.", file=sys.stderr)
    else:
        print(f"LLM request failed ({type(exc).__name__}); using template generator.", file=sys.stderr)


def llm_generate(
    chart: dict[str, Any], topic: str, question: str, lang: str
) -> tuple[str, dict[str, str]] | None:
    """Call an OpenAI-compatible LLM. Returns (reading, premium fields) or None."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    z = chart["zodiac"]
    c = chart["chinese"]
    lp = LIFE_PATH[chart["path"]]
    language = "Thai" if lang == "th" else "English"
    qline = question.strip() if question else "(no specific question)"
    hour = chart.get("hour") or "not provided"
    prompt = (
        f"Write a warm, mystical, personalized destiny reading in {language} for {chart['name']}.\n"
        f"Birth date: {chart['birth_fmt_en']} ({chart['birth_fmt_th']}). "
        f"Birth time / hour type: {hour}.\n"
        f"Western zodiac: {z['en']} ({z['th']}), {z['element_en']} element, ruled by {z['ruler_en']}. "
        f"By nature they are {z['trait_en']}.\n"
        f"Chinese zodiac: {c['label_en']} / {c['label_th']}.\n"
        f"Numerology life path number: {chart['path']} — {lp['title_en']} / {lp['title_th']}. {lp['en']}\n"
        f"Topic of this reading: {TOPICS[topic]['en']} ({TOPICS[topic]['th']}).\n"
        f"The visitor's question: {qline}\n\n"
        "Weave the zodiac, Chinese zodiac, life path number, topic, and question naturally into the prose. "
        "Write 4 to 6 short paragraphs of reasonable length, separated by blank lines. "
        "No medical, legal, or financial advice, and no guaranteed predictions. No scare tactics. "
        "Speak as a wise, kind astrologer. Do not mention that you are an AI. "
        "Do not use markdown, headings, bullet lists, or JSON. "
        f"Write the entire reading in {language}. End with a gentle blessing."
    )
    payload = {
        "model": model,
        "temperature": 0.85,
        "max_tokens": 2048,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a gifted, ethical astrologer writing personalized destiny readings. "
                    "Reply with the reading only, as plain text."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=LLM_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = (data["choices"][0]["message"]["content"] or "").strip()
        if not text:
            return None
        # If a model still returns a JSON wrapper, prefer the reading field.
        if text.startswith("{") or text.startswith("```"):
            print("LLM response was not plain text; using template generator.", file=sys.stderr)
            return None
        return text, {}
    except Exception as exc:
        _log_llm_failure(exc)
        return None



def parse_birth(date_str: str) -> date:
    return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()


def format_date_en(d: date) -> str:
    return d.strftime("%B %d, %Y").replace(" 0", " ")


TH_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
]


def format_date_th(d: date) -> str:
    return f"{d.day} {TH_MONTHS[d.month]} {d.year}"


def build_chart(name: str, birth: date, birth_time: str | None) -> dict[str, Any]:
    zkey = western_zodiac(birth)
    chinese = chinese_zodiac(birth)
    path = life_path_number(birth)
    hour = hour_bucket(birth_time)
    return {
        "name": name,
        "birth": birth.isoformat(),
        "birthTime": birth_time,
        "birth_fmt_en": format_date_en(birth),
        "birth_fmt_th": format_date_th(birth),
        "zodiac_key": zkey,
        "zodiac": ZODIAC[zkey],
        "chinese": chinese,
        "path": path,
        "path_meta": LIFE_PATH[path],
        "hour": hour,
        "seed": f"{name.lower()}|{birth.isoformat()}|{birth_time or ''}",
    }


def public_chart(chart: dict[str, Any], lang: str) -> dict[str, Any]:
    z = chart["zodiac"]
    c = chart["chinese"]
    p = chart["path"]
    lp = chart["path_meta"]
    return {
        "westernZodiac": {
            "key": chart["zodiac_key"],
            "sign": z["th"] if lang == "th" else z["en"],
            "signEn": z["en"],
            "signTh": z["th"],
            "glyph": z["glyph"],
            "element": z["element_th"] if lang == "th" else z["element_en"],
            "modality": z["modality_th"] if lang == "th" else z["modality_en"],
            "ruler": z["ruler_th"] if lang == "th" else z["ruler_en"],
            "dates": z["dates_th"] if lang == "th" else z["dates_en"],
        },
        "chineseZodiac": {
            "key": c["key"],
            "label": c["label_th"] if lang == "th" else c["label_en"],
            "animal": c["animal_th"] if lang == "th" else c["animal_en"],
            "element": c["element_th"] if lang == "th" else c["element_en"],
            "polarity": c["polarity_th"] if lang == "th" else c["polarity_en"],
            "lunarYear": c["lunarYear"],
        },
        "lifePath": {
            "number": p,
            "title": lp["title_th"] if lang == "th" else lp["title_en"],
            "summary": lp["th"] if lang == "th" else lp["en"],
            "master": p in (11, 22, 33),
        },
        "hour": chart["hour"],
    }


def parse_reading_request(body: dict[str, Any]) -> dict[str, Any]:
    name = str(body.get("name") or "").strip()
    if not name or len(name) > 80:
        raise ValueError("Please enter a name.")
    try:
        birth = parse_birth(str(body.get("birthDate") or ""))
    except ValueError as exc:
        raise ValueError("Please enter a valid birth date.") from exc
    today = date.today()
    if birth.year < 1900 or birth > today:
        raise ValueError("Please enter a birth date between 1900 and today.")
    raw_time = str(body.get("birthTime") or "").strip()
    birth_time = raw_time or None
    if birth_time and hour_bucket(birth_time) is None:
        raise ValueError("Please enter a valid birth time.")
    topic = str(body.get("topic") or "life_path").strip()
    if topic not in TOPICS:
        raise ValueError("Please choose a topic.")
    question = str(body.get("question") or "").strip()
    if len(question) > 280:
        raise ValueError("Please keep your question under 280 characters.")
    lang = "th" if str(body.get("lang") or "th").lower().startswith("th") else "en"
    return {"name": name, "birth": birth, "birth_time": birth_time,
            "topic": topic, "question": question, "lang": lang}


def generate_reading(params: dict[str, Any]) -> dict[str, Any]:
    name, birth, lang = params["name"], params["birth"], params["lang"]
    topic, question = params["topic"], params["question"]
    chart = build_chart(name, birth, params["birth_time"])
    luck = lucky_set(birth, chart["path"], chart["chinese"]["key"], chart["chinese"]["element"])
    source = "template"
    text = None
    premium = premium_teaser(chart, luck, lang)
    generated = llm_generate(chart, topic, question, lang)
    if generated:
        text, premium_ai = generated
        source = "llm"
        for key, value in premium_ai.items():
            premium[key] = value
    if not text:
        text = template_reading(chart, topic, question, lang)

    return {
        "ok": True,
        "source": source,
        "name": name,
        "topic": topic,
        "lang": lang,
        "chart": public_chart(chart, lang),
        "reading": text,
        "premium": premium,
    }


def make_reading(body: dict[str, Any]) -> dict[str, Any]:
    """Generate a reading without touching credits (used by tests and tools)."""
    return generate_reading(parse_reading_request(body))


LOCKED_PREMIUM = {
    "forecast": "✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦",
    "gift": "✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦",
    "shadow": "✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦",
    "compatibility": "✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦ ✦",
    "numbers": ["✦", "✦", "✦", "✦", "✦"],
    "colors": [],
    "day": "✦ ✦ ✦",
}


def paid_reading(body: dict[str, Any], visitor_id: Any) -> dict[str, Any]:
    """Validate, reserve one credit (or the one free preview) atomically,
    generate, and only keep the charge when the AI wrote the reading."""
    if not billing.valid_visitor_id(visitor_id):
        raise ValueError("Missing visitor id. Please reload the page.")
    params = parse_reading_request(body)
    kind = SERVICE.reserve_reading(visitor_id)  # raises PaymentError(402) at 0
    try:
        result = generate_reading(params)
    except BaseException:
        SERVICE.release_reading(visitor_id, kind)
        raise
    charged = result["source"] == "llm"
    if not charged:
        # Template fallback (AI unavailable): this question is on the house.
        SERVICE.release_reading(visitor_id, kind)
    result["charge"] = {"kind": kind, "charged": charged}
    result["premiumUnlocked"] = kind == "paid"
    if kind != "paid":
        result["premium"] = dict(LOCKED_PREMIUM)
    result["balance"] = SERVICE.balance(visitor_id)
    return result


ORDER_PATH = re.compile(r"^/api/admin/orders/([A-Za-z0-9]{4,12})/(approve|reject)$")


def packages_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "currency": "THB",
        "basePrice": billing.BASE_PRICE,
        "maxAmount": billing.MAX_AMOUNT,
        "packages": billing.PACKAGES,
        "paymentEnabled": billing.promptpay_id_from_env() is not None,
        "line": "ivymoonask",
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _route(self) -> str:
        return self.path.split("?")[0].rstrip("/") or "/"

    def _visitor(self) -> str | None:
        vid = (self.headers.get("X-Visitor-Id") or "").strip()
        return vid if billing.valid_visitor_id(vid) else None

    def _admin_check(self) -> bool:
        ok = billing.admin_token_ok(self.headers.get("X-Admin-Token"))
        if ok is None:
            self._send(503, {"ok": False, "error": "ADMIN_TOKEN is not set on the server.", "code": "admin_disabled"})
            return False
        if not ok:
            self._send(401, {"ok": False, "error": "Unauthorized.", "code": "unauthorized"})
            return False
        return True

    def _json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length > 16_000:
            raise billing.PaymentError("Request too large.", 413, "too_large")
        raw = self.rfile.read(length) if length else b"{}"
        body = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(body, dict):
            raise ValueError("Invalid JSON body.")
        return body

    def _serve_admin_page(self) -> None:
        page = (STATIC / "admin.html").read_bytes()
        ok = billing.admin_token_ok(self.headers.get("X-Admin-Token"))
        # Browsers cannot send the header on navigation, so the login form is
        # served with 401; the page then calls the admin API with the header.
        self.send_response(200 if ok else 401)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.end_headers()
        self.wfile.write(page)

    def _handle(self, fn) -> None:
        try:
            fn()
        except billing.PaymentError as exc:
            self._send(exc.status, {"ok": False, "error": str(exc), "code": exc.code})
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(400, {"ok": False, "error": str(exc)})
        except Exception:
            traceback.print_exc()
            self._send(500, {"ok": False, "error": "The stars flickered. Please try again."})

    def do_GET(self) -> None:
        route = self._route()
        if route == "/admin":
            self._serve_admin_page()
            return
        if route == "/admin.html":
            self._send(404, {"ok": False, "error": "Not found."})
            return
        if route == "/api/packages":
            self._send(200, packages_payload())
            return
        if route == "/api/health":
            self._send(200, {"ok": True, "store": STORE_KIND, "databaseConfigured": bool(os.environ.get("DATABASE_URL")),
                             "storeError": STORE_PROBLEM is not None})
            return
        if route == "/api/balance":
            def run() -> None:
                vid = self._visitor()
                if not vid:
                    raise ValueError("Missing visitor id.")
                self._send(200, {"ok": True, **SERVICE.balance(vid)})
            self._handle(run)
            return
        if route == "/api/orders":
            def run() -> None:
                vid = self._visitor()
                if not vid:
                    raise ValueError("Missing visitor id.")
                orders = [billing.public_order(o) for o in SERVICE.visitor_orders(vid)]
                self._send(200, {"ok": True, "orders": orders, **SERVICE.balance(vid)})
            self._handle(run)
            return
        if route == "/api/admin/orders":
            def run() -> None:
                if not self._admin_check():
                    return
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                status = None
                for part in query.split("&"):
                    if part.startswith("status="):
                        status = part.split("=", 1)[1] or None
                if status not in (None, "pending", "approved", "rejected"):
                    raise ValueError("Unknown status.")
                self._send(200, {"ok": True, "orders": SERVICE.list_orders(status)})
            self._handle(run)
            return
        if route.startswith("/api/"):
            self._send(404, {"ok": False, "error": "Not found."})
            return
        super().do_GET()

    def do_POST(self) -> None:
        route = self._route()
        if route == "/api/reading":
            def run() -> None:
                body = self._json_body()
                vid = self._visitor() or body.get("visitorId")
                self._send(200, paid_reading(body, vid))
            self._handle(run)
            return
        if route == "/api/orders":
            def run() -> None:
                body = self._json_body()
                vid = self._visitor()
                if not vid:
                    raise ValueError("Missing visitor id.")
                pkg = billing.package_for_amount(body.get("amount"))
                pp_id = billing.promptpay_id_from_env()
                if pp_id is None:
                    raise billing.PaymentError("Payment is coming soon.", 503, "payment_disabled")
                order = SERVICE.create_order(vid, pkg["price"])
                self._send(200, {
                    "ok": True,
                    "order": billing.public_order(order),
                    "promptpay": {"payload": billing.promptpay_payload(pp_id, order["price"])},
                    "line": "ivymoonask",
                })
            self._handle(run)
            return
        match = ORDER_PATH.match(route)
        if match:
            def run() -> None:
                if not self._admin_check():
                    return
                code, action = match.group(1), match.group(2)
                result = SERVICE.approve(code) if action == "approve" else SERVICE.reject(code)
                self._send(200, {"ok": True, **result})
            self._handle(run)
            return
        self._send(404, {"ok": False, "error": "Not found."})


def main() -> None:
    STATIC.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    has_key = bool(os.environ.get("OPENAI_API_KEY"))
    mode = "LLM (OPENAI_API_KEY is set)" if has_key else "template fallback (no OPENAI_API_KEY)"
    pay = "PromptPay on" if billing.promptpay_id_from_env() else "PromptPay off (set PROMPTPAY_ID)"
    admin = "admin on" if os.environ.get("ADMIN_TOKEN") else "admin off (set ADMIN_TOKEN)"
    print(f"ถามจันทร์ / Ask the Moon is listening on http://{HOST}:{PORT}  —  readings: {mode}; {pay}; {admin}", flush=True)
    if STORE_KIND == "postgres":
        tls = "off" if SERVICE.cfg["sslmode"] == "disable" else "on"
        print(f"Credit store: Postgres (DATABASE_URL, TLS {tls}, tables ready)", flush=True)
        for note in billing.NORMALIZE_NOTES[:1]:
            print(f"Credit store note: {note} Please clean up the DATABASE_URL value on Render.", flush=True)
    elif STORE_PROBLEM:
        print(f"Credit store: JSON fallback because Postgres failed: {STORE_PROBLEM}", flush=True)
    else:
        print("Credit store: JSON file in DATA_DIR (no DATABASE_URL; resets on redeploy)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nBye.")
        httpd.server_close()


if __name__ == "__main__":
    main()
