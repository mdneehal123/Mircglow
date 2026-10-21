// Server-side prices: the single source of truth for what a customer is charged.
// _catalog.json is written by build.py from the same product list the website shows, so prices can never drift.
const CAT = require("./_catalog.json");
const PRODUCTS = CAT.products;
const PREPAID_PCT = Number(CAT.prepaidPct) || 0;
const COUPONS = CAT.coupons || {};   // e.g. {"GLOW10": 10} = 10% off

// mode "online": prepaid discount applies. mode "cod": full price, paid at the door.
function price(items, mode = "online", couponCode = "") {
  if (!Array.isArray(items) || !items.length || items.length > 10) throw new Error("Your cart is empty.");
  const lines = items.map(l => {
    const p = PRODUCTS[l && l.id];
    const qty = Math.floor(Number(l && l.qty));
    if (!p || !(qty >= 1 && qty <= 10)) throw new Error("A product in your cart is not available.");
    return { id: l.id, name: p.name, qty, price: p.price, total: p.price * qty, desk: p.desk, jars: p.jars };
  });
  const sub = lines.reduce((a, l) => a + l.total, 0);
  const code = String(couponCode || "").toUpperCase().trim();
  const coupOff = COUPONS[code] ? Math.round((sub * COUPONS[code]) / 100) : 0;
  const prepaidOff = mode === "online" ? Math.round(((sub - coupOff) * PREPAID_PCT) / 100) : 0;
  const discount = coupOff + prepaidOff;
  return { lines, sub, coupon: coupOff ? code : "", coupOff, prepaidOff, discount, total: sub - discount, units: lines.reduce((a, l) => a + l.qty * (l.jars || 1), 0) };
}
module.exports = { price, PREPAID_PCT, COUPONS };
