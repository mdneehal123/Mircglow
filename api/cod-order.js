// POST /api/cod-order: Cash on Delivery. Prices the order on the server and books it with Delhivery.
// Every COD order is also saved in the Order Desk; if Delhivery booking fails, the order is still saved there to book by hand.
const { price } = require("./_pricing");
const { customer } = require("./_shared");
const { delhiveryOn, serviceable, createShipment } = require("./_delhivery");
const { pushToDesk, deskOn } = require("./_orderdesk");
const { readJson, send } = require("./_razorpay");

module.exports = async (req, res) => {
  if (req.method !== "POST") return send(res, 405, { error: "Use POST" });
  if (!delhiveryOn() && !deskOn()) return send(res, 503, { error: "Cash on Delivery is not switched on yet." });
  const b = await readJson(req);
  if (b.website) return send(res, 200, { ok: true }); // hidden field only bots fill in
  let q, c;
  try { q = price(b.items, "cod", b.coupon); c = customer(b.customer); } catch (e) { return send(res, 400, { error: e.message }); }
  const ref = String(b.ref || "").replace(/[^A-Z0-9]/gi, "").slice(0, 20) || "MG" + Date.now().toString(36).toUpperCase();
  let d = { ok: false, error: "Delhivery not set up" };
  if (delhiveryOn()) {
    try {
      const s = await serviceable(c.pin);
      if (s.known && !s.cod) return send(res, 409, { error: "Cash on Delivery isn't available for pin code " + c.pin + ". Please pay online instead.", codUnavailable: true });
    } catch (e) { /* if the check fails, still try to book */ }
    try { d = await createShipment({ ref, c, q, pay: "cod" }); } catch (e) { d = { ok: false, error: String(e.message || e) }; }
  }
  const desk = await pushToDesk(d.ok
    ? { ref, c, q, pay: "cod", paid: false, courier: "Delhivery", awb: d.awb, note: `COD booked with Delhivery · AWB ${d.awb} · print the label from the Delhivery panel` }
    : { ref, c, q, pay: "cod", paid: false, note: "⚠ COD website order, not booked with Delhivery (" + d.error + "). Please book it by hand." });
  if (!d.ok && !desk.ok) {
    console.error("COD order NOT saved", JSON.stringify({ ref, name: c.name, phone: c.phone, pin: c.pin, items: q.lines.map(l => l.id + "x" + l.qty), total: q.total, delhivery: d.error, desk: desk.error }));
    return send(res, 502, { error: "We could not place your order just now. Please try again, or order on WhatsApp." });
  }
  if (d.ok) return send(res, 200, { ok: true, ref, awb: d.awb, courier: "Delhivery", total: q.total, savedToDesk: desk.ok, trackUrl: "https://www.delhivery.com/track/package/" + d.awb });
  return send(res, 200, { ok: true, ref, awb: "", courier: "", total: q.total, pending: true, savedToDesk: desk.ok });
};
