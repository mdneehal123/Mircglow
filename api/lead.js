const { pushLead } = require("./_orderdesk");

// A shopper who ticked "You may message me on WhatsApp..." at checkout. Only then is the number sent to the shop's private
// Order Desk. Never blocks checkout: the browser ignores the answer.
const seen = new Map(); // phone -> [timestamps], per server instance (light protection against floods)
let globalHits = [];
const clean = (v, n) => String(v == null ? "" : v).replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);

module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ ok: false });
  let b = req.body || {};
  if (typeof b === "string") { try { b = JSON.parse(b); } catch (e) { b = {}; } }
  const phone = String(b.phone || "").replace(/\D/g, "").slice(-10);
  if (b.consent !== true || b.website || !/^[6-9]\d{9}$/.test(phone)) return res.status(200).json({ ok: true });
  const now = Date.now(), hour = 3600e3;
  globalHits = globalHits.filter(t => now - t < hour);
  const mine = (seen.get(phone) || []).filter(t => now - t < hour);
  if (globalHits.length >= 300 || mine.length >= 5) return res.status(200).json({ ok: true });
  mine.push(now); globalHits.push(now); seen.set(phone, mine);
  if (seen.size > 2000) seen.clear();
  try { await pushLead({ phone, name: clean(b.name, 80), product: clean(b.product, 120) }); } catch (e) { /* never blocks checkout */ }
  return res.status(200).json({ ok: true });
};
