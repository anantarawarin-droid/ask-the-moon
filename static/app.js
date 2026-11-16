const I18N = {
  th: {
    docTitle: "ถามจันทร์",
    brand: "ถามจันทร์",
    brandSub: "Ask the Moon",
    footBrand: "ถามจันทร์",
    eyebrow: "อ่านดวง · ราศี · นักษัตร · เลขศาสตร์",
    heroTitle: "ถามจันทร์",
    heroLede: "บอกชื่อและวันเกิด แล้วรับบทอ่านดวงที่ถักจากราศีตะวันตก ปีนักษัตรจีน และเลขเส้นทางชีวิต — เลือกหัวข้อที่อยากรู้ ดาวจะตอบเป็นคำของคุณเอง",
    adHeading: "พื้นที่แห่งโอกาสสำหรับแบรนด์ของคุณ",
    adLine1: "ร่วมเป็นส่วนหนึ่งของจักรวาลแห่งการพยากรณ์",
    adLine2: "เปิดรับโฆษณา ประชาสัมพันธ์สินค้าและบริการ สำหรับผู้ที่สนใจร่วมลงพื้นที่โฆษณาบนเว็บไซต์",
    adContact: "ติดต่อสอบถามรายละเอียดเพิ่มเติมได้ที่นี่ · LINE: ivymoonask",
    formTitle: "เปิดดวงของคุณ",
    nameLabel: "ชื่อ",
    namePh: "เช่น น้ำเพชร",
    dateLabel: "วันเกิด",
    timeLabel: "เวลาเกิด",
    optional: "(ไม่บังคับ)",
    topicLabel: "หัวข้อที่อยากรู้",
    topicLove: "ความรัก",
    topicCareer: "การงาน",
    topicMoney: "การเงิน",
    topicPath: "เส้นทางชีวิต",
    qLabel: "คำถามถึงดาว",
    qPh: "เช่น ปีนี้ฉันควรกล้าเริ่มสิ่งใหม่ไหม?",
    submit: "เปิดบทอ่านดวง",
    loading: "กำลังจัดเรียงดวงดาว...",
    freeTag: "บทอ่านฟรี",
    freeTitle: "ดวงที่เปิดให้คุณ",
    premTag: "พรีเมียม",
    premTitle: "บทอ่านลึก",
    lockTitle: "ปลดล็อกบทอ่านลึก",
    lockCopy: "เลขนำโชค สีดวง วันมงคล ความเข้ากันได้ ของขวัญซ่อนเร้น และพยากรณ์ 12 เดือน",
    upgrade: "เติมคำถามเพื่อปลดล็อก",
    lockNote: "บทอ่านลึกเปิดให้อัตโนมัติทุกครั้งที่ใช้เครดิตคำถาม",
    unlockedTag: "ปลดล็อกแล้ว",
    paidTag: "บทอ่านของคุณ",
    balanceShort: "คำถาม",
    balanceTitle: (n) => `คุณมี ${n} คำถาม`,
    creditFree: "คำถามแรกฟรี! ลองถามจันทร์ได้เลย (ไม่หักเครดิต)",
    creditHave: (n) => `คุณเหลือ <b>${n}</b> คำถาม · ถาม 1 ครั้งใช้ 1 คำถาม และปลดล็อกบทอ่านลึก`,
    creditNone: "คำถามของคุณหมดแล้ว เติมแพ็กเกจเพื่อถามต่อ",
    topUp: "เติมคำถาม",
    noCredits: "คำถามของคุณหมดแล้ว — เลือกแพ็กเกจด้านล่างเพื่อถามต่อนะคะ",
    notCharged: "ดวงจันทร์ใช้บทอ่านสำรองครั้งนี้ จึงไม่หักเครดิต",
    chargedPaid: "ใช้ 1 คำถาม · บทอ่านลึกปลดล็อกแล้ว",
    chargedFree: "ใช้คำถามฟรีแล้ว · เติมคำถามเพื่อปลดล็อกบทอ่านลึก",
    pricingEyebrow: "แพ็กเกจคำถาม · เติมผ่านพร้อมเพย์",
    pricingTitle: "เติมพลังจันทร์ ถามได้มากขึ้น",
    pricingLede: "คำถามละ 15 บาท ยิ่งเติมมาก ยิ่งได้คำถามโบนัสฟรี — สูงสุด 150 บาทต่อครั้ง ทุกคำถามที่ใช้เครดิตจะได้บทอ่านลึกครบทุกส่วน",
    how1: "เลือกแพ็กเกจ แล้วสแกน QR พร้อมเพย์ด้วยแอปธนาคาร",
    how2: "ส่งสลิปพร้อมรหัสคำสั่งซื้อทาง LINE: ivymoonask",
    how3: "เมื่อตรวจสอบแล้ว คำถามจะเข้าบัญชีของคุณทันที",
    baht: "บาท",
    questionsUnit: () => "คำถาม",
    bonusFree: (n) => `+ โบนัสฟรี ${n} คำถาม`,
    noBonus: "ไม่มีโบนัส",
    perQ: (v) => `เฉลี่ย ฿${v} / คำถาม`,
    worth: (w) => `มูลค่า ฿${w}`,
    worthPay: (w, pr) => `มูลค่า <s>฿${w}</s> จ่ายเพียง <b>฿${pr}</b>`,
    split: (b, x) => `${b} คำถาม + ${x} ฟรี`,
    save: (pct) => `ประหยัด ${pct}%`,
    buy: "เลือกแพ็กเกจนี้",
    buyBest: "รับดีลที่คุ้มที่สุด",
    bestBadge: "BEST VALUE · คุ้มที่สุด",
    bestPay: "จ่าย 150 บาท",
    bestGet: "รับ 15 คำถาม",
    bestBonus: "ฟรีโบนัส 5 คำถาม",
    bestPer: "เพียงคำถามละ 10 บาท",
    payTitle: "ชำระผ่านพร้อมเพย์",
    payOrder: "รหัสคำสั่งซื้อ",
    payAmount: "ยอดชำระ",
    payGet: (q, b) => b ? `รับ ${q} คำถาม (รวมโบนัส ${b})` : `รับ ${q} คำถาม`,
    payStep1: (a) => `สแกน QR นี้ด้วยแอปธนาคาร แล้วโอน <b>฿${a}</b> ให้ตรงยอด`,
    payStep2: (c) => `ส่งสลิปพร้อมรหัส <b>${c}</b> ทาง LINE: ivymoonask`,
    payStep3: "เมื่อแอดมินตรวจสอบแล้ว คำถามจะเข้าบัญชีของคุณทันที (หน้านี้จะอัปเดตเอง)",
    payLine: "ส่งสลิปทาง LINE",
    copyCode: "คัดลอกรหัส",
    copied: "คัดลอกแล้ว",
    payWaiting: "รอการตรวจสอบสลิป…",
    payApproved: (q) => `เติมสำเร็จ! ได้รับ ${q} คำถามแล้ว ✨`,
    balanceNow: (n) => `ยอดคงเหลือ ${n} คำถาม`,
    payRejected: "คำสั่งซื้อนี้ถูกปฏิเสธ หากโอนแล้ว ติดต่อ LINE: ivymoonask",
    paySoonTitle: "ระบบชำระเงินกำลังจะเปิด",
    paySoonBody: "ดวงจันทร์กำลังเตรียมช่องทางพร้อมเพย์ให้คุณ หากต้องการเติมตอนนี้ ทักมาได้ที่ LINE: ivymoonask",
    payError: "สร้างคำสั่งซื้อไม่สำเร็จ กรุณาลองใหม่",
    close: "ปิด",
    pendingNote: (c) => `มีคำสั่งซื้อ ${c} รอตรวจสอบ`,
    slipTitle: "อัปโหลดสลิป เติมคำถามอัตโนมัติ",
    slipHint: "รูป JPG, PNG หรือ WEBP ไม่เกิน 4MB · ระบบตรวจสลิปและเติมคำถามให้ทันที",
    slipChoose: "เลือกรูปสลิป",
    slipCheck: "ตรวจสลิป",
    slipChecking: "กำลังตรวจสลิป…",
    slipBadType: "กรุณาเลือกรูป JPG, PNG หรือ WEBP เท่านั้น",
    slipTooBig: "รูปใหญ่เกิน 4MB กรุณาลดขนาดหรือแคปหน้าจอใหม่",
    slipNoFile: "กรุณาเลือกรูปสลิปก่อน",
    slipErr: {
      rate_limited: "อัปโหลดถี่เกินไป กรุณารอสักครู่แล้วลองใหม่",
      too_many_slips: "อัปโหลดสลิปครบจำนวนครั้งแล้ว กรุณาส่งสลิปทาง LINE: ivymoonask",
      not_pending: "คำสั่งซื้อนี้ปิดแล้ว กรุณาสร้างคำสั่งซื้อใหม่",
      not_found: "ไม่พบคำสั่งซื้อนี้ กรุณาสร้างคำสั่งซื้อใหม่",
      bad_file_type: "ไฟล์นี้ไม่ใช่รูป JPG, PNG หรือ WEBP",
      file_too_large: "รูปใหญ่เกิน 4MB",
      network: "เชื่อมต่อไม่ได้ กรุณาลองใหม่ หรือส่งสลิปทาง LINE",
    },
    orLine: "หรือส่งสลิปทาง LINE แทนได้",
    payStep2Slip: (c) => `อัปโหลดสลิปด้านล่าง ระบบจะตรวจและเติมคำถามให้ทันที (หรือส่งทาง LINE พร้อมรหัส <b>${c}</b>)`,
    tarotCredit: "ภาพไพ่ทาโรต์: สำรับ Rider-Waite-Smith (ค.ศ. 1909) วาดโดย Pamela Colman Smith · สาธารณสมบัติ จาก Wikimedia Commons",
    tarotReversed: "กลับหัว",
    tarotTap: "แตะไพ่เพื่อดูความหมาย",
    disclaimer: "บทอ่านดวงนี้จัดให้เพื่อแรงบันดาลใจ ไม่ใช่คำแนะนำทางการแพทย์ กฎหมาย การเงิน หรือคำทำนายที่รับประกันผล ทางเลือกยังเป็นของคุณเสมอ",
    badgeZodiac: "ราศีตะวันตก",
    badgeChinese: "ปีนักษัตร",
    badgePath: "เลขเส้นทางชีวิต",
    badgeHour: "ยามเกิด",
    master: "เลขปรมาจารย์",
    sourceTemplate: "สร้างจากดวงและแบบบทอ่าน — เพิ่มคีย์ API เพื่อให้นิยายจากโมเดลภาษา",
    sourceLlm: "เรียบเรียงโดยปัญญาประดิษฐ์ จากดวงของคุณ",
    resultFor: (name, topic) => `บทอ่านสำหรับ ${name} · ${topic}`,
    needName: "กรุณาใส่ชื่อ",
    needDate: "กรุณาใส่วันเกิด",
    hours: { dawn: "รุ่งสาง", morning: "เช้า", afternoon: "บ่าย", evening: "เย็น", night: "ค่ำคืน" },
    topics: { love: "ความรัก", career: "การงาน", money: "การเงิน", life_path: "เส้นทางชีวิต" },
    luckNumbers: "เลขนำโชค",
    luckColors: "สีนำโชค",
    luckDay: "วันมงคล",
    gift: "ของขวัญซ่อนเร้น",
    shadow: "บททดสอบซ่อนเร้น",
    compat: "ความเข้ากันได้",
    forecast: "พยากรณ์ 12 เดือน",
  },
  en: {
    docTitle: "Ask the Moon",
    brand: "Ask the Moon",
    brandSub: "ถามจันทร์",
    footBrand: "Ask the Moon",
    eyebrow: "Readings · Zodiac · Lunar year · Numerology",
    heroTitle: "Ask the Moon",
    heroLede: "Share your name and birthday for a reading woven from Western zodiac, Chinese lunar year, and your numerology life path. Choose a topic, and the sky answers in your own words.",
    adHeading: "A space of opportunity for your brand",
    adLine1: "Become part of the universe of fortune-telling",
    adLine2: "Now accepting ads to promote your products and services",
    adContact: "Contact us here for more details · LINE: ivymoonask",
    formTitle: "Open your chart",
    nameLabel: "Name",
    namePh: "e.g. Nam Phet",
    dateLabel: "Birth date",
    timeLabel: "Birth time",
    optional: "(optional)",
    topicLabel: "What would you like to know?",
    topicLove: "Love",
    topicCareer: "Career",
    topicMoney: "Money",
    topicPath: "Life path",
    qLabel: "A question for the stars",
    qPh: "e.g. Should I be brave enough to start something new this year?",
    submit: "Reveal my reading",
    loading: "The stars are aligning...",
    freeTag: "Free reading",
    freeTitle: "Your open chart",
    premTag: "Premium",
    premTitle: "Deep reading",
    lockTitle: "Unlock the deep reading",
    lockCopy: "Lucky numbers, colors, a fortunate day, compatibility, a hidden gift, and a 12-month forecast.",
    upgrade: "Top up to unlock",
    lockNote: "The deep reading unlocks automatically whenever you use a question credit.",
    unlockedTag: "Unlocked",
    paidTag: "Your reading",
    balanceShort: "questions",
    balanceTitle: (n) => `You have ${n} questions`,
    creditFree: "Your first question is free! Ask the moon now (no credit used).",
    creditHave: (n) => `You have <b>${n}</b> questions left · each question uses 1 and unlocks the deep reading.`,
    creditNone: "You're out of questions. Top up to keep asking.",
    topUp: "Top up",
    noCredits: "You're out of questions — pick a package below to keep asking.",
    notCharged: "The moon used a backup reading this time, so no credit was used.",
    chargedPaid: "1 question used · deep reading unlocked",
    chargedFree: "Free question used · top up to unlock the deep reading",
    pricingEyebrow: "Question packages · PromptPay",
    pricingTitle: "Charge the moon, ask more",
    pricingLede: "15 THB per question, with free bonus questions on bigger packs — up to 150 THB per top-up. Every credited question comes with the full deep reading.",
    how1: "Pick a package and scan the PromptPay QR with your banking app.",
    how2: "Send the slip with your order code on LINE: ivymoonask",
    how3: "Once it's checked, the questions land in your balance right away.",
    baht: "THB",
    questionsUnit: (n) => (n === 1 ? "question" : "questions"),
    bonusFree: (n) => `+ ${n} FREE bonus`,
    noBonus: "No bonus",
    perQ: (v) => `Avg ฿${v} / question`,
    worth: (w) => `Worth ฿${w}`,
    worthPay: (w, pr) => `Worth <s>฿${w}</s>, pay only <b>฿${pr}</b>`,
    split: (b, x) => `${b} questions + ${x} free`,
    save: (pct) => `Save ${pct}%`,
    buy: "Choose this pack",
    buyBest: "Get the best deal",
    bestBadge: "BEST VALUE",
    bestPay: "Pay 150 THB",
    bestGet: "Receive 15 questions",
    bestBonus: "Get 5 FREE bonus questions",
    bestPer: "Only 10 THB per question",
    payTitle: "Pay with PromptPay",
    payOrder: "Order code",
    payAmount: "Amount",
    payGet: (q, b) => b ? `${q} questions (incl. ${b} bonus)` : `${q} questions`,
    payStep1: (a) => `Scan this QR in your banking app and pay exactly <b>฿${a}</b>.`,
    payStep2: (c) => `Send the slip with code <b>${c}</b> on LINE: ivymoonask`,
    payStep3: "Once the admin checks it, the questions are added right away (this page updates itself).",
    payLine: "Send slip on LINE",
    copyCode: "Copy code",
    copied: "Copied",
    payWaiting: "Waiting for slip check…",
    payApproved: (q) => `Top-up done! ${q} questions added ✨`,
    balanceNow: (n) => `Balance: ${n} question${n === 1 ? "" : "s"}`,
    payRejected: "This order was declined. If you already paid, contact LINE: ivymoonask",
    paySoonTitle: "Payments are coming soon",
    paySoonBody: "The moon is preparing PromptPay for you. To top up now, message LINE: ivymoonask",
    payError: "Couldn't create the order. Please try again.",
    close: "Close",
    pendingNote: (c) => `Order ${c} is awaiting review`,
    slipTitle: "Upload your slip for instant top-up",
    slipHint: "JPG, PNG, or WEBP up to 4MB · we verify it and add your questions right away",
    slipChoose: "Choose slip image",
    slipCheck: "Verify slip",
    slipChecking: "Checking your slip…",
    slipBadType: "Please choose a JPG, PNG, or WEBP image.",
    slipTooBig: "The image is over 4MB. Please resize it or take a new screenshot.",
    slipNoFile: "Please choose your slip image first.",
    slipErr: {
      rate_limited: "Too many uploads. Please wait a moment and try again.",
      too_many_slips: "Upload limit reached for this order. Please send the slip on LINE: ivymoonask",
      not_pending: "This order is closed. Please create a new one.",
      not_found: "Order not found. Please create a new one.",
      bad_file_type: "That file isn't a JPG, PNG, or WEBP image.",
      file_too_large: "The image is over 4MB.",
      network: "Couldn't connect. Try again, or send the slip on LINE.",
    },
    orLine: "Or send your slip on LINE instead",
    payStep2Slip: (c) => `Upload your slip below and we'll verify it instantly (or send it on LINE with code <b>${c}</b>).`,
    tarotCredit: "Tarot art: Rider-Waite-Smith deck (1909) by Pamela Colman Smith · public domain, via Wikimedia Commons",
    tarotReversed: "Reversed",
    tarotTap: "Tap a card to see its meaning",
    disclaimer: "These readings are for inspiration, not medical, legal, or financial advice, and not a guaranteed prediction. Your choices remain your own.",
    badgeZodiac: "Western zodiac",
    badgeChinese: "Chinese zodiac",
    badgePath: "Life path number",
    badgeHour: "Hour of birth",
    master: "Master number",
    sourceTemplate: "Woven from your chart and written templates — add an API key to let a language model write the prose.",
    sourceLlm: "Composed by AI from your chart",
    resultFor: (name, topic) => `A reading for ${name} · ${topic}`,
    needName: "Please enter a name.",
    needDate: "Please enter a birth date.",
    hours: { dawn: "Dawn", morning: "Morning", afternoon: "Afternoon", evening: "Evening", night: "Night" },
    topics: { love: "Love", career: "Career", money: "Money", life_path: "Life path" },
    luckNumbers: "Lucky numbers",
    luckColors: "Lucky colors",
    luckDay: "Fortunate day",
    gift: "Hidden gift",
    shadow: "Hidden test",
    compat: "Compatibility",
    forecast: "12-month forecast",
  },
};

