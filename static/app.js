const I18N = {
  th: {
    docTitle: "ถามจันทร์ — ดูดวงไพ่ทาโรต์ 3 ใบ ตอบตรง ๆ | Ask the Moon",
    brand: "ถามจันทร์",
    brandSub: "Ask the Moon",
    footBrand: "ถามจันทร์",
    eyebrow: "ไพ่ทาโรต์ 3 ใบ · ตอบตรง ๆ · โปรไฟล์ดวงจากวันเกิด",
    heroTitle: "ถามจันทร์",
    heroLede: "ดูดวงไพ่ทาโรต์ 3 ใบ ตอบตรง ๆ + โปรไฟล์ดวงจากวันเกิด (ปีนักษัตร เลขวันเกิด ราศี) — พิมพ์คำถามที่อยากรู้ จันทร์จะเปิดไพ่ให้ 3 ใบ บอกคำตอบก่อน แล้วตามด้วยเหตุผลจากไพ่และคำแนะนำที่ทำได้จริง",
    gateTitle: "สมัครฟรี รับคำถามแรกฟรี 1 ข้อ",
    gateCopy: "ถามไพ่ได้หลังสมัครหรือเข้าสู่ระบบ ใช้แค่ชื่อผู้ใช้กับรหัสผ่าน ไม่ต้องใช้อีเมล ไม่ถึง 1 นาที แล้วกรอกคำถามได้เลย",
    gateSignup: "สมัครฟรี",
    gateLogin: "เข้าสู่ระบบ",
    accReady: "พร้อมแล้ว! กรอกชื่อ วันเกิด และคำถามได้เลยค่ะ",
    gTitle: "เข้าสู่ระบบด้วย Google",
    gNote: "ใช้บัญชี Google (Gmail) เท่านั้น ไม่ต้องตั้งรหัสผ่าน เครดิตเก็บไว้ในบัญชี ใช้ได้ทุกอุปกรณ์",
    gFree: "บัญชีใหม่รับคำถามแรกฟรี 1 ข้อ",
    legalPre: "การเข้าสู่ระบบถือว่ายอมรับ", privacyLink: "นโยบายความเป็นส่วนตัว", legalAnd: "และ", termsLink: "ข้อกำหนดการใช้งาน",
    gPrivacy: "เราใช้อีเมลของคุณเพื่อผูกเครดิตกับบัญชี ไม่โพสต์หรือส่งอะไรในนามคุณ",
    gLoading: "กำลังโหลดปุ่ม Google…",
    gBlocked: "โหลดปุ่ม Google ไม่ได้ ลองปิดตัวบล็อกโฆษณา/โหมดส่วนตัว แล้วรีเฟรชหน้าอีกครั้ง",
    gateCopyG: "ถามไพ่ได้หลังเข้าสู่ระบบด้วย Google (Gmail) เท่านั้น ไม่ต้องตั้งรหัสผ่าน ไม่ถึง 1 นาที แล้วกรอกคำถามได้เลย",
    gateSignupG: "เข้าสู่ระบบด้วย Google",
    forgotLink: "ลืมรหัสผ่าน?",
    forgotHow: "ไม่ต้องกังวลค่ะ ทักแอดมินทางช่องทางด้านล่าง พร้อมแจ้ง “ชื่อผู้ใช้” ของคุณ แอดมินจะตั้งรหัสผ่านชั่วคราวให้ เข้าสู่ระบบแล้วเปลี่ยนรหัสใหม่ได้ที่เมนูบัญชี เครดิตของคุณยังอยู่ครบ",
    forgotNone: "ติดต่อแอดมินพร้อมแจ้งชื่อผู้ใช้ของคุณ",
    heroOfferIn: (n) => n > 0 ? `✨ คุณมีคำถามเหลือ ${n} ข้อ` : "✨ คุณมีคำถามฟรี 1 ข้อ ถามได้เลย",
    creditLogin: "สมัครฟรี รับคำถามแรกฟรี 1 ข้อ · เข้าสู่ระบบก่อนถามไพ่นะคะ",
    accNeedLoginAsk: "สมัครฟรี รับคำถามแรกฟรี 1 ข้อ ✨ กรุณาสมัครหรือเข้าสู่ระบบก่อนถามไพ่ค่ะ",
    profileTitle: "โปรไฟล์ดวงของคุณ",
    profileNote: "ข้อมูลนี้คำนวณจากวันเกิดของคุณ แยกจากคำตอบของไพ่ซึ่งอ่านจากไพ่ 3 ใบเท่านั้น",
    profileSub: (p) => `เกิด${p.weekdayTh}ที่ ${p.dateTh}${p.birthTime ? " เวลา " + p.birthTime + " น." : ""}`,
    profChinese: "ปีนักษัตร",
    profNumber: "เลขวันเกิด",
    profWestern: "ราศีตะวันตก",
    profHour: "ยามเกิด",
    profMaster: "เลขมาสเตอร์",
    adHeading: "พื้นที่แห่งโอกาสสำหรับแบรนด์ของคุณ",
    adLine1: "ร่วมเป็นส่วนหนึ่งของจักรวาลแห่งการพยากรณ์",
    adLine2: "เปิดรับโฆษณา ประชาสัมพันธ์สินค้าและบริการ สำหรับผู้ที่สนใจร่วมลงพื้นที่โฆษณาบนเว็บไซต์",
    adContact: "ติดต่อสอบถามรายละเอียดเพิ่มเติมได้ที่นี่ · LINE: ivymoonask",
    formTitle: "ถามไพ่ของคุณ",
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
    qLabel: "คำถามของคุณ",
    detailsLabel: "เล่าเพิ่มเติม",
    detailsHint: "บอกสถานการณ์ตอนนี้ให้จันทร์เข้าใจ เช่น เขาเป็นใครกับคุณ เกิดอะไรขึ้น เพื่อให้คำตอบตรงกับเรื่องของคุณมากขึ้น",
    detailsPh: "เช่น คุยกับเขามา 3 เดือน ช่วงนี้เขาตอบช้าลง",
    qPh: "เช่น งานใหม่ที่สมัครไว้จะได้ไหม?",
    submit: "เปิดไพ่ถามจันทร์",
    loading: "กำลังสับไพ่และเปิดไพ่ให้คุณ...",
    freeTag: "บทอ่านฟรี",
    freeTitle: "คำตอบจากไพ่",
    premTag: "พรีเมียม",
    premTitle: "บทอ่านลึก",
    lockTitle: "ปลดล็อกบทอ่านลึก",
    lockCopy: "ช่วงเวลาที่ไพ่ชี้ จุดแข็ง สิ่งที่ต้องระวัง ขั้นต่อไปที่ควรทำ เลข สี และวันมงคลจากไพ่ของคุณ",
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
    how2: "อัปโหลดสลิปบนหน้านี้ ระบบตรวจสอบให้อัตโนมัติ",
    how3: "เครดิตเข้าบัญชีของคุณทันทีหลังตรวจผ่าน",
    baht: "บาท",
    questionsUnit: () => "ข้อ",
    totalLabel: "รวมทั้งหมด",
    split: (b, x, q) => `${b} + โบนัส ${x} = รวม ${q} ข้อ`,
    noBonus: (q) => `${q} ข้อ · ไม่มีโบนัส`,
    perQ: (v) => `เฉลี่ย ฿${v.replace(/\.00$/, "")} / ข้อ`,
    save: (pct) => `ถูกลง ${pct}%`,
    saveVs: (pct) => `ถูกลง ${pct}% จากราคาปกติข้อละ ฿15`,
    buy: "เลือกแพ็กเกจนี้",
    buyBest: "รับดีลที่คุ้มที่สุด",
    bestTag: "BEST VALUE · คุ้มที่สุด",
    bestBadge: (pkg) => `จ่าย ${pkg.price} บาท ได้ ${pkg.questions} ข้อ (โบนัส ${pkg.bonus} ข้อ) เฉลี่ยข้อละ ${pkg.perQuestion.replace(/\.00$/, "")} บาท`,
    payTitle: "ชำระผ่านพร้อมเพย์",
    payRef: "อ้างอิง",
    payAmount: "ยอดชำระ",
    payGet: (q, b) => b ? `รับรวม ${q} ข้อ (${q - b} + โบนัส ${b})` : `รับ ${q} ข้อ`,
    payStep1: (a) => `สแกน QR ด้วยแอปธนาคาร แล้วโอน <b>฿${a}</b> ให้ตรงยอด`,
    payLine: "มีปัญหา? ติดต่อ LINE",
    payWaiting: "รอสลิปของคุณ…",
    payReview: "กำลังตรวจสอบเพิ่มเติม เครดิตจะเข้าอัตโนมัติเมื่อผ่าน",
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
      too_many_slips: "อัปโหลดสลิปครบจำนวนครั้งแล้ว มีปัญหา? ติดต่อ LINE: ivymoonask",
      not_pending: "คำสั่งซื้อนี้ปิดแล้ว กรุณาสร้างคำสั่งซื้อใหม่",
      not_found: "ไม่พบคำสั่งซื้อนี้ กรุณาสร้างคำสั่งซื้อใหม่",
      bad_file_type: "ไฟล์นี้ไม่ใช่รูป JPG, PNG หรือ WEBP",
      file_too_large: "รูปใหญ่เกิน 4MB",
      network: "เชื่อมต่อไม่ได้ กรุณาลองอัปโหลดใหม่อีกครั้ง",
    },
    payStep2Slip: () => "อัปโหลดสลิปด้านล่าง ระบบตรวจและเติมคำถามให้ทันที",
    accountLogin: "เข้าสู่ระบบ",
    accountNote: "สมัครบัญชีเพื่อเก็บเครดิตไว้ใช้ได้ทุกอุปกรณ์",
    accTitleLogin: "เข้าสู่ระบบ",
    accTitleSignup: "สมัครบัญชี",
    accTabLogin: "เข้าสู่ระบบ",
    accTabSignup: "สมัครใหม่",
    accUser: "ชื่อผู้ใช้",
    accUserHint: "3–20 ตัว ใช้ a-z, 0-9 หรือ _",
    accPass: "รหัสผ่าน",
    accPassHint: "อย่างน้อย 8 ตัวอักษร",
    accSubmitLogin: "เข้าสู่ระบบ",
    accSubmitSignup: "สมัครและเข้าสู่ระบบ",
    accBusy: "กำลังดำเนินการ…",
    accNeedLogin: "กรุณาสมัครบัญชีหรือเข้าสู่ระบบก่อนซื้อแพ็กเกจ เครดิตจะได้ไม่หายและใช้ได้ทุกอุปกรณ์ค่ะ",
    accMerged: (n) => n > 0 ? `ย้ายเครดิต ${n} คำถามเข้าบัญชีแล้ว ✨` : "",
    accWelcome: (u) => `ยินดีต้อนรับ ${u} ✨`,
    accHello: (u) => `สวัสดี ${u}`,
    accBalance: (n) => `เหลือ ${n} คำถาม`,
    accLogout: "ออกจากระบบ",
    accLoggedOut: "ออกจากระบบแล้ว",
    accChangePw: "เปลี่ยนรหัสผ่าน",
    accCurrentPw: "รหัสผ่านปัจจุบัน",
    accNewPw: "รหัสผ่านใหม่",
    accPwChanged: "เปลี่ยนรหัสผ่านแล้ว",
    accForgot: "ลืมรหัสผ่าน? ทัก LINE: ivymoonask แอดมินจะตั้งรหัสชั่วคราวให้",
    accErr: {
      bad_login: "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง",
      bad_google_token: "เข้าสู่ระบบด้วย Google ไม่สำเร็จ กรุณาลองใหม่",
      google_only: "ตอนนี้เข้าสู่ระบบด้วย Google ได้อย่างเดียวค่ะ",
      username_taken: "ชื่อผู้ใช้นี้มีคนใช้แล้ว ลองชื่ออื่นนะคะ",
      bad_username: "ชื่อผู้ใช้ต้องมี 3–20 ตัว ใช้ได้เฉพาะ a-z, 0-9 และ _",
      weak_password: "รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร",
      bad_password: "รหัสผ่านยาวเกินไป",
      rate_limited: "ลองหลายครั้งเกินไป กรุณารอสักครู่แล้วลองใหม่",
      login_required: "กรุณาเข้าสู่ระบบก่อน",
      network: "เชื่อมต่อไม่ได้ กรุณาลองใหม่",
    },
    tarotCredit: "ภาพไพ่ทาโรต์: สำรับ Rider-Waite-Smith (ค.ศ. 1909) วาดโดย Pamela Colman Smith · สาธารณสมบัติ จาก Wikimedia Commons",
    tarotReversed: "กลับหัว",
    tarotTap: "แตะไพ่เพื่อดูความหมาย",
    disclaimer: "คำตอบจากไพ่ทาโรต์มีไว้เป็นแนวทาง ไม่ใช่คำแนะนำทางการแพทย์ กฎหมาย หรือการเงิน การตัดสินใจสุดท้ายเป็นของคุณ",
    badgeZodiac: "ราศีตะวันตก",
    badgeChinese: "ปีนักษัตร",
    badgePath: "เลขเส้นทางชีวิต",
    badgeHour: "ยามเกิด",
    master: "เลขปรมาจารย์",
    sourceTemplate: "คำตอบจากความหมายของไพ่ (ระบบสำรอง)",
    sourceLlm: "เรียบเรียงโดยปัญญาประดิษฐ์ จากไพ่ 3 ใบของคุณ",
    resultFor: (name, topic) => `คำตอบสำหรับ ${name} · ${topic}`,
    needName: "กรุณาใส่ชื่อ",
    needDate: "กรุณาใส่วันเกิด",
    hours: { dawn: "รุ่งสาง", morning: "เช้า", afternoon: "บ่าย", evening: "เย็น", night: "ค่ำคืน" },
    topics: { love: "ความรัก", career: "การงาน", money: "การเงิน", life_path: "เส้นทางชีวิต" },
    luckNumbers: "เลขจากไพ่",
    luckColors: "สีมงคลจากไพ่",
    luckDay: "วันมงคล",
    gift: "จุดแข็งจากไพ่",
    shadow: "สิ่งที่ต้องระวัง",
    compat: "ขั้นต่อไปที่ควรทำ",
    forecast: "ช่วงเวลาที่ไพ่ชี้",
  },
  en: {
    docTitle: "Ask the Moon — 3-card tarot, straight answers | ถามจันทร์",
    brand: "Ask the Moon",
    brandSub: "ถามจันทร์",
    footBrand: "Ask the Moon",
    eyebrow: "3-card tarot · Straight answers · Birth profile",
    heroTitle: "Ask the Moon",
    heroLede: "Type what you want to know. The Moon draws three tarot cards and gives you a straight answer, the reasons in the cards, and advice you can act on. Add your birthday to see your Chinese zodiac, birth number, and star sign too.",
    gateTitle: "Sign up free — get your first question free",
    gateCopy: "You can ask after signing up or logging in. Just a username and password, no email, under a minute — then type your question.",
    gateSignup: "Sign up free",
    gateLogin: "Log in",
    accReady: "You're in! Fill in your name, birthday and question.",
    gTitle: "Sign in with Google",
    gNote: "Google (Gmail) accounts only. No password to remember; your credits are saved to your account on every device.",
    gFree: "New accounts get 1 free question",
    legalPre: "By signing in you agree to the", privacyLink: "Privacy Policy", legalAnd: "and", termsLink: "Terms of Service",
    gPrivacy: "We use your email to link your credits to your account. We never post or send anything as you.",
    gLoading: "Loading the Google button…",
    gBlocked: "The Google button didn't load. Try turning off ad blockers / private mode, then reload.",
    gateCopyG: "You can ask after signing in with Google (Gmail). No password, under a minute — then type your question.",
    gateSignupG: "Sign in with Google",
    forgotLink: "Forgot password?",
    forgotHow: "No worries. Message the admin on one of the channels below with your username. The admin will set a temporary password; log in and change it from the account menu. Your credits stay safe.",
    forgotNone: "Contact the admin with your username.",
    heroOfferIn: (n) => n > 0 ? `✨ You have ${n} questions left` : "✨ You have 1 free question — ask away",
    creditLogin: "Sign up free and get your first question free · please log in to ask.",
    accNeedLoginAsk: "Sign up free and get 1 free question ✨ Please sign up or log in to ask the cards.",
    profileTitle: "Your birth profile",
    profileNote: "Worked out from your birthday, separate from the tarot answer, which reads only the three cards.",
    profileSub: (p) => `Born on a ${p.weekdayEn}, ${p.dateEn}${p.birthTime ? " at " + p.birthTime : ""}`,
    profChinese: "Chinese zodiac",
    profNumber: "Birth number",
    profWestern: "Star sign",
    profHour: "Hour of birth",
    profMaster: "Master number",
    adHeading: "A space of opportunity for your brand",
    adLine1: "Become part of the universe of fortune-telling",
    adLine2: "Now accepting ads to promote your products and services",
    adContact: "Contact us here for more details · LINE: ivymoonask",
    formTitle: "Ask the cards",
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
    qLabel: "Your question",
    detailsLabel: "Tell us more",
    detailsHint: "Describe what's going on so the moon understands, e.g. who they are to you and what happened, so the answer fits your situation better.",
    detailsPh: "e.g. We've been talking for 3 months and lately they reply more slowly.",
    qPh: "e.g. Will I get the new job I applied for?",
    submit: "Draw the cards",
    loading: "Shuffling and drawing your cards...",
    freeTag: "Free reading",
    freeTitle: "The cards' answer",
    premTag: "Premium",
    premTitle: "Deep reading",
    lockTitle: "Unlock the deep reading",
    lockCopy: "Timing, your strength, what to watch out for, your next step, plus numbers, colors and a good day from your cards.",
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
    how2: "Upload your slip on this page and it's verified automatically.",
    how3: "Credits are added to your account right after the slip passes.",
    baht: "THB",
    questionsUnit: (n) => (n === 1 ? "question" : "questions"),
    totalLabel: "Total",
    split: (b, x, q) => `${b} + ${x} bonus = ${q} total`,
    noBonus: (q) => `${q} ${q === 1 ? "question" : "questions"} · no bonus`,
    perQ: (v) => `Avg ฿${v.replace(/\.00$/, "")} / question`,
    save: (pct) => `${pct}% off`,
    saveVs: (pct) => `${pct}% off the regular ฿15 per question`,
    buy: "Choose this pack",
    buyBest: "Get the best deal",
    bestTag: "BEST VALUE",
    bestBadge: (pkg) => `Pay ${pkg.price} THB, get ${pkg.questions} questions (${pkg.bonus} bonus), avg ${pkg.perQuestion.replace(/\.00$/, "")} THB each`,
    payTitle: "Pay with PromptPay",
    payRef: "ref",
    payAmount: "Amount",
    payGet: (q, b) => b ? `${q} questions total (${q - b} + ${b} bonus)` : `${q} questions`,
    payStep1: (a) => `Scan this QR in your banking app and pay exactly <b>฿${a}</b>.`,
    payLine: "Problem? Contact LINE",
    payWaiting: "Waiting for your slip…",
    payReview: "We're checking this further. Credits are added automatically once it passes.",
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
      too_many_slips: "Upload limit reached for this order. Problem? Contact LINE: ivymoonask",
      not_pending: "This order is closed. Please create a new one.",
      not_found: "Order not found. Please create a new one.",
      bad_file_type: "That file isn't a JPG, PNG, or WEBP image.",
      file_too_large: "The image is over 4MB.",
      network: "Couldn't connect. Please try uploading again.",
    },
    payStep2Slip: () => "Upload your slip below. It's checked and your questions are added right away.",
    accountLogin: "Log in",
    accountNote: "Create an account to keep your credits on every device",
    accTitleLogin: "Log in",
    accTitleSignup: "Create an account",
    accTabLogin: "Log in",
    accTabSignup: "Sign up",
    accUser: "Username",
    accUserHint: "3–20 characters: a-z, 0-9 or _",
    accPass: "Password",
    accPassHint: "At least 8 characters",
    accSubmitLogin: "Log in",
    accSubmitSignup: "Sign up and log in",
    accBusy: "Working…",
    accNeedLogin: "Please sign up or log in before buying, so your credits are safe on any device.",
    accMerged: (n) => n > 0 ? `Moved ${n} question${n === 1 ? "" : "s"} into your account ✨` : "",
    accWelcome: (u) => `Welcome, ${u} ✨`,
    accHello: (u) => `Hi, ${u}`,
    accBalance: (n) => `${n} question${n === 1 ? "" : "s"} left`,
    accLogout: "Log out",
    accLoggedOut: "Logged out",
    accChangePw: "Change password",
    accCurrentPw: "Current password",
    accNewPw: "New password",
    accPwChanged: "Password changed",
    accForgot: "Forgot your password? Message LINE: ivymoonask and the admin will set a temporary one.",
    accErr: {
      bad_login: "Wrong username or password.",
      bad_google_token: "Google sign-in failed. Please try again.",
      google_only: "Please sign in with Google.",
      username_taken: "That username is taken. Try another one.",
      bad_username: "Usernames are 3–20 characters: a-z, 0-9 and _ only.",
      weak_password: "Passwords need at least 8 characters.",
      bad_password: "That password is too long.",
      rate_limited: "Too many attempts. Please wait a moment and try again.",
      login_required: "Please log in first.",
      network: "Couldn't connect. Please try again.",
    },
    tarotCredit: "Tarot art: Rider-Waite-Smith deck (1909) by Pamela Colman Smith · public domain, via Wikimedia Commons",
    tarotReversed: "Reversed",
    tarotTap: "Tap a card to see its meaning",
    disclaimer: "Tarot answers are guidance, not medical, legal, or financial advice. The final decision is yours.",
    badgeZodiac: "Western zodiac",
    badgeChinese: "Chinese zodiac",
    badgePath: "Life path number",
    badgeHour: "Hour of birth",
    master: "Master number",
    sourceTemplate: "Answer from the card meanings (backup mode)",
    sourceLlm: "Written by AI from your three cards",
    resultFor: (name, topic) => `An answer for ${name} · ${topic}`,
    needName: "Please enter a name.",
    needDate: "Please enter a birth date.",
    hours: { dawn: "Dawn", morning: "Morning", afternoon: "Afternoon", evening: "Evening", night: "Night" },
    topics: { love: "Love", career: "Career", money: "Money", life_path: "Life path" },
    luckNumbers: "Numbers from your cards",
    luckColors: "Colors from your cards",
    luckDay: "Fortunate day",
    gift: "Your strength in the cards",
    shadow: "What to watch out for",
    compat: "Your next step",
    forecast: "Timing the cards show",
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
  balance: { credits: 0, freeAvailable: false },
  packages: [],
  paymentEnabled: false,
  slipEnabled: false,
  slipMaxBytes: 4 * 1024 * 1024,
  slipResult: null,
  slipBusy: false,
  slipFile: null,
  order: null,
  pollTimer: null,
  account: null,
  accountMode: "signup",
  accountMsg: null,
  accountBusy: false,
  afterLogin: null,
  authMode: "password",
  googleClientId: null,
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
  renderAccountButton();
  const accModal = document.getElementById("account-modal");
  if (accModal && !accModal.hidden) renderAccountModal();
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

