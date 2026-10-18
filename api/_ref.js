// Order numbers: "MG" + digits. A missing or foreign ref gets a fresh one.
module.exports = function orderRef(v) {
  const r = String(v || "").toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 20);
  return /^MG\d{5,18}$/.test(r) ? r : "MG" + Date.now().toString().slice(-7);
};
