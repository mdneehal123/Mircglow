// Sends a website order into the Order Desk inbox (server to server, protected by WEB_ORDER_KEY).
// The Order Desk keeps one entry per order number, so sending the same order twice never makes a duplicate.
const deskUrl = () => (process.env.ORDERDESK_URL || "https://www.skinday.shop").replace(/\/+$/, "");
const deskOn = () => Boolean((process.env.WEB_ORDER_KEY || "").trim());

async function pushToDesk({ ref, c, q, pay, paid, payId, courier, awb, note }) {
  if (!deskOn()) return { ok: false, error: "WEB_ORDER_KEY not set" };
  const body = {
    ref, src: "web", site: "mircglow.com", brand: "mg", pay, paid: Boolean(paid), payId: payId || "",
    total: q.total, sub: q.sub, disc: q.discount, coupon: q.coupon || "", courier: courier || "", awb: awb || "", note: note || "",
    name: c.name, phone: c.phone, email: c.email, house: c.address, area: c.city, landmark: c.landmark, pin: c.pin, city: c.city, state: c.state,
    items: q.lines.map(l => [l.desk || l.id, l.name, l.qty, l.price]),
  };
  try {
    const r = await fetch(deskUrl() + "/api/web-order", {
      method: "POST", headers: { "Content-Type": "application/json", "x-web-order-key": process.env.WEB_ORDER_KEY.trim() }, body: JSON.stringify(body),
    });
    const j = await r.json().catch(() => ({}));
    return r.ok && j.ok ? { ok: true, id: j.id } : { ok: false, error: j.error || "Order Desk HTTP " + r.status };
  } catch (e) { return { ok: false, error: String(e.message || e) }; }
}
// A shopper who ticked the consent box at checkout: goes to Order Desk > Customers > Not bought yet.
async function pushLead({ phone, name, product }) {
  if (!deskOn()) return { ok: false };
  try {
    const r = await fetch(deskUrl() + "/api/web-order", {
      method: "POST", headers: { "Content-Type": "application/json", "x-web-order-key": process.env.WEB_ORDER_KEY.trim() },
      body: JSON.stringify({ lead: true, consent: true, phone, name: name || "", product: product || "", site: "mircglow.com" }),
    });
    return { ok: r.ok };
  } catch (e) { return { ok: false }; }
}
module.exports = { pushToDesk, pushLead, deskOn };