const ANIMAL_ICON = { rat: "🐀", ox: "🐂", tiger: "🐅", rabbit: "🐇", dragon: "🐉", snake: "🐍",
  horse: "🐎", goat: "🐐", monkey: "🐒", rooster: "🐓", dog: "🐕", pig: "🐖" };

function renderProfile(p) {
  const panel = document.getElementById("profile-panel");
  if (!p) {
    panel.hidden = true;
    return;
  }
  const th = state.lang === "th";
  const dict = t();
  const L = (o, k) => (th ? o[k + "Th"] : o[k + "En"]);
  const item = (icon, label, value, extra, meaning) => `
    <div class="prof-item">
      <div class="prof-icon" aria-hidden="true">${escapeHtml(icon)}</div>
      <div class="prof-text">
        <small>${escapeHtml(label)}</small>
        <b>${escapeHtml(value)}</b>
        ${extra ? `<span class="prof-extra">${escapeHtml(extra)}</span>` : ""}
        <p>${escapeHtml(meaning)}</p>
      </div>
    </div>`;
  const c = p.chinese, n = p.number, w = p.western;
  const items = [
    item(ANIMAL_ICON[c.key] || "☯", dict.profChinese, th ? `ปี${c.th}` : `${c.en}`,
      th ? `ปีนักษัตรเริ่มตรุษจีน พ.ศ. ${c.lunarYear + 543}` : `Lunar year from Chinese New Year ${c.lunarYear}`,
      `${L(c, "meaning")} · ${L(c, "element")}`),
    item(String(n.value), dict.profNumber, `${n.value} · ${L(n, "title")}`, n.master ? dict.profMaster : "", L(n, "meaning")),
    item(w.glyph, dict.profWestern, th ? w.th : w.en, `${L(w, "dates")} · ${L(w, "element")}`, L(w, "meaning")),
  ];
  if (p.hour) items.push(item("☾", dict.profHour, th ? p.hour.th : p.hour.en, p.birthTime || "", L(p.hour, "meaning")));
  document.getElementById("profile-grid").innerHTML = items.join("");
  document.getElementById("profile-sub").textContent = dict.profileSub(p);
  panel.hidden = false;
}

