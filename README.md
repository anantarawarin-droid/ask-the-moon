# ถามจันทร์ — Ask the Moon

A bilingual (Thai / English) tarot web app. Visitors enter a name, a topic, and a question. The server draws three Rider-Waite-Smith cards and the AI gives a direct answer based only on those cards: a clear answer first, then how the cards support it, then 1–2 concrete pieces of advice. The visitor's birth date (and optional time) feeds a separate **profile panel** — ปีนักษัตร, the birth-date (life path) number with its meaning, and the Western sign — computed in `birthprofile.py`. Birth data is never sent to the AI; the tarot answer stays cards-only.

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
| `SLIPOK_BRANCH_ID`, `SLIPOK_API_KEY` | SlipOK branch + API key for automatic slip checks. Unset = no upload box (QR + LINE flow only) |
| `DATABASE_URL` | Postgres URL (e.g. Neon). When set, balances and orders live in Postgres and survive redeploys. TLS is required by default |
| `DATA_DIR` | JSON fallback location when there is no `DATABASE_URL` (default `./data`) |

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

Storage: with `DATABASE_URL` set, `PostgresCreditService` (in `credits.py`) creates its tables (`moon_visitors`, `moon_orders`) on startup and uses `UPDATE ... WHERE credits > 0 RETURNING` for the 1-credit deduction and `SELECT ... FOR UPDATE` for one-time approval. The driver is pure-Python `pg8000` (`requirements.txt`); a copy is also shipped in `vendor/` so the app runs even when the host's build step does not install requirements. Without `DATABASE_URL` (or if the connection fails, which is logged without the URL) it falls back to a JSON file in `DATA_DIR`, which resets on Render redeploys. `GET /api/health` shows which store is in use.

Tests: `python3 -m unittest discover -s tests -v` (add `TEST_DATABASE_URL=postgresql://user:pw@127.0.0.1:5432/testdb?sslmode=disable` to also run the Postgres tests; they truncate the `moon_*` tables).

If no API key is set, or the model request fails or times out (about 20 seconds), the site uses a built-in template generator that still weaves in the person's signs and numbers. Do not invent or paste a key you do not have, and never commit one to the repo.

## Slip upload (SlipOK)

When both SlipOK variables are set, the payment window shows an upload box under the QR.
The browser sends the raw image (JPG/PNG/WEBP, ≤ 4 MB; type is checked by magic bytes) to
`POST /api/orders/<code>/slip` with the `X-Visitor-Id` header. The server forwards it to
SlipOK (`amount` = order price, `log=true`, 20 s timeout, one retry on timeout/network/5xx).

* **Verified** → the order is approved immediately (credits added once), `transRef` is saved.
  A `transRef` can only belong to one order (unique index in Postgres).