function visitorId() {
  let id = localStorage.getItem("moon-visitor");
  if (!id || !/^[A-Za-z0-9_-]{16,64}$/.test(id)) {
    const bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);
    id = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
    localStorage.setItem("moon-visitor", id);
  }
  return id;
}

const state = {
  lang: localStorage.getItem("duang-lang") || "th",
  last: null,
  visitor: visitorId(),
  balance: { credits: 0, freeAvailable: true },
  packages: [],
  paymentEnabled: false,
  slipEnabled: false,
  slipMaxBytes: 4 * 1024 * 1024,
  slipResult: null,
  slipBusy: false,
  slipFile: null,
  order: null,
  pollTimer: null,
};

function api(path, options = {}) {
  const headers = { "X-Visitor-Id": state.visitor, ...(options.headers || {}) };
  if (options.body) headers["Content-Type"] = "application/json";
  return fetch(path, { ...options, headers }).then(async (response) => {
    let data = {};
    try { data = await response.json(); } catch (_) { /* empty */ }
    return { response, data };
  });
}

function t() {
  return I18N[state.lang] || I18N.th;
}

function applyLang() {
  const dict = t();
  document.documentElement.lang = state.lang;
  document.body.dataset.lang = state.lang;
  document.title = dict.docTitle;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (typeof dict[key] === "string") el.textContent = dict[key];
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (typeof dict[key] === "string") el.setAttribute("placeholder", dict[key]);
  });
  document.getElementById("lang-th").classList.toggle("is-on", state.lang === "th");
  document.getElementById("lang-en").classList.toggle("is-on", state.lang === "en");
  renderBalance();
  renderPricing();
  if (state.order) renderPayModal();
  if (state.last) renderResult(state.last);
}

