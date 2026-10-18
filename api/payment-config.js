// GET /api/payment-config — tells the checkout which services are switched on.
const { enabled, keyId, send } = require("./_razorpay");
const { delhiveryOn } = require("./_delhivery");
module.exports = (req, res) => send(res, 200, { enabled: enabled(), keyId: enabled() ? keyId() : "", cod: delhiveryOn() });
