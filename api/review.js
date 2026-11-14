// A customer review from the product page form. Checked here, then sent to the private Order Desk,
// where it waits as "pending" until the owner approves it. Nothing is published automatically.
const seen = new Map(); let globalHits = [];
const clean = (v, n) => String(v == null ? "" : v).replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);
const catalog = require("./_catalog.json");
module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ ok: false });
  let b = req.body || {}; if (typeof b === "string") { try { b = JSON.parse(b); } catch (e) { b = {}; } }
  if (b.website) return res.status(200).json({ ok: true }); // honeypot
  const rating = Math.round(Number(b.rating)), text = clean(b.text, 1200), name = clean(b.name, 40), city = clean(b.city, 40);
  const product = clean(b.product, 80).replace(/[^a-z0-9-]/g, "");
  const item = (catalog.products || {})[product];
  if (!(rating >= 1 && rating <= 5)) return res.status(400).json({ ok: false, error: "Please choose a star rating." });
  if (text.length < 10) return res.status(400).json({ ok: false, error: "Please write a few more words (at least 10 letters)." });
  if (name.length < 2) return res.status(400).json({ ok: false, error: "Please add your first name." });
  if (!item) return res.status(400).json({ ok: false, error: "Unknown product." });
  if (/https?:\/\/|www\./i.test(text)) return res.status(400).json({ ok: false, error: "Please remove links from your review." });
  const ip = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim() || "x";
  const now = Date.now(), hour = 3600e3;
  globalHits = globalHits.filter(t => now - t < hour); const mine = (seen.get(ip) || []).filter(t => now - t < hour);
  if (globalHits.length >= 200 || mine.length >= 4) return res.status(429).json({ ok: false, error: "Too many reviews from this connection. Please try again later." });
  mine.push(now); globalHits.push(now); seen.set(ip, mine); if (seen.size > 2000) seen.clear();
  const key = (process.env.WEB_ORDER_KEY || "").trim(); if (!key) return res.status(503).json({ ok: false, error: "Reviews are not switched on yet." });
  const desk = (process.env.ORDERDESK_URL || "https://www.skinday.shop").replace(/\/+$/, "");
  try {
    const r = await fetch(desk + "/api/web-order", { method: "POST", headers: { "Content-Type": "application/json", "x-web-order-key": key },
      body: JSON.stringify({ review: true, site: "mircglow.com", product, productName: item.name || product, rating, text, name, city, phone: String(b.phone || "").replace(/\D/g, "").slice(-10) }) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || !j.ok) return res.status(502).json({ ok: false, error: "Could not send your review. Please try again." });
    return res.status(200).json({ ok: true });
  } catch (e) { return res.status(502).json({ ok: false, error: "Could not send your review. Please try again." }); }
};
