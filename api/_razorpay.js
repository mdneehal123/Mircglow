const crypto = require("crypto");
const keyId = () => process.env.RAZORPAY_KEY_ID || "";
const secret = () => process.env.RAZORPAY_KEY_SECRET || "";
const enabled = () => Boolean(keyId() && secret());

async function rz(path, body) {
  const res = await fetch("https://api.razorpay.com/v1" + path, {
    method: body ? "POST" : "GET",
    headers: { "Content-Type": "application/json", Authorization: "Basic " + Buffer.from(keyId() + ":" + secret()).toString("base64") },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((data.error && data.error.description) || "Payment service error");
  return data;
}

function validSignature(orderId, paymentId, signature) {
  const expected = crypto.createHmac("sha256", secret()).update(orderId + "|" + paymentId).digest("hex");
  const a = Buffer.from(expected), b = Buffer.from(String(signature || ""));
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function readJson(req) {
  if (req.body && typeof req.body === "object") return Promise.resolve(req.body);
  return new Promise(resolve => {
    let s = ""; req.on("data", c => { s += c; if (s.length > 20000) req.destroy(); });
    req.on("end", () => { try { resolve(JSON.parse(s || "{}")); } catch { resolve({}); } });
  });
}
function send(res, status, obj) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(obj));
}
module.exports = { keyId, enabled, rz, validSignature, readJson, send };