* **Clear failure** (1012 repeated, 1013 wrong amount, 1014 wrong receiver, 1005–1008 not a slip,
  or the slip's amount ≠ order) → friendly Thai/English message, order stays pending.
* **Uncertain** (timeout, quota/setup 1000–1004, bank 1009/1010/1011, anything else) → order
  stays pending with slip status `review`; `/admin` shows the note and slip summary.
* Images are never stored; only a small summary (ref, amount, date, names, banks).
* Limits: 5 uploads per order, 8 per visitor per 10 minutes.

## Tarot (ให้ไพ่เล่าเรื่องราว)

Every reading (free or paid) draws 3 distinct cards from the full 78-card deck with
`secrets.SystemRandom`, each upright or reversed. There are no positions: the AI is asked to read
the three together as one story that answers the question, and the template fallback does the same.
The draw is returned as `tarot.cards` (id, Thai/English name, reversed, meaning, image).
Meanings (Thai + English, upright + reversed) live in `tarot.py`.

**Card art credit:** Rider-Waite-Smith tarot deck (1909), illustrated by Pamela Colman Smith,
public domain, from Wikimedia Commons. Each file's Commons page and license ("Public domain")
are listed in `static/tarot/SOURCES.json`. Images are 300 px wide WebP files (~45 KB each).

## API

`POST /api/reading`

```json
{
  "name": "Nam Phet",
  "birthDate": "2006-07-07",
  "birthTime": "14:30",
  "topic": "career",
  "question": "งานใหม่ที่สมัครไว้จะได้ไหม",
  "lang": "th"
}
```

`topic` may be `love`, `career`, `money`, or `life_path`. `lang` may be `th` or `en`. `question` is optional
(without one, the cards answer about the topic). `birthDate`/`birthTime` are optional for the API (the page asks for
the date); when given, the response has a `profile` object and the date is saved on the account to prefill next time.
**Asking requires login** (`401 login_required`), including the free question.

## Accounts

Username + password (3–20 letters/numbers/_, case-insensitive unique; password ≥ 8). No email.

* Passwords: PBKDF2-HMAC-SHA256, 240,000 iterations, 16-byte per-user salt, `hmac.compare_digest`.
* Sessions: random token in the `moon_session` cookie (HttpOnly, Secure, SameSite=Lax, 90 days);
  only its SHA-256 is stored (`moon_sessions`). Logout deletes it.
* Sign-up/login merges the device's anonymous balance, free-question use, and pending orders into the
  account once (idempotent). The account's credits live in a wallet row whose id never reaches the browser.
* Asking and buying require an account (`401 login_required`). Every account gets **one** free question
  (new accounts start with it; existing accounts keep their state). Anonymous ids get none, and their old free-question
  flag is not merged; their paid credits and pending orders still move into the account on login.
* Rate limits (in memory): login 20 per IP and 10 per username per 10 minutes; sign-up 5 per IP per hour.
* Forgotten password: `/admin` → “รีเซ็ตรหัสผ่าน” sets a temporary password to send on LINE
  (all of that user's sessions end). Users can change their password in the account menu.

API: `POST /api/auth/signup`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`,
`POST /api/auth/password`, admin `POST /api/admin/reset-password {"username"}`.

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

## Contact channels (password resets, payment help)

The login modal's “ลืมรหัสผ่าน?” section lists the admin's contact channels from env vars; only the ones set are shown.
`CONTACT_LINE` defaults to `ivymoonask` (set it to an empty value to hide LINE). Optional: `CONTACT_TIKTOK`,
`CONTACT_IG`, `CONTACT_FACEBOOK`, `CONTACT_EMAIL` (handles without `@` are fine; badly formatted values are ignored).
They are also returned by `GET /api/contacts` and in `/api/packages`.

## Google Sign-In (Google-only accounts)

Set `GOOGLE_CLIENT_ID` on Render (a Web OAuth client ID from Google Cloud; no client secret is used) and the site
switches to **Google-only**: the login modal shows only “Sign in with Google”, username/password sign-up, login,
change-password and admin password reset are turned off (`403 google_only`). Without the variable, the
username/password system keeps working.

* The browser gets an ID token from Google Identity Services and POSTs it to `/api/auth/google`.
* `google_auth.py` verifies it with the standard library: Google's JWKS (cached per Cache-Control), RS256
  (RSASSA-PKCS1-v1_5/SHA-256 via `pow()`), `aud == GOOGLE_CLIENT_ID`, Google issuer, `exp`/`iat`, `email_verified`.
* Accounts are keyed by the Google `sub` (stored as `username_key = "google:<sub>"`), with the email saved for display.
  First login merges the device's anonymous paid credits and pending orders; each Google account gets 1 free question.
* Admin: `/admin` lists accounts by email (`GET /api/admin/users`); orders show the customer's email.

Authorized JavaScript origins for the OAuth client: `https://foolmoon.lol`, `https://www.foolmoon.lol`,
`https://ask-the-moon.onrender.com` (no redirect URIs needed for the popup/ID-token flow).
