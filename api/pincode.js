// GET /api/pincode?pin=575001: city/state and whether Cash on Delivery is available (Delhivery lookup; books nothing).
const { delhiveryOn, serviceable } = require("./_delhivery");
const { send } = require("./_razorpay");
const STATES = { AN:"Andaman and Nicobar Islands", AP:"Andhra Pradesh", AR:"Arunachal Pradesh", AS:"Assam", BR:"Bihar", CH:"Chandigarh", CT:"Chhattisgarh", CG:"Chhattisgarh",
  DN:"Dadra and Nagar Haveli and Daman and Diu", DD:"Dadra and Nagar Haveli and Daman and Diu", DL:"Delhi", GA:"Goa", GJ:"Gujarat", HR:"Haryana", HP:"Himachal Pradesh",
  JK:"Jammu and Kashmir", JH:"Jharkhand", KA:"Karnataka", KL:"Kerala", LA:"Ladakh", LD:"Lakshadweep", MP:"Madhya Pradesh", MH:"Maharashtra", MN:"Manipur", ML:"Meghalaya",
  MZ:"Mizoram", NL:"Nagaland", OR:"Odisha", OD:"Odisha", PY:"Puducherry", PB:"Punjab", RJ:"Rajasthan", SK:"Sikkim", TN:"Tamil Nadu", TG:"Telangana", TS:"Telangana",
  TR:"Tripura", UP:"Uttar Pradesh", UT:"Uttarakhand", UK:"Uttarakhand", WB:"West Bengal" };
module.exports = async (req, res) => {
  const pin = String((req.query && req.query.pin) || new URL(req.url, "http://x").searchParams.get("pin") || "").replace(/\D/g, "");
  if (!/^[1-9]\d{5}$/.test(pin)) return send(res, 400, { error: "Enter a 6-digit pin code." });
  if (!delhiveryOn()) return send(res, 200, { known: false });
  try { const s = await serviceable(pin); if (s.state && STATES[s.state.toUpperCase()]) s.state = STATES[s.state.toUpperCase()]; res.setHeader && res.setHeader("Cache-Control", "public, max-age=86400"); return send(res, 200, s); }
  catch (e) { return send(res, 200, { known: false }); }
};
