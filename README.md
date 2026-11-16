# ถามจันทร์ — Ask the Moon

A bilingual (Thai / English) destiny-reading web app. Visitors enter a name, birth date, optional birth time, a topic, and an optional question. The site computes Western zodiac, Chinese zodiac (with element), and a numerology life path number, then writes a personalized reading.

This is a working prototype: the free reading is real, the Premium deep reading is shown locked beside it, and there are placeholder ad banners so you can see how the site could earn money.

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
| `OPENAI_BASE_URL` | Optional, default `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Optional, default `gpt-4o-mini` |

If no API key is set, the site uses a built-in template generator that still weaves in the person's signs and numbers, so the demo works immediately. Do not invent or paste a key you do not have.

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
  static/index.html
  static/styles.css
  static/app.js
  screenshot.png      # sample of a completed reading
  README.md
```

## หมายเหตุ

Readings are for inspiration only, not medical, legal, or financial advice, and not a guaranteed prediction.

## Deploy notes

The app reads `PORT` from the environment (default `5050`) and binds to `0.0.0.0` so it can run on a host like Render. Do not commit API keys. To let an LLM write the readings, set `OPENAI_API_KEY` in the host's environment, not in the repo.
