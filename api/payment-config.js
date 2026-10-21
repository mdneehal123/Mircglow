// GET /api/payment-config: tells the checkout which services are switched on (no secrets).
const { enabled, keyId, send } = require("./_razorpay");
const { delhiveryOn } = require("./_delhivery");
const { deskOn } = require("./_orderdesk");
const { PREPAID_PCT } = require("./_pricing");
module.exports = (req, res) => send(res, 200, { online: enabled(), keyId: enabled() ? keyId() : "", cod: delhiveryOn() || deskOn(), delhivery: delhiveryOn(), orderdesk: deskOn(), prepaidPct: PREPAID_PCT });
