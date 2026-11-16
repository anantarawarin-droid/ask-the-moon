# ถามจันทร์ — Ask the Moon

A bilingual (Thai / English) destiny-reading web app. Visitors enter a name, birth date, optional birth time, a topic, and an optional question. The site computes Western zodiac, Chinese zodiac (with element), and a numerology life path number, then writes a personalized reading.

Visitors get one free question, then buy question credits (PromptPay, approved by the owner on `/admin`). Each AI-written reading uses 1 credit and unlocks the deep reading. Ad banners point advertisers to LINE `ivymoonask`.

## วิธีเปิดใช้ / How to run

You only need Python 3.10+ (no packages to install).

```bash
cd destiny-site
python3 app.py
```

Then open [http://127.0.0.1:5050](http://127.0.0.1:5050) in a browser.

Optional environment variables:

| Variable | What it does |
| --- | --- |
| `PORT` | Server port (default `5050`) |
| `HOST` | Bind address (default `0.0.0.0`, required on Render) |
| `OPENAI_API_KEY` | If set, `/api/reading` asks an OpenAI-compatible model to write the prose |
| `OPENAI_BASE_URL` | Optional, default `https://api.openai.com/v1`. For Gemini use `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `OPENAI_MODEL` | Optional, default `gpt-4o-mini`. For Gemini a current Flash model such as `gemini-3.5-flash-lite` |
| `PROMPTPAY_ID` | Your PromptPay phone (10 digits) or national ID (13 digits). Unset = "payment coming soon" |
| `ADMIN_TOKEN` | Long random password for `/admin`. Unset = admin disabled |
| `DATA_DIR` | Where balances and orders are stored (default `./data`) |

## Pricing and credits

The package table lives once in `credits.py` (`PACKAGE_TABLE`) and the page reads it from `GET /api/packages`:

| THB | Questions | Bonus | Avg / question |
| --- | --- | --- | --- |
| 15 | 1 | 0 | 15.00 |
| 30 | 2 | 0 | 15.00 |
| 45 | 3 | 0 | 15.00 |
| 60 | 4 | 0 | 15.00 |
| 75 | 5 | 0 | 15.00 |
| 90 | 7 | 1 | 12.86 |
| 105 | 8 | 1 | 13.13 |
| 120 | 10 | 2 | 12.00 |
| 135 | 12 | 3 | 11.25 |
| 150 | 15 | 5 | 10.00 (BEST VALUE) |

Flow: the browser keeps an anonymous visitor id in localStorage → `POST /api/orders {amount}` creates a pending order with a short code and a PromptPay QR for that exact amount → the visitor sends the slip and code on LINE `ivymoonask` → the owner approves on `/admin` → the package's questions (bonus included) are added once. `POST /api/reading` takes 1 credit atomically and keeps it only when the AI wrote the reading (a template fallback is free). New visitors get one free preview reading without the deep section. At 0 credits the API answers 402.

Storage is a JSON file (`DATA_DIR/credits.json`) with a lock and atomic writes. On Render's free plan there is no persistent disk, so balances and orders reset on every deploy or restart. Add a Render disk and point `DATA_DIR` at it, or swap `JsonStore` for a database, before taking real money at scale.

Tests: `python3 -m unittest discover -s tests -v`

If no API key is set, or the model request fails or times out (about 20 seconds), the site uses a built-in template generator that still weaves in the person's signs and numbers. Do not invent or paste a key you do not have, and never commit one to the repo.

## API

`POST /api/reading`

```json
{
  "name": "Nam Phet",
  "birthDate": "2006-07-07",
  "birthTime": "14:30",
  "topic": "life_path",
  "question": "What is my path this year?",
  "lang": "th"
}
```

`topic` may be `love`, `career`, `money`, or `life_path`. `lang` may be `th` or `en`. `birthTime` and `question` are optional.

## โครงสร้างไฟล์ / Files

```
destiny-site/
  app.py              # web server, chart math, template + optional LLM readings
  credits.py          # packages, PromptPay payloads, orders, balances, storage
  tests/              # unit + HTTP tests
  static/admin.html   # owner page at /admin
  static/vendor/qrcode.js  # QR renderer (MIT, Kazuhiko Arase)
  static/index.html
  static/styles.css
  static/app.js
  README.md
```

## หมายเหตุ

Readings are for inspiration only, not medical, legal, or financial advice, and not a guaranteed prediction.

## Deploy notes

The app reads `PORT` from the environment (default `5050`) and binds to `0.0.0.0` so it can run on a host like Render. Do not commit API keys. To let an LLM write the readings, set `OPENAI_API_KEY` in the host's environment, not in the repo.
