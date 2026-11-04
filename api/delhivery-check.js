// GET /api/delhivery-check — confirms the Delhivery token works (pin code lookup only; books nothing, shows no secrets).
const { delhiveryOn, serviceable } = require("./_delhivery");
const { send } = require("./_razorpay");
module.exports = async (req, res) => {
  const pickup = process.env.DELHIVERY_PICKUP || "";
  const out = { on: delhiveryOn(), env: process.env.DELHIVERY_ENV === "staging" ? "staging" : "live", pickupNameLength: pickup.length,
    pickupHasExtraSpaces: pickup !== pickup.trim(), tokenLength: (process.env.DELHIVERY_TOKEN || "").length };
  if (!out.on) return send(res, 200, out);
  // TEMPORARY (remove before merge): ?pin=600044 shows Delhivery's raw pin code record. Books nothing, shows no secrets.
  const rawPin = String(new URL(req.url, "http://x").searchParams.get("pin") || "").replace(/\D/g, "");
  if (/^[1-9]\d{5}$/.test(rawPin)) {
    try {
      const base = process.env.DELHIVERY_ENV === "staging" ? "https://staging-express.delhivery.com" : "https://track.delhivery.com";
      const r = await fetch(base + "/c/api/pin-codes/json/?filter_codes=" + rawPin, { headers: { Authorization: "Token " + process.env.DELHIVERY_TOKEN, Accept: "application/json" }, signal: AbortSignal.timeout(8000) });
      out.httpStatus = r.status; out.raw = await r.json().catch(() => null);
    } catch (e) { out.error = String(e.message || e).slice(0, 200); }
    res.setHeader && res.setHeader("Cache-Control", "no-store");
    return send(res, 200, out);
  }
  try { const s = await serviceable("581320"); out.tokenWorks = s.known; out.sample = { pin: "581320", cod: s.cod, prepaid: s.prepaid }; }
  catch (e) { out.tokenWorks = false; out.error = String(e.message || e).slice(0, 200); }
  send(res, 200, out);
};
