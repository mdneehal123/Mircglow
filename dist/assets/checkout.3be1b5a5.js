/* Mirc Glow checkout: cart, address, Pay online (Razorpay) or Cash on Delivery (Delhivery), WhatsApp fallback.
   Prices shown here are for display only; the server works out the amount to charge from api/_catalog.json. */
function mgCheckout() {
  var D = JSON.parse(document.getElementById("co-data").textContent);
  var P = D.products, $ = function (s) { return document.querySelector(s); };
  var cfg = { online: false, cod: false, prepaidPct: D.prepaidPct }, coupon = "", busy = false;
  var inr = function (n) { return "₹" + Math.round(n).toLocaleString("en-IN"); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  function cart() { return MGCart.get().filter(function (l) { return P[l.id] && l.qty > 0; }); }

  function totals(mode) {
    var sub = cart().reduce(function (a, l) { return a + P[l.id].price * l.qty; }, 0);
    var cOff = D.coupons[coupon] ? Math.round(sub * D.coupons[coupon] / 100) : 0;
    var pOff = mode === "online" ? Math.round((sub - cOff) * cfg.prepaidPct / 100) : 0;
    return { sub: sub, cOff: cOff, pOff: pOff, total: sub - cOff - pOff };
  }
  function mode() { var r = document.querySelector('input[name="pay"]:checked'); return r ? r.value : ""; }

  function render() {
    var c = cart(), box = $("[data-co-lines]");
    if (!c.length) {
      $("[data-co-main]").hidden = true; $("[data-co-empty]").hidden = false; return;
    }
    box.innerHTML = c.map(function (l) {
      var p = P[l.id];
      return '<div class="co-line"><img src="' + esc(p.img) + '" alt="" width="64" height="64"><div><b>' + esc(p.name) + '</b><small>' + esc(p.size) + ' · ' + inr(p.price) + ' each</small><div>' +
        '<span class="co-q"><button type="button" data-q="-1" data-id="' + esc(l.id) + '" aria-label="One less">−</button><span>' + l.qty + '</span><button type="button" data-q="1" data-id="' + esc(l.id) + '" aria-label="One more">+</button></span>' +
        '<button type="button" class="co-rm" data-rm="' + esc(l.id) + '">Remove</button></div></div><span class="co-pr">' + inr(p.price * l.qty) + '</span></div>';
    }).join("");
    var m = mode(), t = totals(m || "cod");
    var rows = '<span>Subtotal</span><span>' + inr(t.sub) + '</span>';
    if (t.cOff) rows += '<span>Code ' + esc(coupon) + '</span><span class="off">−' + inr(t.cOff) + '</span>';
    if (t.pOff) rows += '<span>Online payment ' + cfg.prepaidPct + '% off</span><span class="off">−' + inr(t.pOff) + '</span>';
    rows += '<span>Shipping</span><span class="off">FREE</span><span class="tot">Total</span><span class="tot">' + inr(t.total) + '</span>';
    $("[data-co-sum]").innerHTML = rows;
    var on = totals("online").total;
    $("[data-pay-online-note]").textContent = cfg.prepaidPct ? "UPI, cards, net banking · pay " + inr(on) + " (" + cfg.prepaidPct + "% off)" : "UPI, cards, net banking";
    $("[data-pay-cod-note]").textContent = "Pay " + inr(totals("cod").total) + " in cash or UPI when it arrives";
    var go = $("[data-co-go]");
    go.textContent = m === "online" ? "Pay " + inr(t.total) + " securely" : m === "cod" ? "Place order · " + inr(t.total) + " on delivery" : "Send order on WhatsApp";
    $("[data-co-wa]").href = waLink();
  }

  function form() {
    var f = $("#co-form"), v = function (n) { return (f.elements[n].value || "").trim(); };
    return { name: v("name"), phone: v("phone").replace(/\D/g, "").slice(-10), email: v("email"), address: v("address"), landmark: v("landmark"), pin: v("pin").replace(/\D/g, ""), city: v("city"), state: v("state") };
  }
  function check(c) {
    var bad = [];
    if (c.name.length < 2) bad.push("name");
    if (!/^[6-9]\d{9}$/.test(c.phone)) bad.push("10-digit mobile number");
    if (c.address.length < 8) bad.push("full address (house no., street, area)");
    if (!/^[1-9]\d{5}$/.test(c.pin)) bad.push("6-digit pin code");
    if (!c.city) bad.push("city");
    return bad.length ? "Please fill in your " + bad.join(", ") + "." : "";
  }
  function msg(t, kind) { var m = $("[data-co-msg]"); m.textContent = t; m.className = "co-msg " + (kind || ""); }
  function waLink() {
    var c = form(), t = totals(mode() === "online" ? "online" : "cod");
    var lines = cart().map(function (l) { return "• " + l.qty + " x " + P[l.id].name + " (" + P[l.id].size + ") – " + inr(P[l.id].price * l.qty); }).join("\n");
    var txt = "Hi Mirc Glow, I'd like to order:\n" + lines + (coupon ? "\nCode: " + coupon : "") + "\nTotal: " + inr(t.total) + "\n\nName: " + c.name + "\nPhone: " + c.phone +
      "\nAddress: " + [c.address, c.landmark, c.city, c.state, c.pin].filter(Boolean).join(", ") + "\nPayment: " + (mode() === "online" ? "pay online" : "Cash on Delivery");
    return "https://wa.me/" + D.wa + "?text=" + encodeURIComponent(txt);
  }
  function save() { try { localStorage.setItem("mg_addr", JSON.stringify(form())); } catch (e) {} }
  function restore() {
    try { var a = JSON.parse(localStorage.getItem("mg_addr") || "null"); if (!a) return; var f = $("#co-form");
      ["name", "phone", "email", "address", "landmark", "pin", "city", "state"].forEach(function (k) { if (a[k] && !f.elements[k].value) f.elements[k].value = a[k]; }); } catch (e) {}
  }
  function done(o) {
    try { sessionStorage.setItem("mg_last_order", JSON.stringify(o)); } catch (e) {}
    MGCart.set([]); location.href = "/order-success/";
  }
  function ref() { return "MG" + Date.now().toString(36).toUpperCase().slice(-7) + Math.floor(Math.random() * 36).toString(36).toUpperCase(); }
  function api(path, body) {
    return fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { j._status = r.status; return j; }); });
  }
  function rzLoad() {
    if (window.Razorpay) return Promise.resolve();
    return new Promise(function (ok, fail) { var s = document.createElement("script"); s.src = "https://checkout.razorpay.com/v1/checkout.js"; s.onload = ok; s.onerror = function () { fail(new Error("Could not load the payment window. Check your internet and try again.")); }; document.head.appendChild(s); });
  }
  function setBusy(b) { busy = b; var g = $("[data-co-go]"); g.disabled = b; if (b) g.textContent = "Please wait…"; else render(); }
  function summary(c, t, extra) {
    return Object.assign({ name: c.name, phone: c.phone, city: c.city, pin: c.pin, total: t.total,
      items: cart().map(function (l) { return { n: P[l.id].name, q: l.qty, p: P[l.id].price }; }) }, extra);
  }

  function payOnline(c) {
    var r = ref(), items = cart().map(function (l) { return { id: l.id, qty: l.qty }; }), t = totals("online");
    setBusy(true); msg("");
    rzLoad().then(function () { return api("/api/create-order/", { items: items, coupon: coupon, ref: r }); }).then(function (o) {
      if (!o.orderId) throw new Error(o.error || "Could not start the payment.");
      var rz = new Razorpay({
        key: o.keyId, order_id: o.orderId, amount: o.amount, currency: "INR", name: "Mirc Glow", description: "Order " + r,
        prefill: { name: c.name, contact: "+91" + c.phone, email: c.email || undefined }, notes: { ref: r }, theme: { color: "#157A36" },
        handler: function (resp) {
          msg("Payment received. Confirming…", "ok");
          api("/api/verify-payment/", Object.assign({}, resp, { items: items, coupon: coupon, ref: r, customer: c })).then(function (v) {
            if (!v.ok) { setBusy(false); msg((v.error || "We could not confirm the payment.") + " If money was deducted, please WhatsApp us your order number " + r + ".", "err"); return; }
            done(summary(c, t, { ref: r, pay: "online", amount: v.amount, paymentId: v.paymentId }));
          }).catch(function () { setBusy(false); msg("We could not confirm the payment. If money was deducted, please WhatsApp us your order number " + r + ".", "err"); });
        },
        modal: { ondismiss: function () { setBusy(false); msg("Payment cancelled. You can try again or choose Cash on Delivery."); } }
      });
      rz.on("payment.failed", function (e) { msg("Payment failed: " + ((e.error && e.error.description) || "please try again") + ".", "err"); });
      rz.open();
    }).catch(function (e) { setBusy(false); msg(e.message + " You can also choose Cash on Delivery or order on WhatsApp.", "err"); });
  }
  function payCod(c) {
    var r = ref(), t = totals("cod");
    setBusy(true); msg("");
    api("/api/cod-order/", { ref: r, items: cart().map(function (l) { return { id: l.id, qty: l.qty }; }), coupon: coupon, customer: c, website: $("#co-form").elements.website.value })
      .then(function (o) {
        if (o.ok) { done(summary(c, t, { ref: o.ref || r, pay: "cod", awb: o.awb || "", trackUrl: o.trackUrl || "" })); return; }
        setBusy(false);
        if (o.codUnavailable) { var on = document.querySelector('input[name="pay"][value="online"]'); if (on && !on.disabled) { on.checked = true; render(); } }
        msg(o.error || "We could not place the order. Please try again, or order on WhatsApp.", "err");
      }).catch(function () { setBusy(false); msg("Network problem. Please try again, or order on WhatsApp.", "err"); });
  }

  // events
  document.addEventListener("click", function (e) {
    var q = e.target.closest("[data-q]"), rm = e.target.closest("[data-rm]");
    if (q || rm) {
      var id = (q || rm).getAttribute(q ? "data-id" : "data-rm"), c = MGCart.get();
      c = c.map(function (l) { if (l.id === id) l.qty = rm ? 0 : Math.max(0, Math.min(10, l.qty + parseInt(q.getAttribute("data-q"), 10))); return l; }).filter(function (l) { return l.qty > 0; });
      MGCart.set(c); render();
    }
  });
  $("#co-form").addEventListener("change", function (e) { if (e.target.name === "pay") render(); save(); });
  $("#co-form").addEventListener("input", function () { $("[data-co-wa]").href = waLink(); });
  $("[data-cp-apply]").addEventListener("click", function () {
    var v = $("#co-cp").value.trim().toUpperCase();
    if (!v) { coupon = ""; msg(""); render(); return; }
    if (D.coupons[v]) { coupon = v; msg("Code " + v + " applied: " + D.coupons[v] + "% off.", "ok"); } else { coupon = ""; msg("That code isn't valid.", "err"); }
    render();
  });
  var pinEl = $("#co-form").elements.pin, lastPin = "";
  pinEl.addEventListener("input", function () {
    var p = pinEl.value.replace(/\D/g, ""); if (p.length !== 6 || p === lastPin) return; lastPin = p;
    fetch("/api/pincode/?pin=" + p).then(function (r) { return r.json(); }).then(function (s) {
      var f = $("#co-form"), note = $("[data-pin-note]");
      if (!s.known) { note.textContent = ""; return; }
      if (s.city && !f.elements.city.value) f.elements.city.value = s.city.replace(/\b\w/g, function (x) { return x.toUpperCase(); }).replace(/\B\w+/g, function (x) { return x.toLowerCase(); });
      if (s.state && !f.elements.state.value) f.elements.state.value = s.state;
      var cod = document.querySelector('input[name="pay"][value="cod"]');
      if (cod && cfg.cod) { cod.disabled = !s.cod; cod.closest(".co-opt").classList.toggle("off", !s.cod); if (!s.cod && cod.checked) { var on = document.querySelector('input[name="pay"][value="online"]'); if (on && !on.disabled) on.checked = true; } }
      note.textContent = s.cod ? "✓ We deliver here · Cash on Delivery available" : (s.prepaid ? "✓ We deliver here · online payment only for this pin code" : "");
      render();
    }).catch(function () {});
  });
  $("#co-form").addEventListener("submit", function (e) {
    e.preventDefault(); if (busy) return;
    var c = form(), m = mode(), err = check(c);
    if (!cart().length) return msg("Your cart is empty.", "err");
    if (err) return msg(err, "err");
    save();
    if (m === "online") return payOnline(c);
    if (m === "cod") return payCod(c);
    window.open(waLink(), "_blank", "noopener");
  });

  // which payment options are switched on (from the server; no secrets)
  restore(); render();
  fetch("/api/payment-config/").then(function (r) { return r.json(); }).then(function (j) { cfg.online = !!j.online; cfg.cod = !!j.cod; if (j.prepaidPct != null) cfg.prepaidPct = j.prepaidPct; })
    .catch(function () {}).then(function () {
      var on = document.querySelector('input[name="pay"][value="online"]'), cod = document.querySelector('input[name="pay"][value="cod"]');
      [[on, cfg.online], [cod, cfg.cod]].forEach(function (x) { x[0].disabled = !x[1]; x[0].closest(".co-opt").hidden = !x[1]; });
      if (cfg.online) on.checked = true; else if (cfg.cod) cod.checked = true;
      $("[data-co-waonly]").hidden = cfg.online || cfg.cod;
      if (!cfg.online) cfg.prepaidPct = 0;
      render();
    });
}
// runs after every deferred script (site.js provides MGCart)
if (window.MGCart) mgCheckout(); else document.addEventListener("DOMContentLoaded", mgCheckout);
