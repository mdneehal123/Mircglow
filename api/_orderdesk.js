// Sends a website order into the Order Desk inbox (server to server, protected by WEB_ORDER_KEY).
const { DESK_ID } = require("./_pricing");
const deskUrl = () => (process.env.ORDERDESK_URL || "https://www.skinday.shop").replace(/\/+$/, "");
const deskOn = () => Boolean(process.env.WEB_ORDER_KEY);

async function pushToDesk({ ref, c, q, pay, paid, payId, courier, awb, note }) {
  if (!deskOn()) return { ok: false, error: "WEB_ORDER_KEY not set" };
  const body = {
    ref, src: "web", site: "mircglow.com", brand: "mg", pay, paid: Boolean(paid), payId: payId || "",
    total: q.total, sub: q.sub, disc: q.discount, coupon: q.coupon, courier: courier || "", awb: awb || "", note: note || "",
    name: c.name, phone: c.phone, email: c.email, house: c.address, area: c.city, landmark: c.landmark, pin: c.pin, city: c.city, state: c.state,
    items: q.lines.map(l => [DESK_ID[l.id] || "", l.name, l.qty, l.price]),
  };
  try {
    const r = await fetch(deskUrl() + "/api/web-order", {
      method: "POST", headers: { "Content-Type": "application/json", "x-web-order-key": process.env.WEB_ORDER_KEY }, body: JSON.stringify(body),
    });
    const j = await r.json().catch(() => ({}));
    return r.ok && j.ok ? { ok: true, id: j.id } : { ok: false, error: j.error || "Order Desk HTTP " + r.status };
  } catch (e) { return { ok: false, error: String(e.message || e) }; }
}
module.exports = { pushToDesk, deskOn };