function setLang(lang) {
  state.lang = lang === "en" ? "en" : "th";
  localStorage.setItem("duang-lang", state.lang);
  applyLang();
}

function paintStars() {
  const canvas = document.getElementById("stars");
  const ctx = canvas.getContext("2d");
  const stars = [];
  function resize() {
    canvas.width = window.innerWidth * devicePixelRatio;
    canvas.height = window.innerHeight * devicePixelRatio;
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    stars.length = 0;
    const count = Math.min(220, Math.floor((window.innerWidth * window.innerHeight) / 9000));
    for (let i = 0; i < count; i += 1) {
      stars.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        r: Math.random() * 1.3 + 0.2,
        a: Math.random(),
        s: Math.random() * 0.015 + 0.004,
        gold: Math.random() > 0.86,
      });
    }
  }
  function tick() {
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    for (const star of stars) {
      star.a += star.s;
      const alpha = 0.25 + Math.abs(Math.sin(star.a)) * 0.75;
      ctx.beginPath();
      ctx.fillStyle = star.gold
        ? `rgba(243, 226, 168, ${alpha})`
        : `rgba(255, 255, 255, ${alpha})`;
      ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(tick);
  }
  resize();
  window.addEventListener("resize", resize);
  tick();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function badge(label, value, hint) {
  const hintHtml = hint ? `<div style="color:#f3e2a8;font-size:0.72rem;margin-top:0.15rem">${escapeHtml(hint)}</div>` : "";
  return `<li class="badge"><small>${escapeHtml(label)}</small><b>${escapeHtml(value)}</b>${hintHtml}</li>`;
}

let tarotRevealed = "";

function renderTarot(tarot) {
  const box = document.getElementById("tarot");
  const row = document.getElementById("tarot-row");
  const cards = (tarot && tarot.cards) || [];
  if (!cards.length) {
    box.hidden = true;
    row.innerHTML = "";
    return;
  }
  const th = state.lang === "th";
  const dict = t();
  const key = cards.map((c) => c.id + (c.reversed ? "r" : "u")).join(",");
  const already = key === tarotRevealed; // language switch: keep cards face up, no replay
  document.getElementById("tarot-title").textContent = th ? tarot.headingTh : tarot.headingEn;
  row.innerHTML = cards
    .map((c, i) => {
      const name = th ? c.nameTh.replace(/\s*\(.*\)$/, "") : c.nameEn;
      const sub = th ? c.nameEn : c.nameTh.replace(/\s*\(.*\)$/, "");
      const meaning = th ? c.meaningTh : c.meaningEn;
      return `
      <figure class="tcard${c.reversed ? " is-reversed" : ""}${already ? " is-flipped no-anim" : ""}" style="--i:${i}">
        <button type="button" class="tcard-inner" aria-label="${escapeHtml(name)}" title="${escapeHtml(meaning)}">
          <span class="tcard-face tcard-back" aria-hidden="true"><span class="tcard-moon">☾</span></span>
          <span class="tcard-face tcard-front"><img src="${escapeHtml(c.image)}" alt="${escapeHtml(c.nameEn)}" decoding="async" /></span>
        </button>
        <figcaption>
          <b class="tcard-name">${escapeHtml(th ? c.nameTh.replace(/\s*\(.*\)$/, "") : c.nameEn)}</b>
          <small class="tcard-sub">${escapeHtml(sub)}</small>
          ${c.reversed ? `<span class="tcard-rev">${escapeHtml(dict.tarotReversed)}</span>` : ""}
          <span class="tcard-meaning">${escapeHtml(meaning)}</span>
        </figcaption>
      </figure>`;
    })
    .join("");
  box.hidden = false;
  if (already) return;
  // Preload the art, then flip each card in turn.
  const figs = [...row.querySelectorAll(".tcard")];
  const loads = [...row.querySelectorAll("img")].map(
    (img) => new Promise((resolve) => { if (img.complete) resolve(); else { img.onload = resolve; img.onerror = resolve; } }),
  );
  const start = () => figs.forEach((fig, i) => setTimeout(() => fig.classList.add("is-flipped"), 500 + i * 650));
  Promise.race([Promise.all(loads), new Promise((r) => setTimeout(r, 2500))]).then(start);
  tarotRevealed = key;
}

function renderResult(data) {
  const dict = t();
  const result = document.getElementById("result");
  const chart = data.chart;
  const topicLabel = dict.topics[data.topic] || data.topic;
  document.getElementById("result-for").textContent = dict.resultFor(data.name, topicLabel);

  const pathHint = chart.lifePath.master ? dict.master : "";
  const hour = chart.hour ? dict.hours[chart.hour] : "";
  const badges = [
    badge(dict.badgeZodiac, `${chart.westernZodiac.glyph} ${chart.westernZodiac.sign}`, chart.westernZodiac.dates),
    badge(dict.badgeChinese, chart.chineseZodiac.label, String(chart.chineseZodiac.lunarYear)),
    badge(dict.badgePath, `${chart.lifePath.number} · ${chart.lifePath.title}`, pathHint),
  ];
  if (hour) badges.push(badge(dict.badgeHour, hour));
  document.getElementById("badges").innerHTML = badges.join("");
  renderTarot(data.tarot);
  document.getElementById("reading-body").textContent = data.reading;
  const charge = data.charge || {};
  let note = data.source === "llm" ? dict.sourceLlm : dict.sourceTemplate;
  if (charge.kind && !charge.charged) note += " · " + dict.notCharged;
  else if (charge.kind === "paid") note += " · " + dict.chargedPaid;
  else if (charge.kind === "free") note += " · " + dict.chargedFree;
  document.getElementById("source-note").textContent = note;
  const premiumCard = document.querySelector(".reading-card.premium");
  premiumCard.classList.toggle("is-unlocked", Boolean(data.premiumUnlocked));
  premiumCard.querySelector(".gold-tag").textContent = data.premiumUnlocked ? dict.unlockedTag : dict.premTag;
  document.querySelector(".tag.free").textContent = data.premiumUnlocked ? dict.paidTag : dict.freeTag;

  const prem = data.premium || {};
  const colors = (prem.colors || [])
    .map((c) => {
      const name = state.lang === "th" ? c.th : c.en;
      return `<span class="swatch" title="${escapeHtml(name)}" style="background:${escapeHtml(c.hex)}"></span> ${escapeHtml(name)}`;
    })
    .join(" · ");
  document.getElementById("premium-body").innerHTML = `
    <h4>${escapeHtml(dict.luckNumbers)}</h4>
    <p>${escapeHtml((prem.numbers || []).join(" · "))}</p>
    <h4>${escapeHtml(dict.luckColors)}</h4>
    <p class="swatches">${colors}</p>
    <h4>${escapeHtml(dict.luckDay)}</h4>
    <p>${escapeHtml(prem.day || "")}</p>
    <h4>${escapeHtml(dict.gift)}</h4>
    <p>${escapeHtml(prem.gift || "")}</p>
    <h4>${escapeHtml(dict.shadow)}</h4>
    <p>${escapeHtml(prem.shadow || "")}</p>
    <h4>${escapeHtml(dict.compat)}</h4>
    <p>${escapeHtml(prem.compatibility || "")}</p>
    <h4>${escapeHtml(dict.forecast)}</h4>
    <p>${escapeHtml(prem.forecast || "")}</p>
  `;
  result.hidden = false;
}

async function onSubmit(event) {
  event.preventDefault();
  const dict = t();
  const error = document.getElementById("form-error");
  const status = document.getElementById("status");
  const result = document.getElementById("result");
  const button = document.getElementById("submit-btn");
  error.hidden = true;
  error.textContent = "";

  const name = document.getElementById("name").value.trim();
  const birthDate = document.getElementById("birthDate").value;
  const birthTime = document.getElementById("birthTime").value;
  const question = document.getElementById("question").value.trim();
  const topic = (document.querySelector('input[name="topic"]:checked') || {}).value || "life_path";

  if (!name) {
    error.textContent = dict.needName;
    error.hidden = false;
    return;
  }
  if (!birthDate) {
    error.textContent = dict.needDate;
    error.hidden = false;
    return;
  }

  if (!state.balance.freeAvailable && state.balance.credits <= 0) {
    showNoCredits();
    return;
  }

  button.disabled = true;
  status.hidden = false;
  result.hidden = true;

  try {
    const { response, data } = await api("/api/reading", {
      method: "POST",
      body: JSON.stringify({
        name,
        birthDate,
        birthTime,
        topic,
        question,
        lang: state.lang,
      }),
    });
    if (response.status === 402) {
      await refreshBalance();
      showNoCredits();
      return;
    }
    if (!response.ok || !data.ok) {
      throw new Error(data.error || "The stars flickered.");
    }
    if (data.balance) setBalance(data.balance);
    state.last = data;
    renderResult(data);
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    error.textContent = err.message || (state.lang === "th" ? "เกิดข้อผิดพลาด กรุณาลองใหม่" : "Something went wrong. Please try again.");
    error.hidden = false;
  } finally {
    button.disabled = false;
    status.hidden = true;
  }
}

function showNoCredits() {
  const error = document.getElementById("form-error");
  error.textContent = t().noCredits;
  error.hidden = false;
  document.getElementById("pricing").scrollIntoView({ behavior: "smooth", block: "start" });
  document.getElementById("pricing").classList.add("flash");
  setTimeout(() => document.getElementById("pricing").classList.remove("flash"), 1800);
}

function setBalance(balance) {
  const before = state.balance.credits;
  state.balance = { credits: Number(balance.credits) || 0, freeAvailable: Boolean(balance.freeAvailable) };
  renderBalance(before !== state.balance.credits);
}

function renderBalance(bump = false) {
  const dict = t();
  const { credits, freeAvailable } = state.balance;
  const chip = document.getElementById("balance-chip");
  document.getElementById("balance-num").textContent = String(credits);
  chip.title = dict.balanceTitle(credits);
  chip.classList.toggle("is-empty", credits <= 0);
  if (bump) {
    chip.classList.remove("bump");
    void chip.offsetWidth;
    chip.classList.add("bump");
  }
  const text = document.getElementById("credit-text");
  const strip = document.getElementById("credit-strip");
  strip.classList.toggle("is-empty", credits <= 0 && !freeAvailable);
  if (credits > 0) text.innerHTML = dict.creditHave(credits);
  else if (freeAvailable) text.textContent = dict.creditFree;
  else text.textContent = dict.creditNone;
}

async function refreshBalance() {
  try {
    const { response, data } = await api("/api/balance");
    if (response.ok && data.ok) setBalance(data);
  } catch (_) { /* offline: keep last known */ }
}

async function loadPackages() {
  try {
    const { response, data } = await api("/api/packages");
    if (response.ok && data.ok) {
      state.packages = data.packages;
      state.paymentEnabled = Boolean(data.paymentEnabled);
      state.slipEnabled = Boolean(data.slipEnabled);
      if (data.slipMaxBytes) state.slipMaxBytes = data.slipMaxBytes;
      renderPricing();
    }
  } catch (_) { /* leave the grid empty */ }
}

function tierOf(pkg) {
  if (pkg.bestValue) return "tier-best";
  if (pkg.bonus >= 2) return "tier-high";
  if (pkg.bonus >= 1) return "tier-bonus";
  return "tier-base";
}

function renderPricing() {
  const grid = document.getElementById("price-grid");
  if (!grid || !state.packages.length) return;
  const dict = t();
  grid.innerHTML = state.packages.map((pkg, i) => {
    const tier = tierOf(pkg);
    if (pkg.bestValue) {
      return `
      <article class="price-card ${tier}" style="--i:${i}">
        <div class="best-badge">${escapeHtml(dict.bestBadge)}</div>
        <div class="best-body">
          <div class="best-main">
            <p class="price"><span class="cur">฿</span>${pkg.price}</p>
            <p class="qty"><b>${pkg.questions}</b> ${escapeHtml(dict.questionsUnit(pkg.questions))}</p>
            <p class="bonus">${escapeHtml(dict.bonusFree(pkg.bonus))}</p>
          </div>
          <ul class="best-list">
            <li>✦ ${escapeHtml(dict.bestPay)}</li>
            <li>✦ ${escapeHtml(dict.bestGet)}</li>
            <li>✦ ${escapeHtml(dict.bestBonus)}</li>
            <li class="hi">✦ ${escapeHtml(dict.bestPer)}</li>
          </ul>
        </div>
        <p class="meta"><span class="per">${escapeHtml(dict.perQ(pkg.perQuestion))}</span>
          <span class="worth"><s>${escapeHtml(dict.worth(pkg.worth))}</s> · ${escapeHtml(dict.save(pkg.savingsPercent))}</span></p>
        <button type="button" class="btn gold buy" data-amount="${pkg.price}">${escapeHtml(dict.buyBest)}</button>
      </article>`;
    }
    const save = pkg.savingsPercent > 0
      ? `<span class="save-pill">${escapeHtml(dict.save(pkg.savingsPercent))}</span>` : "";
    return `
      <article class="price-card ${tier}${pkg.bonus ? " has-save" : ""}" style="--i:${i}">
        ${save}
        <p class="price"><span class="cur">฿</span>${pkg.price}</p>
        <p class="qty"><b>${pkg.questions}</b> ${escapeHtml(dict.questionsUnit(pkg.questions))}</p>
        <p class="bonus ${pkg.bonus ? "" : "none"}">${escapeHtml(pkg.bonus ? dict.bonusFree(pkg.bonus) : dict.noBonus)}</p>
        <p class="meta"><span class="per">${escapeHtml(dict.perQ(pkg.perQuestion))}</span>
          ${pkg.bonus ? `<span class="split">✦ ${escapeHtml(dict.split(pkg.baseQuestions, pkg.bonus))}</span>
          <span class="worth-line">${dict.worthPay(pkg.worth, pkg.price)}</span>` : ""}</p>
        <button type="button" class="btn ${pkg.bonus ? "gold" : "soft"} buy" data-amount="${pkg.price}">${escapeHtml(dict.buy)}</button>
      </article>`;
  }).join("");
}

function stopPolling() {
  if (state.pollTimer) clearInterval(state.pollTimer);
  state.pollTimer = null;
}

function openPayModal() {
  document.getElementById("pay-modal").hidden = false;
}

function closePayModal() {
  document.getElementById("pay-modal").hidden = true;
  state.slipResult = null;
  state.slipFile = null;
  stopPolling();
  state.order = null;
}

function qrSvg(payload) {
  if (typeof qrcode !== "function") return "";
  const qr = qrcode(0, "M");
  qr.addData(payload);
  qr.make();
  return qr.createSvgTag({ cellSize: 6, margin: 2, scalable: true });
}

function renderPayModal() {
  const dict = t();
  const box = document.getElementById("pay-content");
  const o = state.order;
  if (!o) return;
  if (o.soon) {
    box.innerHTML = `
      <div class="pay-soon">
        <div class="lock-icon" aria-hidden="true">☾</div>
        <h3 id="pay-title">${escapeHtml(dict.paySoonTitle)}</h3>
        <p>${escapeHtml(dict.paySoonBody)}</p>
        <a class="btn gold line-btn" href="https://line.me/ti/p/~ivymoonask" target="_blank" rel="noopener">LINE: ivymoonask</a>
      </div>`;
    return;
  }
  const order = o.order;
  let statusHtml = `<p class="pay-status waiting"><span class="pulse"></span>${escapeHtml(dict.payWaiting)}</p>`;
  if (order.status === "approved") {
    const r = state.slipResult;
    const head = r && r.kind === "success" ? (state.lang === "th" ? r.th : r.en) : dict.payApproved(order.questions);
    statusHtml = `<p class="pay-status ok">${escapeHtml(head)}<br><b class="new-balance">${escapeHtml(dict.balanceNow(state.balance.credits))}</b></p>`;
  }
  if (order.status === "rejected") statusHtml = `<p class="pay-status bad">${escapeHtml(dict.payRejected)}</p>`;
  box.innerHTML = `
    <h3 id="pay-title">${escapeHtml(dict.payTitle)}</h3>
    <div class="pay-summary">
      <div><small>${escapeHtml(dict.payOrder)}</small><b class="code">${escapeHtml(order.code)}</b></div>
      <div><small>${escapeHtml(dict.payAmount)}</small><b>฿${order.price}</b></div>
    </div>
    <p class="pay-get">${escapeHtml(dict.payGet(order.questions, order.bonus))}</p>
    <div class="qr-frame">
      <div class="qr-head">PromptPay · พร้อมเพย์</div>
      <div class="qr" id="qr">${qrSvg(o.promptpay.payload)}</div>
      <div class="qr-amount">฿${order.price}.00</div>
    </div>
    <ol class="pay-steps">
      <li>${dict.payStep1(order.price)}</li>
      <li>${state.slipEnabled && order.status === "pending" ? dict.payStep2Slip(escapeHtml(order.code)) : dict.payStep2(escapeHtml(order.code))}</li>
      <li>${escapeHtml(dict.payStep3)}</li>
    </ol>
    ${state.slipEnabled && order.status === "pending" ? slipSectionHtml(dict) : ""}
    ${statusHtml}
    ${state.slipEnabled && order.status === "pending" ? `<p class="or-line">${escapeHtml(dict.orLine)}</p>` : ""}
    <div class="pay-actions">
      <button type="button" class="btn ghost" id="copy-code">${escapeHtml(dict.copyCode)}</button>
      <a class="btn gold line-btn" href="https://line.me/ti/p/~ivymoonask" target="_blank" rel="noopener">${escapeHtml(dict.payLine)}</a>
    </div>`;
  if (state.slipEnabled && order.status === "pending") setupSlipUpload();
  document.getElementById("copy-code").addEventListener("click", async (event) => {
    try { await navigator.clipboard.writeText(order.code); } catch (_) { /* ignore */ }
    event.currentTarget.textContent = dict.copied;
  });
}

function slipSectionHtml(dict) {
  const r = state.slipResult;
  let msg = "";
  if (r) {
    const text = state.lang === "th" ? r.th : r.en;
    msg = `<p class="slip-msg ${escapeHtml(r.kind)}" role="status">${escapeHtml(text)}</p>`;
  }
  return `
    <div class="slip-box">
      <p class="slip-title">${escapeHtml(dict.slipTitle)}</p>
      <p class="slip-hint">${escapeHtml(dict.slipHint)}</p>
      <label class="slip-pick">
        <input type="file" id="slip-file" accept="image/jpeg,image/png,image/webp" />
        <span id="slip-file-label">${escapeHtml(state.slipFile ? state.slipFile.name : dict.slipChoose)}</span>
      </label>
      <button type="button" class="btn gold" id="slip-send" ${state.slipBusy ? "disabled" : ""}>${escapeHtml(state.slipBusy ? dict.slipChecking : dict.slipCheck)}</button>
      ${msg}
    </div>`;
}

function setSlipResult(kind, th, en) {
  state.slipResult = { kind, th, en };
}

function setupSlipUpload() {
  const input = document.getElementById("slip-file");
  const label = document.getElementById("slip-file-label");
  const send = document.getElementById("slip-send");
  let file = state.slipFile || null;
  const OK_TYPES = ["image/jpeg", "image/png", "image/webp"];
  const validate = (f) => {
    const dict = t();
    if (!f) return dict.slipNoFile;
    const typeOk = OK_TYPES.includes(f.type) || /\.(jpe?g|png|webp)$/i.test(f.name || "");
    if (!typeOk) return dict.slipBadType;
    if (f.size > state.slipMaxBytes) return dict.slipTooBig;
    return null;
  };
  input.addEventListener("change", () => {
    file = (input.files && input.files[0]) || null;
    state.slipFile = file;
    const problem = validate(file);
    label.textContent = file ? file.name : t().slipChoose;
    if (problem && file) {
      setSlipResult("failed", problem, problem);
      renderPayModal();
    }
  });
  send.addEventListener("click", async () => {
    const problem = validate(file);
    if (problem) {
      const th = I18N.th[problem === t().slipNoFile ? "slipNoFile" : problem === t().slipTooBig ? "slipTooBig" : "slipBadType"];
      const en = I18N.en[problem === t().slipNoFile ? "slipNoFile" : problem === t().slipTooBig ? "slipTooBig" : "slipBadType"];
      setSlipResult("failed", th, en);
      renderPayModal();
      return;
    }
    const code = state.order.order.code;
    state.slipBusy = true;
    state.slipResult = null;
    renderPayModal();
    try {
      const response = await fetch(`/api/orders/${encodeURIComponent(code)}/slip`, {
        method: "POST",
        headers: { "X-Visitor-Id": state.visitor, "Content-Type": file.type || "application/octet-stream" },
        body: file,
      });
      let data = {};
      try { data = await response.json(); } catch (_) { /* empty */ }
      if (response.ok && data.ok) {
        setSlipResult(data.result, data.messageTh, data.messageEn);
        if (data.balance) setBalance(data.balance);
        if (data.order && state.order && state.order.order.code === data.order.code) state.order.order = data.order;
        if (data.result === "success") {
          stopPolling();
          toast(state.lang === "th" ? data.messageTh : data.messageEn);
        }
      } else {
        const key = data.code || "network";
        setSlipResult("failed", I18N.th.slipErr[key] || data.error || I18N.th.slipErr.network,
          I18N.en.slipErr[key] || data.error || I18N.en.slipErr.network);
      }
    } catch (_) {
      setSlipResult("failed", I18N.th.slipErr.network, I18N.en.slipErr.network);
    } finally {
      state.slipBusy = false;
      renderPayModal();
      const target = document.querySelector("#pay-content .slip-msg, #pay-content .pay-status.ok");
      if (target) target.scrollIntoView({ block: "center", behavior: "smooth" });
    }
  });
}

function toast(message) {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.hidden = false;
  el.classList.add("show");
  setTimeout(() => { el.classList.remove("show"); el.hidden = true; }, 4200);
}

async function checkOrders() {
  try {
    const { response, data } = await api("/api/orders");
    if (!response.ok || !data.ok) return;
    setBalance(data);
    if (state.order && state.order.order) {
      const fresh = data.orders.find((o) => o.code === state.order.order.code);
      if (fresh && fresh.status !== state.order.order.status) {
        state.order.order = fresh;
        renderPayModal();
        if (fresh.status === "approved") toast(t().payApproved(fresh.questions));
        if (fresh.status !== "pending") stopPolling();
      }
    }
  } catch (_) { /* try again next tick */ }
}

async function buy(amount) {
  if (!state.paymentEnabled) {
    state.order = { soon: true };
    renderPayModal();
    openPayModal();
    return;
  }
  try {
    const { response, data } = await api("/api/orders", {
      method: "POST",
      body: JSON.stringify({ amount }),
    });
    if (response.status === 503 && data.code === "payment_disabled") {
      state.paymentEnabled = false;
      return buy(amount);
    }
    if (!response.ok || !data.ok) throw new Error(data.error || t().payError);
    state.slipResult = null;
    state.slipFile = null;
    state.order = data;
    renderPayModal();
    openPayModal();
    stopPolling();
    state.pollTimer = setInterval(checkOrders, 8000);
  } catch (err) {
    toast(err.message || t().payError);
  }
}

function setupPricing() {
  document.getElementById("price-grid").addEventListener("click", (event) => {
    const btn = event.target.closest(".buy");
    if (btn) buy(Number(btn.dataset.amount));
  });
  const modal = document.getElementById("pay-modal");
  document.getElementById("pay-close-x").addEventListener("click", closePayModal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) closePayModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) closePayModal();
  });
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) checkOrders();
  });
}

function setup() {
  const dateInput = document.getElementById("birthDate");
  dateInput.max = new Date().toISOString().slice(0, 10);
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => setLang(btn.dataset.lang));
  });
  document.getElementById("reading-form").addEventListener("submit", onSubmit);
  setupPricing();
  applyLang();
  paintStars();
  loadPackages();
  checkOrders();
}

setup();