function renderResult(data) {
  const dict = t();
  const result = document.getElementById("result");
  const topicLabel = dict.topics[data.topic] || data.topic;
  document.getElementById("result-for").textContent = dict.resultFor(data.name, topicLabel);

  const badges = data.question ? [badge(dict.qLabel, data.question)] : [];
  document.getElementById("badges").innerHTML = badges.join("");
  renderTarot(data.tarot);
  renderProfile(data.profile);
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
  const question = document.getElementById("question").value.trim();
  const details = document.getElementById("details").value.trim().slice(0, 500);
  const topic = (document.querySelector('input[name="topic"]:checked') || {}).value || "life_path";

  const birthDate = document.getElementById("birthDate").value;
  const birthTime = document.getElementById("birthTime").value;

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

  if (!state.account) {
    // Every question (the free one too) needs an account.
    state.afterLogin = () => document.getElementById("reading-form").requestSubmit();
    openAccountModal("signup", dict.accNeedLoginAsk);
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
        details,
        lang: state.lang,
      }),
    });
    if (response.status === 402) {
      await refreshBalance();
      showNoCredits();
      return;
    }
    if (response.status === 401 && data.code === "login_required") {
      state.account = null;
      renderAccountButton();
      state.afterLogin = () => document.getElementById("reading-form").requestSubmit();
      openAccountModal("signup", dict.accNeedLoginAsk);
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
  if ("account" in balance) {
    state.account = balance.account;
    renderAccountButton();
  }
  if (balance.birth) prefillBirth(balance.birth);
  const before = state.balance.credits;
  state.balance = { credits: Number(balance.credits) || 0, freeAvailable: Boolean(balance.freeAvailable) };
  renderBalance(before !== state.balance.credits);
}

