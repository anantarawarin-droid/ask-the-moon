import puppeteer from "puppeteer-core";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const out = path.join(root, "screenshot.png");
const url = process.env.DUANG_URL || "http://127.0.0.1:5050/";

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || "/usr/bin/google-chrome",
  headless: "new",
  args: [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--font-render-hinting=none",
    "--hide-scrollbars",
  ],
  defaultViewport: { width: 1440, height: 1100, deviceScaleFactor: 2 },
});

const page = await browser.newPage();
await page.goto(url, { waitUntil: "networkidle2", timeout: 60000 });
await page.evaluate(() => document.fonts.ready);
await page.waitForSelector("#reading-form");

await page.click("#lang-th");
await page.$eval("#name", (el) => { el.value = ""; });
await page.type("#name", "น้ำเพชร");
await page.$eval("#birthDate", (el) => {
  el.value = "2006-07-07";
  el.dispatchEvent(new Event("input", { bubbles: true }));
  el.dispatchEvent(new Event("change", { bubbles: true }));
});
await page.$eval("#birthTime", (el) => {
  el.value = "14:30";
  el.dispatchEvent(new Event("input", { bubbles: true }));
  el.dispatchEvent(new Event("change", { bubbles: true }));
});
await page.click('input[name="topic"][value="life_path"]');
await page.$eval("#question", (el) => { el.value = ""; });
await page.type("#question", "ปีนี้ฉันควรกล้าเริ่มสิ่งใหม่ไหม?");

await Promise.all([
  page.waitForSelector("#result:not([hidden])", { timeout: 15000 }),
  page.click("#submit-btn"),
]);

await page.waitForFunction(
  () => document.querySelector("#reading-body")?.textContent?.trim().length > 40,
  { timeout: 15000 },
);

// Let the reading scroll into view and the starfield paint a few frames.
await page.evaluate(() => document.querySelector("#result").scrollIntoView({ block: "start" }));
await new Promise((r) => setTimeout(r, 800));
// Full-page shot from the top so the hero, form, reading, and locked premium are all visible.
await page.evaluate(() => window.scrollTo(0, 0));
await new Promise((r) => setTimeout(r, 400));
await page.screenshot({ path: out, fullPage: true, type: "png" });
console.log("wrote", out);
await browser.close();
