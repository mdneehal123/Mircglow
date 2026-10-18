// Server-side prices: the single source of truth for what a customer is charged online.
// The product table (_products.json) is written by build.py from the PRODUCTS list, the same
// list the product pages are built from, so the website and the checkout can never disagree.
const CATALOG = require("./_products.json");
const PRODUCTS = CATALOG.products;
// Order Desk product IDs and jars per pack (for parcel weight)
const DESK_ID = Object.fromEntries(Object.entries(PRODUCTS).map(([k, p]) => [k, p.desk || ""]));
const UNITS = Object.fromEntries(Object.entries(PRODUCTS).map(([k, p]) => [k, p.units || 1]));
// Coupons (GLOW10: 10% off, as advertised across the site) also come from build.py.
const COUPONS = CATALOG.coupons || {};
const SHIPPING = 0; // free shipping across India

function price(items, couponCode) {
  if (!Array.isArray(items) || !items.length || items.length > 10) throw new Error("Your cart is empty.");
  const lines = items.map(l => {
    const p = Object.prototype.hasOwnProperty.call(PRODUCTS, l && l.id) ? PRODUCTS[l.id] : null;
    const qty = Math.floor(Number(l && l.qty));
    if (!p || !(qty >= 1 && qty <= 20)) throw new Error("A product in your cart is not available.");
    return { id: l.id, name: p.sold, qty, price: p.price, total: p.price * qty };
  });
  const sub = lines.reduce((a, l) => a + l.total, 0);
  const code = String(couponCode || "").trim().toUpperCase();
  const c = Object.prototype.hasOwnProperty.call(COUPONS, code) ? COUPONS[code] : null;
  let coup = 0;
  if (c && sub >= c.min) coup = Math.round(c.type === "pct" ? (sub * c.value) / 100 : c.value);
  const total = Math.round(sub - coup + SHIPPING);
  return { lines, sub, coupon: coup ? code : "", discount: coup, total, units: lines.reduce((a, l) => a + l.qty * (UNITS[l.id] || 1), 0) };
}
module.exports = { price, DESK_ID, COUPONS };
