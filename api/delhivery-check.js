// GET /api/delhivery-check — confirms the Delhivery token works (pin code lookup only; books nothing, shows no secrets).
const { delhiveryOn, serviceable } = require("./_delhivery");
const { send } = require("./_razorpay");
module.exports = async (req, res) => {
  const pickup = process.env.DELHIVERY_PICKUP || "";
  const out = { on: delhiveryOn(), env: process.env.DELHIVERY_ENV === "staging" ? "staging" : "live", pickupNameLength: pickup.length,
    pickupHasExtraSpaces: pickup !== pickup.trim(), tokenLength: (process.env.DELHIVERY_TOKEN || "").length };
  if (!out.on) return send(res, 200, out);
  try { const s = await serviceable("581320"); out.tokenWorks = s.known; out.sample = { pin: "581320", cod: s.cod, prepaid: s.prepaid }; }
  catch (e) { out.tokenWorks = false; out.error = String(e.message || e).slice(0, 200); }
  send(res, 200, out);
};