function prefillBirth(birth) {
  // Returning users: fill saved birth data, but never overwrite what they typed.
  const d = document.getElementById("birthDate");
  const tm = document.getElementById("birthTime");
  if (birth.date && !d.value) d.value = birth.date;
  if (birth.time && !tm.value) tm.value = birth.time;
}

function renderOffer() {
  const dict = t();
  const btn = document.getElementById("hero-signup");
  if (!btn) return;
  const { credits, freeAvailable } = state.balance;
  // Logged out: no hero button. The sign-in card below already has the one Google button.
  // Logged in: a quiet status line ("you have N questions"), only when there is something to ask with.
  const show = Boolean(state.account) && (credits > 0 || freeAvailable);
  if (show) btn.textContent = dict.heroOfferIn(credits);
  btn.parentElement.hidden = !show;
  btn.classList.toggle("is-in", show);
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
  strip.classList.toggle("needs-login", !state.account);
  if (!state.account && credits <= 0) {
    strip.classList.remove("is-empty");
    text.textContent = dict.creditLogin;
  } else if (credits > 0) text.innerHTML = dict.creditHave(credits);
  else if (freeAvailable) text.textContent = dict.creditFree;
  else text.textContent = dict.creditNone;
  renderOffer();
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
      state.contacts = Array.isArray(data.contacts) ? data.contacts : [];
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
  // Every number on a card comes from the same package record:
  // headline = total questions (bonus included); breakdown = base + bonus = total; per question = price / total.
  grid.innerHTML = state.packages.map((pkg, i) => {
    const tier = tierOf(pkg);
    const qty = `<p class="qty"><small>${escapeHtml(dict.totalLabel)}</small> <b>${pkg.questions}</b> ${escapeHtml(dict.questionsUnit(pkg.questions))}</p>`;
    const split = `<p class="bonus ${pkg.bonus ? "" : "none"}">${escapeHtml(dict.split(pkg.baseQuestions, pkg.bonus, pkg.questions))}</p>`;
    const per = `<span class="per">${escapeHtml(dict.perQ(pkg.perQuestion))}</span>`;
    if (pkg.bestValue) {
      return `
      <article class="price-card ${tier}" style="--i:${i}">
        <div class="best-badge">${escapeHtml(dict.bestTag)}</div>
        <div class="best-body">
          <div class="best-main">
            <p class="price"><span class="cur">฿</span>${pkg.price}</p>
            ${qty}
            ${split}
          </div>
          <p class="best-line">✦ ${escapeHtml(dict.bestBadge(pkg))}</p>
        </div>
        <p class="meta">${pkg.savingsPercent > 0 ? `<span class="save-pill inline">${escapeHtml(dict.saveVs(pkg.savingsPercent))}</span>` : per}</p>
        <button type="button" class="btn gold buy" data-amount="${pkg.price}">${escapeHtml(dict.buyBest)}</button>
      </article>`;
    }
    const save = pkg.savingsPercent > 0
      ? `<span class="save-pill">${escapeHtml(dict.save(pkg.savingsPercent))}</span>` : "";
    return `
      <article class="price-card ${tier}${pkg.bonus ? " has-save" : ""}" style="--i:${i}">
        ${save}
        <p class="price"><span class="cur">฿</span>${pkg.price}</p>
        ${qty}
        ${split}
        <p class="meta">${per}</p>
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
  const inReview = order.slipStatus === "review" || (state.slipResult && state.slipResult.kind === "review");
  let statusHtml = `<p class="pay-status waiting"><span class="pulse"></span>${escapeHtml(inReview ? dict.payReview : dict.payWaiting)}</p>`;
  if (order.status === "approved") {
    const r = state.slipResult;
    const head = r && r.kind === "success" ? (state.lang === "th" ? r.th : r.en) : dict.payApproved(order.questions);
    statusHtml = `<p class="pay-status ok">${escapeHtml(head)}<br><b class="new-balance">${escapeHtml(dict.balanceNow(state.balance.credits))}</b></p>`;
  }
  if (order.status === "rejected") statusHtml = `<p class="pay-status bad">${escapeHtml(dict.payRejected)}</p>`;
  box.innerHTML = `
    <h3 id="pay-title">${escapeHtml(dict.payTitle)}</h3>
    <div class="pay-summary">
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
      <li>${escapeHtml(dict.payStep2Slip())}</li>
    </ol>
    ${state.slipEnabled && order.status === "pending" ? slipSectionHtml(dict) : ""}
    ${statusHtml}
    <p class="pay-help"><a href="https://line.me/ti/p/~ivymoonask" target="_blank" rel="noopener">${escapeHtml(dict.payLine)}</a> <span class="pay-ref">· ${escapeHtml(dict.payRef)} ${escapeHtml(order.code)}</span></p>`;
  if (state.slipEnabled && order.status === "pending") setupSlipUpload();
}

function slipSectionHtml(dict) {
  const r = state.slipResult;
  let msg = "";
  if (r && r.kind !== "review") { // review is shown as the neutral status line below
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
  if (!state.account) {
    state.afterLogin = () => buy(amount);
    openAccountModal("signup", t().accNeedLogin);
    return;
  }
  try {
    const { response, data } = await api("/api/orders", {
      method: "POST",
      body: JSON.stringify({ amount }),
    });
    if (response.status === 401 && data.code === "login_required") {
      state.account = null;
      renderAccountButton();
      state.afterLogin = () => buy(amount);
      openAccountModal("signup", t().accNeedLogin);
      return;
    }
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

// ---- accounts ------------------------------------------------------------
function renderAccountButton() {
  const label = document.getElementById("account-label");
  const btn = document.getElementById("account-btn");
  if (!label) return;
  if (state.account) {
    label.textContent = shortName(state.account.username);
    btn.classList.add("is-in");
  } else {
    label.textContent = t().accountLogin;
    btn.classList.remove("is-in");
  }
  const note = document.getElementById("pricing-account-note");
  if (note) note.hidden = Boolean(state.account);
  renderGate();
}

function openAccountModal(mode, message) {
  if (mode) state.accountMode = mode;
  state.accountMsg = message ? { kind: "info", text: message } : null;
  renderAccountModal();
  document.getElementById("account-modal").hidden = false;
  const first = document.querySelector("#account-content input");
  if (first) setTimeout(() => first.focus({ preventScroll: true }), 50);
}

function closeAccountModal() {
  document.getElementById("account-modal").hidden = true;
  state.afterLogin = null;
  state.accountMsg = null;
}

function accErrText(code, fallback) {
  const dict = t();
  return dict.accErr[code] || fallback || dict.accErr.network;
}

let gisPromise = null;

function loadGis() {
  if (window.google && window.google.accounts && window.google.accounts.id) return Promise.resolve(true);
  if (gisPromise) return gisPromise;
  gisPromise = new Promise((resolve) => {
    const s = document.createElement("script");
    s.src = "https://accounts.google.com/gsi/client?hl=" + (state.lang === "th" ? "th" : "en");
    s.async = true;
    s.defer = true;
    s.onload = () => resolve(true);
    s.onerror = () => { gisPromise = null; resolve(false); };
    document.head.appendChild(s);
  });
  return gisPromise;
}

let gisReady = false;

async function mountGoogleButton() {
  const slot = document.getElementById("g-btn");
  if (!slot) return;
  const ok = await loadGis();
  const slotNow = document.getElementById("g-btn");
  if (!slotNow) return;
  if (!ok || !window.google || !window.google.accounts) {
    slotNow.innerHTML = `<p class="acc-msg error">${escapeHtml(t().gBlocked)}</p>`;
    return;
  }
  if (!gisReady) {
    window.google.accounts.id.initialize({
      client_id: state.googleClientId,
      callback: onGoogleCredential,
      ux_mode: "popup",
      auto_select: false,
      cancel_on_tap_outside: true,
      itp_support: true,
    });
    gisReady = true;
  }
  slotNow.innerHTML = "";
  const width = Math.min(320, Math.max(220, slotNow.clientWidth || 300));
  window.google.accounts.id.renderButton(slotNow, {
    type: "standard", theme: "filled_black", size: "large", shape: "pill",
    text: "continue_with", logo_alignment: "left", width, locale: state.lang === "th" ? "th" : "en",
  });
}

async function onGoogleCredential(response) {
  const dict = t();
  state.accountBusy = true;
  state.accountMsg = { kind: "info", text: dict.accBusy };
  renderAccountModal();
  try {
    const { response: res, data } = await api("/api/auth/google", {
      method: "POST",
      body: JSON.stringify({ credential: response && response.credential }),
    });
    state.accountBusy = false;
    if (!res.ok || !data.ok) {
      state.accountMsg = { kind: "error", text: accErrText(data.code, data.error) };
      renderAccountModal();
      return;
    }
    finishLogin(data);
  } catch (_) {
    state.accountBusy = false;
    state.accountMsg = { kind: "error", text: dict.accErr.network };
    renderAccountModal();
  }
}

function finishLogin(data) {
  const dict = t();
  setBalance(data);
  const moved = data.merged ? data.merged.movedCredits : 0;
  const next = state.afterLogin;
  state.afterLogin = null;
  document.getElementById("account-modal").hidden = true;
  toast([dict.accWelcome(shortName(data.account.username)), dict.accMerged(moved)].filter(Boolean).join(" · "));
  checkOrders();
  if (next) next();
}

function shortName(u) {
  return String(u || "").split("@")[0];
}

function forgotHtml(dict) {
  const list = (state.contacts || []).map((c) =>
    `<li><a href="${escapeHtml(c.url)}" target="_blank" rel="noopener"><b>${escapeHtml(c.label)}</b> ${escapeHtml(c.value)}</a></li>`).join("");
  return `
    <details class="acc-forgot">
      <summary>${escapeHtml(dict.forgotLink)}</summary>
      <p>${escapeHtml(dict.forgotHow)}</p>
      ${list ? `<ul class="contact-list">${list}</ul>` : `<p>${escapeHtml(dict.forgotNone)}</p>`}
    </details>`;
}

function renderGate() {
  // Logged out: show the sign-up card first and lock the form, so nobody fills it in for nothing.
  const gate = document.getElementById("login-gate");
  const fields = document.getElementById("form-fields");
  if (!gate || !fields) return;
  const out = !state.account;
  gate.hidden = !out;
  fields.disabled = out;
  const dict = t();
  const g = state.authMode === "google";
  document.getElementById("gate-login").hidden = g;
  document.getElementById("gate-signup").textContent = g ? dict.gateSignupG : dict.gateSignup;
  document.querySelector("#login-gate .gate-copy").textContent = g ? dict.gateCopyG : dict.gateCopy;
  fields.classList.toggle("is-locked", out);
}

function renderAccountModal() {
  const dict = t();
  const box = document.getElementById("account-content");
  const msg = state.accountMsg
    ? `<p class="acc-msg ${escapeHtml(state.accountMsg.kind)}" role="status">${escapeHtml(state.accountMsg.text)}</p>` : "";
  if (state.account) {
    box.innerHTML = `
      <div class="acc-avatar" aria-hidden="true">☾</div>
      <h3 id="account-title">${escapeHtml(dict.accHello(shortName(state.account.username)))}</h3>
      ${state.account.google ? `<p class="acc-email">${escapeHtml(state.account.username)}</p>` : ""}
      <p class="acc-balance">${escapeHtml(dict.accBalance(state.balance.credits))}</p>
      ${msg}
      ${state.account.google || state.authMode === "google" ? "" : `<details class="acc-change">
        <summary>${escapeHtml(dict.accChangePw)}</summary>
        <form id="acc-pw-form" class="acc-form" novalidate>
          <label><span>${escapeHtml(dict.accCurrentPw)}</span>
            <input type="password" id="acc-cur" autocomplete="current-password" required /></label>
          <label><span>${escapeHtml(dict.accNewPw)}</span>
            <input type="password" id="acc-new" autocomplete="new-password" minlength="8" required />
            <small>${escapeHtml(dict.accPassHint)}</small></label>
          <button type="submit" class="btn ghost" ${state.accountBusy ? "disabled" : ""}>${escapeHtml(dict.accChangePw)}</button>
        </form>
      </details>`}
      <button type="button" class="btn gold" id="acc-logout">${escapeHtml(dict.accLogout)}</button>`;
    document.getElementById("acc-logout").addEventListener("click", logout);
    const pwForm = document.getElementById("acc-pw-form");
    if (pwForm) pwForm.addEventListener("submit", changePassword);
    return;
  }
  if (state.authMode === "google") {
    box.innerHTML = `
      <div class="acc-avatar" aria-hidden="true">☾</div>
      <h3 id="account-title">${escapeHtml(dict.gTitle)}</h3>
      <p class="acc-note">${escapeHtml(dict.gNote)}</p>
      ${msg}
      <p class="acc-free">✨ ${escapeHtml(dict.gFree)}</p>
      <div class="g-btn" id="g-btn"><p class="acc-note">${escapeHtml(dict.gLoading)}</p></div>
      <p class="acc-privacy">${escapeHtml(dict.gPrivacy)}</p>
      <p class="acc-legal">${escapeHtml(dict.legalPre)} <a href="/privacy" target="_blank" rel="noopener">${escapeHtml(dict.privacyLink)}</a> ${escapeHtml(dict.legalAnd)} <a href="/terms" target="_blank" rel="noopener">${escapeHtml(dict.termsLink)}</a></p>`;
    mountGoogleButton();
    return;
  }
  const signup = state.accountMode === "signup";
  box.innerHTML = `
    <div class="acc-avatar" aria-hidden="true">☾</div>
    <h3 id="account-title">${escapeHtml(signup ? dict.accTitleSignup : dict.accTitleLogin)}</h3>
    <p class="acc-note">${escapeHtml(dict.accountNote)}</p>
    <div class="acc-tabs" role="tablist">
      <button type="button" role="tab" class="acc-tab ${signup ? "is-on" : ""}" data-mode="signup" aria-selected="${signup}">${escapeHtml(dict.accTabSignup)}</button>
      <button type="button" role="tab" class="acc-tab ${signup ? "" : "is-on"}" data-mode="login" aria-selected="${!signup}">${escapeHtml(dict.accTabLogin)}</button>
    </div>
    ${msg}
    <form id="acc-form" class="acc-form" novalidate>
      <label><span>${escapeHtml(dict.accUser)}</span>
        <input type="text" id="acc-user" autocomplete="username" autocapitalize="none" spellcheck="false" maxlength="20" required />
        ${signup ? `<small>${escapeHtml(dict.accUserHint)}</small>` : ""}</label>
      <label><span>${escapeHtml(dict.accPass)}</span>
        <input type="password" id="acc-pass" autocomplete="${signup ? "new-password" : "current-password"}" maxlength="128" required />
        ${signup ? `<small>${escapeHtml(dict.accPassHint)}</small>` : ""}</label>
      <button type="submit" class="btn gold" ${state.accountBusy ? "disabled" : ""}>${escapeHtml(state.accountBusy ? dict.accBusy : (signup ? dict.accSubmitSignup : dict.accSubmitLogin))}</button>
    </form>
    ${signup ? "" : forgotHtml(dict)}`;
  box.querySelectorAll(".acc-tab").forEach((tab) => tab.addEventListener("click", () => {
    state.accountMode = tab.dataset.mode;
    const keep = state.accountMsg && state.accountMsg.kind === "info" ? state.accountMsg : null;
    state.accountMsg = keep;
    renderAccountModal();
  }));
  document.getElementById("acc-form").addEventListener("submit", submitAccount);
}

async function submitAccount(event) {
  event.preventDefault();
  const dict = t();
  const username = document.getElementById("acc-user").value.trim();
  const password = document.getElementById("acc-pass").value;
  const signup = state.accountMode === "signup";
  if (signup && !/^[A-Za-z0-9_]{3,20}$/.test(username)) {
    state.accountMsg = { kind: "error", text: dict.accErr.bad_username };
    renderAccountModal();
    document.getElementById("acc-user").value = username;
    return;
  }
  if (signup && password.length < 8) {
    state.accountMsg = { kind: "error", text: dict.accErr.weak_password };
    renderAccountModal();
    document.getElementById("acc-user").value = username;
    return;
  }
  state.accountBusy = true;
  renderAccountModal();
  try {
    const { response, data } = await api(signup ? "/api/auth/signup" : "/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    state.accountBusy = false;
    if (!response.ok || !data.ok) {
      state.accountMsg = { kind: "error", text: accErrText(data.code, data.error) };
      renderAccountModal();
      document.getElementById("acc-user").value = username;
      return;
    }
    finishLogin(data);
  } catch (_) {
    state.accountBusy = false;
    state.accountMsg = { kind: "error", text: dict.accErr.network };
    renderAccountModal();
  }
}

async function logout() {
  try {
    const { data } = await api("/api/auth/logout", { method: "POST", body: "{}" });
    setBalance(data.ok ? data : { account: null, credits: 0, freeAvailable: false });
  } catch (_) { /* ignore */ }
  state.account = null;
  renderAccountButton();
  renderBalance();
  // Shared device: don't leave the saved birthday in the form.
  document.getElementById("birthDate").value = "";
  document.getElementById("birthTime").value = "";
  closeAccountModal();
  toast(t().accLoggedOut);
}

async function changePassword(event) {
  event.preventDefault();
  const dict = t();
  const current = document.getElementById("acc-cur").value;
  const next = document.getElementById("acc-new").value;
  if (next.length < 8) {
    state.accountMsg = { kind: "error", text: dict.accErr.weak_password };
    renderAccountModal();
    return;
  }
  const { response, data } = await api("/api/auth/password", {
    method: "POST",
    body: JSON.stringify({ current, new: next }),
  });
  state.accountMsg = response.ok && data.ok
    ? { kind: "ok", text: dict.accPwChanged }
    : { kind: "error", text: accErrText(data.code, data.error) };
  renderAccountModal();
}

function setupAccount() {
  const modal = document.getElementById("account-modal");
  document.getElementById("account-btn").addEventListener("click", () => openAccountModal(state.account ? null : "login"));
  document.getElementById("account-close-x").addEventListener("click", closeAccountModal);
  modal.addEventListener("click", (event) => { if (event.target === modal) closeAccountModal(); });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) closeAccountModal();
  });
  renderAccountButton();
}

async function loadAuthConfig() {
  try {
    const { response, data } = await api("/api/auth/config");
    if (response.ok && data.ok) {
      state.authMode = data.mode === "google" && data.googleClientId ? "google" : "password";
      state.googleClientId = data.googleClientId || null;
      renderGate();
      if (state.authMode === "google") loadGis(); // warm up so the button appears instantly
      const modal = document.getElementById("account-modal");
      if (modal && !modal.hidden) renderAccountModal();
    }
  } catch (_) { /* keep password mode */ }
}

function setup() {
  const dateInput = document.getElementById("birthDate");
  dateInput.max = new Date().toISOString().slice(0, 10);
  const afterGate = () => {
    document.getElementById("oracle").scrollIntoView({ behavior: "smooth", block: "start" });
    const name = document.getElementById("name");
    setTimeout(() => (name.value ? document.getElementById("question") : name).focus({ preventScroll: true }), 400);
  };
  document.getElementById("gate-signup").addEventListener("click", () => {
    openAccountModal("signup", null);
    state.afterLogin = afterGate;
  });
  document.getElementById("gate-login").addEventListener("click", () => {
    openAccountModal("login", null);
    state.afterLogin = afterGate;
  });
  document.getElementById("hero-signup").addEventListener("click", () => {
    if (state.account) document.getElementById("oracle").scrollIntoView({ behavior: "smooth", block: "start" });
    else {
      openAccountModal("signup", t().accNeedLoginAsk);
      state.afterLogin = afterGate;
    }
  });
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => setLang(btn.dataset.lang));
  });
  document.getElementById("reading-form").addEventListener("submit", onSubmit);
  const detailsBox = document.getElementById("details");
  const detailsCount = document.getElementById("details-count");
  const syncCount = () => { detailsCount.textContent = `${detailsBox.value.length}/500`; };
  detailsBox.addEventListener("input", syncCount);
  syncCount();
  setupPricing();
  setupAccount();
  loadAuthConfig();
  applyLang();
  paintStars();
  loadPackages();
  checkOrders();
}

setup();
