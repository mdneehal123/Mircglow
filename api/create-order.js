// POST /api/create-order: works out the amount on the server and creates a Razorpay order.
const { price } = require("./_pricing");
const { enabled, keyId, rz, readJson, send } = require("./_razorpay");

module.exports = async (req, res) => {
  if (req.method !== "POST") return send(res, 405, { error: "Use POST" });
  if (!enabled()) return send(res, 503, { error: "Online payment is not switched on yet." });
  const body = await readJson(req);
  let q;
  try { q = price(body.items, "online", body.coupon); } catch (e) { return send(res, 400, { error: e.message }); }
  const ref = String(body.ref || "").replace(/[^A-Z0-9]/gi, "").slice(0, 20);
  try {
    const order = await rz("/orders", {
      amount: q.total * 100, currency: "INR", receipt: ref || undefined,
      notes: { site: "mircglow.com", ref, items: q.lines.map(l => `${l.name} x${l.qty}`).join(", ").slice(0, 250), coupon: q.coupon },
    });
    send(res, 200, { orderId: order.id, amount: order.amount, currency: "INR", keyId: keyId(), total: q.total });
  } catch (e) {
    send(res, 502, { error: "Could not start the payment. Please try again or choose Cash on Delivery." });
  }
};
