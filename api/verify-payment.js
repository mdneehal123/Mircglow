// POST /api/verify-payment: confirms with Razorpay that the payment is real, checks the amount
// against the server price, then puts the paid order into the Order Desk.
const { price } = require("./_pricing");
const { customer } = require("./_shared");
const { pushToDesk } = require("./_orderdesk");
const { enabled, rz, validSignature, readJson, send } = require("./_razorpay");

module.exports = async (req, res) => {
  if (req.method !== "POST") return send(res, 405, { error: "Use POST" });
  if (!enabled()) return send(res, 503, { error: "Online payment is not switched on." });
  const b = await readJson(req);
  const { razorpay_order_id: orderId, razorpay_payment_id: paymentId, razorpay_signature: sig } = b;
  if (!orderId || !paymentId || !validSignature(orderId, paymentId, sig)) return send(res, 400, { ok: false, error: "Payment could not be verified." });
  let p;
  try { p = await rz("/payments/" + encodeURIComponent(paymentId)); }
  catch (e) { return send(res, 502, { ok: false, error: "Could not confirm the payment. If money was deducted, message us on WhatsApp." }); }
  const ok = p.order_id === orderId && (p.status === "captured" || p.status === "authorized");
  if (!ok) return send(res, 400, { ok: false, error: "Payment was not completed.", status: p.status });

  const out = { ok: true, paymentId, status: p.status, amount: p.amount / 100, method: p.method, savedToDesk: false };
  try {
    const q = price(b.items, "online", b.coupon); const c = customer(b.customer);
    const ref = String(b.ref || (p.notes && p.notes.ref) || "").replace(/[^A-Z0-9]/gi, "").slice(0, 20);
    const match = q.total * 100 === p.amount;
    const desk = await pushToDesk({ ref, c, q: { ...q, total: p.amount / 100 }, pay: "upi", paid: true, payId: paymentId,
      note: `Paid online via Razorpay (${p.method || "online"}) ${paymentId}` + (match ? "" : ` ⚠ amount ₹${p.amount / 100} differs from cart ₹${q.total}`) });
    out.savedToDesk = desk.ok;
    if (!desk.ok) console.error("order desk push failed", ref, desk.error);
  } catch (e) { out.deskError = e.message; console.error("paid order not saved to desk", e.message); }
  send(res, 200, out);
};
