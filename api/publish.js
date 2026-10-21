// Daily publish, run by Vercel Cron (see "crons" in vercel.json). No GitHub activity at all.
// 1. Starts a fresh Vercel build through a Deploy Hook. The build runs build.py with today's India date,
//    so pages in content/plan/schedule.json go live on their date.
// 2. Tells IndexNow (Bing, Yandex and others) about the pages that go live today.
// Needs two Vercel environment variables: DEPLOY_HOOK_URL (Settings > Git > Deploy Hooks) and CRON_SECRET (any long random text).
const schedule = require("../content/plan/schedule.json");
const SITE = "https://mircglow.com";
const INDEXNOW_KEY = "74d314fcd13a092ae512fe4c12566f9f";

function todayIST() {
  return new Date(Date.now() + 5.5 * 3600 * 1000).toISOString().slice(0, 10);
}

module.exports = async function handler(req, res) {
  const send = (code, obj) => { res.statusCode = code; res.setHeader("Content-Type", "application/json"); res.setHeader("Cache-Control", "no-store"); res.end(JSON.stringify(obj)); };
  const secret = (process.env.CRON_SECRET || "").trim();
  if (!secret) return send(503, { ok: false, error: "Set CRON_SECRET in Vercel." });
  if ((req.headers.authorization || "") !== "Bearer " + secret) return send(401, { ok: false, error: "Not allowed." });
  const hook = (process.env.DEPLOY_HOOK_URL || "").trim();
  if (!/^https:\/\/api\.vercel\.com\//.test(hook)) return send(503, { ok: false, error: "Set DEPLOY_HOOK_URL in Vercel." });

  const out = { ok: true, date: todayIST() };
  try {
    const r = await fetch(hook, { method: "POST" });
    out.build = r.ok ? "started" : "failed " + r.status;
    if (!r.ok) out.ok = false;
  } catch (e) { out.ok = false; out.build = "failed " + String(e && e.message || e); }

  const urls = schedule.filter(m => m.date === out.date).map(m => `${SITE}/${m.slug}/`);
  out.newPages = urls;
  if (urls.length) {
    urls.push(SITE + "/sitemap.xml");
    try {
      const r = await fetch("https://api.indexnow.org/indexnow", { method: "POST", headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify({ host: "mircglow.com", key: INDEXNOW_KEY, keyLocation: `${SITE}/${INDEXNOW_KEY}.txt`, urlList: urls }) });
      out.indexnow = r.status;
    } catch (e) { out.indexnow = "failed"; }
  }
  return send(out.ok ? 200 : 502, out);
};
