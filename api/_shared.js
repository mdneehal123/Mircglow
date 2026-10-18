// Customer details from checkout, cleaned the same way the Order Desk form cleans them.
const clean = (v, n) => String(v == null ? "" : v).replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);
function customer(c) {
  c = c || {};
  const f = {
    name: clean(c.name, 80), phone: String(c.phone || "").replace(/\D/g, "").slice(-10), email: clean(c.email, 120),
    address: clean(c.address, 220), landmark: clean(c.landmark, 120), city: clean(c.city, 60), state: clean(c.state, 60),
    pin: String(c.pin || "").replace(/\D/g, ""),
  };
  const errs = [];
  if (f.name.length < 2) errs.push("name");
  if (!/^[6-9]\d{9}$/.test(f.phone)) errs.push("10-digit mobile number");
  if (f.address.length < 8) errs.push("full address");
  if (!/^[1-9]\d{5}$/.test(f.pin)) errs.push("6-digit pin code");
  if (errs.length) throw new Error("Please check: " + errs.join(", ") + ".");
  return f;
}
module.exports = { customer, clean };
