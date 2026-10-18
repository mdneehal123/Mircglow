/* Mirc Glow: quantity boxes, WhatsApp order links, sticky buy bar, guide slider. */
(function () {
  // quantity − / +
  document.addEventListener("click", function (e) {
    var b = e.target.closest(".qty button"); if (!b) return;
    var i = b.parentNode.querySelector("input"); var v = parseInt(i.value, 10) || 1;
    i.value = Math.max(1, Math.min(20, v + parseInt(b.getAttribute("data-step"), 10)));
  });
  // put the chosen quantity into the WhatsApp message
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[data-wa-order]"); if (!a) return;
    var box = a.closest(".panel, .buy"); var q = box && box.querySelector(".qty input");
    var n = q ? parseInt(q.value, 10) || 1 : 1;
    var base = a.getAttribute("data-base") || a.href; a.setAttribute("data-base", base);
    if (n < 2) { a.href = base; return; }
    try {
      var u = new URL(base); var t = u.searchParams.get("text") || "";
      t = t.replace("• ", "• " + n + " x ");
      a.href = u.origin + u.pathname + "?text=" + encodeURIComponent(t); // %20 for spaces: WhatsApp shows them correctly
    } catch (x) {}
  }, true);
  // sticky buy bar on product pages, once the main buy button is off screen
  var bar = document.getElementById("pbar"), buy = document.querySelector("#buy [data-wa-order]");
  if (bar && buy && "IntersectionObserver" in window) {
    new IntersectionObserver(function (es) { var r = es[0]; bar.hidden = r.isIntersecting || r.boundingClientRect.top > 0; }).observe(buy);
  }
  // guide slider
  document.querySelectorAll("[data-slider]").forEach(function (s) {
    var nav = s.nextElementSibling; if (!nav) return;
    var c = nav.querySelector("[data-count]"), n = s.children.length;
    function step() { return s.children[0].getBoundingClientRect().width + 16; }
    function upd() { c.textContent = Math.min(n, Math.round(s.scrollLeft / step()) + 1) + " / " + n; }
    s.addEventListener("scroll", function () { requestAnimationFrame(upd); }, { passive: true });
    function go(d) { s.scrollBy({ left: d * step(), behavior: "smooth" }); setTimeout(upd, 450); setTimeout(upd, 900); }
    nav.querySelector("[data-prev]").onclick = function () { go(-1); };
    nav.querySelector("[data-next]").onclick = function () { go(1); };
    if ("onscrollend" in window) s.addEventListener("scrollend", upd);
  });
})();
/* home: offer slider (auto-advance + dots) and search that jumps straight to the page */
(function () {
  var s = document.querySelector("[data-fk-slider]");
  if (s) {
    var dots = s.parentNode.querySelectorAll(".fk-dots i"), n = s.children.length, i = 0, t;
    function cur() { return Math.round(s.scrollLeft / (s.children[0].offsetWidth + 10)); }
    function mark() { i = cur(); dots.forEach(function (d, k) { d.classList.toggle("on", k === i); }); }
    function next() { if (document.hidden) return; var w = s.children[0].offsetWidth + 10; var last = s.scrollLeft + s.clientWidth >= s.scrollWidth - 5; s.scrollTo({ left: last ? 0 : s.scrollLeft + w }); }
    s.addEventListener("scroll", function () { requestAnimationFrame(mark); }, { passive: true });
    function go() { clearInterval(t); t = setInterval(next, 4000); }
    s.addEventListener("touchstart", function () { clearInterval(t); }, { passive: true });
    s.addEventListener("touchend", go, { passive: true });
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) go();
    mark();
  }
  var f = document.querySelector("[data-fk-search]");
  if (f) f.addEventListener("submit", function (e) {
    var q = f.q.value.trim().toLowerCase(); if (!q) { e.preventDefault(); return; }
    var opts = f.querySelectorAll("option"), best = null;
    opts.forEach(function (o) { var v = o.value.toLowerCase(); if (!best && (v === q || v.indexOf(q) > -1)) best = o; });
    if (!best) { var w = q.split(/\s+/); opts.forEach(function (o) { var v = o.value.toLowerCase(); if (!best && w.every(function (x) { return v.indexOf(x) > -1; })) best = o; }); }
    e.preventDefault(); location.href = best ? best.getAttribute("data-u") : "/shop/";
  });
  var q = document.getElementById("fk-q");
  if (q) q.addEventListener("change", function () { var o = Array.prototype.find.call(q.list.options, function (o) { return o.value === q.value; }); if (o) location.href = o.getAttribute("data-u"); });
})();
/* Amazon-style: delivery date estimate and recently viewed items (stored only in this browser) */
(function () {
  var d = document.querySelector("[data-del]");
  if (d) {
    var f = function (n) { var t = new Date(); t.setDate(t.getDate() + n); return t.toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" }); };
    d.innerHTML = "<b>FREE delivery</b> between <b>" + f(3) + "</b> and <b>" + f(7) + "</b> · Cash on Delivery available";
  }
  var K = "mg_recent", list = [];
  try { list = JSON.parse(localStorage.getItem(K) || "[]"); } catch (e) {}
  var me = document.getElementById("rv-item"), cur = null;
  if (me) { try { cur = JSON.parse(me.textContent); } catch (e) {} }
  var box = document.querySelector("[data-recent]");
  if (box) {
    var show = list.filter(function (x) { return !cur || x.u !== cur.u; }).slice(0, 8);
    if (show.length) {
      box.querySelector(".az-rrow").innerHTML = show.map(function (x) {
        var e = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
        return '<a class="az-rv" href="' + e(x.u) + '"><img src="' + e(x.i) + '" alt="" loading="lazy">' + e(x.n) + '<b>' + e(x.p) + ' <s>' + e(x.m) + '</s></b></a>';
      }).join("");
      box.hidden = false;
    }
  }
  if (cur) {
    list = [cur].concat(list.filter(function (x) { return x.u !== cur.u; })).slice(0, 10);
    try { localStorage.setItem(K, JSON.stringify(list)); } catch (e) {}
  }
})();
/* Shop: cart (stored only in this browser), cart drawer, one-page checkout, order confirmation.
   Online checkout switches on when Razorpay or Delhivery keys are set in Vercel (/api/payment-config/);
   until then the site keeps ordering on WhatsApp exactly as before. Prices shown here come from build.py;
   the server works out the real amount itself. */
(function () {
  var CAT = window.MG_CAT || { p: {}, c: {}, wa: "919980881230" };
  var P = CAT.p, $ = function (s, r) { return (r || document).querySelector(s); };
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var rs = function (n) { return "₹" + Math.round(n).toLocaleString("en-IN"); };
  var waLink = function (t) { return "https://wa.me/" + CAT.wa + "?text=" + encodeURIComponent(t); };

  /* ---------- cart ---------- */
  var cart = (store.get("mg_cart", []) || []).filter(function (l) { return l && P[l.id] && l.qty > 0; });
  function saveCart() { store.set("mg_cart", cart); paintCount(); }
  function count() { return cart.reduce(function (a, l) { return a + l.qty; }, 0); }
  function subtotal() { return cart.reduce(function (a, l) { return a + P[l.id].p * l.qty; }, 0); }
  function mrpTotal() { return cart.reduce(function (a, l) { return a + P[l.id].m * l.qty; }, 0); }
  function setQty(id, q) {
    q = Math.max(0, Math.min(20, q | 0));
    var l = cart.filter(function (x) { return x.id === id; })[0];
    if (!q) cart = cart.filter(function (x) { return x.id !== id; });
    else if (l) l.qty = q; else cart.push({ id: id, qty: q });
    saveCart();
  }
  function addItem(id, q) { var l = cart.filter(function (x) { return x.id === id; })[0]; setQty(id, (l ? l.qty : 0) + q); }
  function paintCount() {
    document.querySelectorAll("[data-cart-count]").forEach(function (b) { var n = count(); b.textContent = n; b.hidden = !n; });
  }
  function cartMsg() {
    return "Hi Mirc Glow, I'd like to order:\n" + cart.map(function (l) { var p = P[l.id]; return "• " + (l.qty > 1 ? l.qty + " x " : "") + p.n + " (" + p.s + ") – " + rs(p.p) + " each"; }).join("\n") +
      "\nTotal: " + rs(subtotal()) + "\n\nName:\nFull address with pincode:\nPayment: Cash on Delivery / pay online";
  }

  /* ---------- is online checkout switched on? ---------- */
  var cfg = null;
  function payConfig(fresh) {
    var c = store.get("mg_pay", null);
    if (!fresh && c && c.v && Date.now() - c.t < 6e5) return Promise.resolve(c.v);
    if (!window.fetch) return Promise.resolve({ enabled: false, cod: false });
    return fetch("/api/payment-config/", { cache: "no-store" }).then(function (r) { if (!r.ok) throw 0; return r.json(); })
      .then(function (j) { var v = { enabled: !!j.enabled, keyId: j.keyId || "", cod: !!j.cod }; store.set("mg_pay", { v: v, t: Date.now() }); return v; })
      .catch(function () { return { enabled: false, cod: false }; });
  }
  function applyConfig(v) { cfg = v; document.documentElement.classList.toggle("shop-off", !(v.enabled || v.cod) && !count()); }

  /* ---------- drawer ---------- */
  var drawer = null;
  function lineHTML(l, small) {
    var p = P[l.id];
    return '<div class="cd-line"><a href="' + esc(p.u) + '"><img src="' + esc(p.i) + '" alt="" width="64" height="64" loading="lazy"></a><div><a class="cd-t" href="' + esc(p.u) + '">' + esc(p.n) + '</a><span class="cd-m">' + esc(p.s) + ' · ' + rs(p.p) + '</span>' +
      (small ? '<span class="cd-m">Qty ' + l.qty + '</span>' : '<div class="cd-q"><button type="button" data-q="' + esc(l.id) + '" data-d="-1" aria-label="Decrease quantity">−</button><span>' + l.qty + '</span><button type="button" data-q="' + esc(l.id) + '" data-d="1" aria-label="Increase quantity">+</button><button type="button" class="cd-rm" data-rm="' + esc(l.id) + '">Remove</button></div>') +
      '</div><b class="cd-p">' + rs(p.p * l.qty) + '</b></div>';
  }
  function cartBody() {
    if (!cart.length) return '<div class="cd-empty"><p>Your cart is empty.</p><a class="yb yb-fill" href="/shop/">Shop the creams</a></div>';
    var save = mrpTotal() - subtotal();
    return '<div class="cd-lines">' + cart.map(function (l) { return lineHTML(l); }).join("") + '</div>' +
      '<div class="cd-foot"><div class="cd-sub"><span>Subtotal</span><b>' + rs(subtotal()) + '</b></div>' +
      (save > 0 ? '<p class="cd-save">You save ' + rs(save) + ' · Free shipping</p>' : '<p class="cd-save">Free shipping across India</p>') +
      '<a class="yb yb-fill" href="/checkout/">Checkout</a><a class="cd-wa" href="' + esc(waLink(cartMsg())) + '" target="_blank" rel="noopener">Or order this cart on WhatsApp</a></div>';
  }
  function paintCart() {
    if (drawer) $(".cd-body", drawer).innerHTML = cartBody();
    var page = $("[data-cart-page]"); if (page) page.innerHTML = cartBody();
  }
  function openDrawer(note) {
    if (!drawer) {
      drawer = document.createElement("div"); drawer.className = "cd"; drawer.hidden = true;
      drawer.innerHTML = '<div class="cd-bg" data-cd-close></div><div class="cd-panel" role="dialog" aria-modal="true" aria-labelledby="cdH"><div class="cd-head"><h2 id="cdH">Your cart</h2><button type="button" class="cd-x" data-cd-close aria-label="Close cart">×</button></div><p class="cd-note" hidden></p><div class="cd-body"></div></div>';
      document.body.appendChild(drawer);
    }
    paintCart();
    var n = $(".cd-note", drawer); n.textContent = note || ""; n.hidden = !note;
    drawer.hidden = false; document.documentElement.classList.add("cd-open");
    setTimeout(function () { var x = $(".cd-x", drawer); if (x) x.focus(); }, 30);
  }
  function closeDrawer() { if (drawer) { drawer.hidden = true; document.documentElement.classList.remove("cd-open"); } }
  function qtyNear(el) { var box = el.closest(".buy, .panel"); var i = box && box.querySelector(".qty input"); return i ? Math.max(1, parseInt(i.value, 10) || 1) : 1; }

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-cart-add],[data-cart-buy],[data-cart-open],[data-cd-close],[data-q],[data-rm]");
    if (!t) return;
    if (t.hasAttribute("data-cart-add")) {
      var ids = t.getAttribute("data-cart-add").split(","), q = ids.length > 1 ? 1 : qtyNear(t);
      ids.forEach(function (id) { if (P[id]) addItem(id, q); });
      openDrawer(ids.length > 1 ? "Both creams added to your cart." : "Added to your cart."); return;
    }
    if (t.hasAttribute("data-cart-buy")) {
      var id = t.getAttribute("data-cart-buy"); if (!P[id]) return;
      var l = cart.filter(function (x) { return x.id === id; })[0];
      setQty(id, Math.max(qtyNear(t), l ? l.qty : 0)); location.href = "/checkout/"; return;
    }
    if (t.hasAttribute("data-cart-open")) { e.preventDefault(); openDrawer(); return; }
    if (t.hasAttribute("data-cd-close")) { closeDrawer(); return; }
    if (t.hasAttribute("data-q")) { var k = t.getAttribute("data-q"), c = cart.filter(function (x) { return x.id === k; })[0]; if (c) setQty(k, c.qty + parseInt(t.getAttribute("data-d"), 10)); paintCart(); return; }
    if (t.hasAttribute("data-rm")) { setQty(t.getAttribute("data-rm"), 0); paintCart(); }
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });
  paintCount();
  if ($("[data-cart-page]")) paintCart();
  payConfig(false).then(applyConfig);

  /* ---------- checkout ---------- */
  var form = document.getElementById("ckForm");
  if (form) checkout();
  function checkout() {
    var co = store.get("mg_co", {}) || {}, coupon = "";
    ["phone", "email", "name", "address", "landmark", "pin", "city"].forEach(function (k) { if (co[k]) form[k].value = co[k]; });
    if (co.state) form.state.value = co.state;
    if (co.pay === "cod") form.pay.value = "cod";
    if (co.coupon && CAT.c[co.coupon]) coupon = co.coupon;
    $("#coupon").value = coupon;
    var read = function () {
      co = { phone: form.phone.value.replace(/\D/g, ""), email: form.email.value.trim(), name: form.name.value.trim(), address: form.address.value.trim(), landmark: form.landmark.value.trim(),
        pin: form.pin.value.replace(/\D/g, ""), city: form.city.value.trim(), state: form.state.value, pay: form.pay.value, coupon: coupon };
      store.set("mg_co", co);
    };
    function totals() {
      var sub = subtotal(), c = CAT.c[coupon], off = 0;
      if (c && sub >= c.min) off = Math.round(c.type === "pct" ? sub * c.value / 100 : c.value);
      return { sub: sub, mrp: mrpTotal(), off: off, total: sub - off };
    }
    function paint() {
      var empty = !cart.length;
      $("#ckEmpty").hidden = !empty; form.classList.toggle("is-empty", empty);
      if (empty) return;
      var t = totals();
      $("#ckLines").innerHTML = cart.map(function (l) { return lineHTML(l); }).join("");
      $("#ckTot").innerHTML = '<div><span>MRP total</span><s>' + rs(t.mrp) + '</s></div><div><span>Price</span><span>' + rs(t.sub) + '</span></div>' +
        (t.off ? '<div class="g"><span>Coupon ' + esc(coupon) + '</span><span>−' + rs(t.off) + '</span></div>' : '') +
        '<div><span>Shipping</span><span class="g">FREE</span></div><div class="grand"><span>' + (co.pay === "cod" ? "Pay on delivery" : "To pay") + '</span><span>' + rs(t.total) + '</span></div>';
      $("#sumTop").textContent = rs(t.total);
      $("#barAmt").innerHTML = rs(t.total) + '<small>You save ' + rs(t.mrp - t.total) + '</small>';
      var on = cfg && (co.pay === "online" ? cfg.enabled : cfg.cod);
      $("#placeBtn").textContent = !on ? "Confirm order on WhatsApp" : co.pay === "online" ? "Pay " + rs(t.total) : "Place COD order";
      $("#onlineNote").textContent = cfg && !cfg.enabled ? "UPI or card · we send a secure payment link on WhatsApp" : "UPI · Cards · Net banking · Wallets, full amount";
      $("#ckWa").href = waLink(cartMsg());
      marks();
    }
    function marks() {
      var c = /^[6-9]\d{9}$/.test(co.phone), a = co.name.length > 1 && /^\d{6}$/.test(co.pin) && co.city && co.address.length > 7 && co.state;
      var n1 = $("#n1"), n2 = $("#n2");
      n1.className = "ck-n" + (c ? " done" : ""); n1.textContent = c ? "✓" : "1";
      n2.className = "ck-n" + (a ? " done" : ""); n2.textContent = a ? "✓" : "2";
    }
    function setErr(id, m) { var f = $("#f-" + id); if (f) { f.classList.add("bad"); $(".ck-err", f).textContent = m; } }
    function clearErr(id) { var f = $("#f-" + id); if (f) { f.classList.remove("bad"); $(".ck-err", f).textContent = ""; } }
    function validate() {
      var first = null, bad = function (id, m) { setErr(id, m); first = first || id; };
      if (!/^[6-9]\d{9}$/.test(co.phone)) bad("phone", "Enter a 10-digit mobile number starting with 6–9.");
      if (co.email && !/^\S+@\S+\.\S+$/.test(co.email)) bad("email", "Check the email address, or leave it blank.");
      if (co.name.length < 2) bad("name", "Enter the name for delivery.");
      if (co.address.length < 8) bad("address", "Add house number, street and area.");
      if (!/^[1-9]\d{5}$/.test(co.pin)) bad("pin", "Pin code should be 6 digits.");
      if (!co.city) bad("city", "Enter your city.");
      if (!co.state) bad("state", "Choose your state.");
      if (first) { var el = document.getElementById(first); el.scrollIntoView({ behavior: "smooth", block: "center" }); setTimeout(function () { el.focus(); }, 300); }
      return !first;
    }
    var lastPin = "";
    function lookupPin(pin) {
      if (pin === lastPin || !window.fetch) return; lastPin = pin;
      var m = $("#pinMsg");
      fetch("https://api.postalpincode.in/pincode/" + pin).then(function (r) { return r.json(); }).then(function (j) {
        var po = j && j[0] && j[0].PostOffice && j[0].PostOffice[0];
        if (!po) { if (j && j[0] && j[0].Status === "Error") { m.className = "ck-msg no"; m.textContent = "We couldn't find that pin code. Please check it."; } return; }
        if (!form.city.value.trim()) form.city.value = po.District;
        var st = Array.prototype.filter.call(form.state.options, function (o) { return o.value && o.value.toLowerCase() === String(po.State).toLowerCase(); })[0];
        if (st) form.state.value = st.value;
        m.className = "ck-msg ok"; m.textContent = "Delivering to " + po.District + ", " + po.State + " · Free shipping";
        clearErr("city"); clearErr("state"); read(); paint();
      }).catch(function () {});
    }
    function applyCoupon(code) {
      code = String(code || "").trim().toUpperCase(); var m = $("#cMsg"), c = CAT.c[code];
      if (!code) { coupon = ""; m.textContent = ""; }
      else if (!c) { coupon = ""; m.className = "ck-msg no"; m.textContent = "That code isn't valid."; }
      else if (subtotal() < c.min) { coupon = ""; m.className = "ck-msg no"; m.textContent = "Add " + rs(c.min - subtotal()) + " more to use " + code + "."; }
      else { coupon = code; m.className = "ck-msg ok"; m.textContent = code + " applied · " + (c.label || ""); }
      $("#applyC").textContent = coupon ? "Remove" : "Apply"; read(); paint();
    }
    form.addEventListener("input", function (e) {
      var t = e.target;
      if (t.id === "phone") t.value = t.value.replace(/\D/g, "").slice(0, 10);
      if (t.id === "pin") { t.value = t.value.replace(/\D/g, "").slice(0, 6); if (t.value.length === 6) lookupPin(t.value); }
      if (t.id === "coupon") return;
      read(); clearErr(t.id); paint();
    });
    form.addEventListener("change", function () { read(); paint(); });
    $("#applyC").onclick = function () { if (coupon) { $("#coupon").value = ""; applyCoupon(""); } else applyCoupon($("#coupon").value); };
    $("#coupon").addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); applyCoupon(this.value); } });
    $("#sumT").onclick = function () { var b = $("#sumBody"), o = b.classList.toggle("open"); this.setAttribute("aria-expanded", o); };
    document.addEventListener("click", function (e) { if (e.target.closest("#ckLines [data-q], #ckLines [data-rm]")) setTimeout(function () { applyCoupon(coupon); }, 0); });
    form.addEventListener("submit", placeOrder);
    read(); if (coupon) applyCoupon(coupon); paint();
    payConfig(true).then(function (v) { applyConfig(v); paint(); });
    if (co.pin && co.pin.length === 6) lookupPin(co.pin);

    function payMsg(t) { var m = $("#payMsg"); m.textContent = t || ""; m.hidden = !t; }
    function items() { return cart.map(function (l) { return { id: l.id, qty: l.qty }; }); }
    function cust() { return { name: co.name, phone: co.phone, email: co.email, address: co.address, landmark: co.landmark, city: co.city, state: co.state, pin: co.pin }; }
    function post(url, body) {
      return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { j._status = r.status; j._ok = r.ok; return j; }); });
    }
    function busy(on, label) { var b = $("#placeBtn"); b.disabled = on; if (on) { b.setAttribute("data-l", b.textContent); b.textContent = label; } else if (b.getAttribute("data-l")) b.textContent = b.getAttribute("data-l"); }
    function loadRazorpay() {
      if (window.Razorpay) return Promise.resolve();
      return new Promise(function (ok, fail) { var sc = document.createElement("script"); sc.src = "https://checkout.razorpay.com/v1/checkout.js"; sc.onload = ok; sc.onerror = function () { fail(new Error("Could not load the payment window. Check your internet and try again.")); }; document.head.appendChild(sc); });
    }
    function payOnline(order) {
      busy(true, "Opening secure payment…");
      return loadRazorpay().then(function () { return post("/api/create-order/", { items: items(), coupon: coupon, ref: order.id }); }).then(function (j) {
        if (!j._ok) throw new Error(j.error || "Could not start the payment.");
        order.t.total = j.total;
        return new Promise(function (resolve, reject) {
          var rzp = new window.Razorpay({ key: j.keyId, order_id: j.orderId, amount: j.amount, currency: "INR", name: "Mirc Glow", description: "Order " + order.id,
            image: "/assets/logo.png", prefill: { name: co.name, contact: "+91" + co.phone, email: co.email || "" }, notes: { ref: order.id }, theme: { color: "#157A36" },
            modal: { ondismiss: function () { reject(new Error("Payment was cancelled. You can try again or choose Cash on Delivery.")); } },
            handler: function (resp) {
              var fail = "We couldn't confirm the payment. If money was deducted, message us on WhatsApp with order " + order.id + ".";
              post("/api/verify-payment/", { razorpay_order_id: resp.razorpay_order_id, razorpay_payment_id: resp.razorpay_payment_id, razorpay_signature: resp.razorpay_signature, ref: order.id, items: items(), coupon: coupon, customer: cust() })
                .then(function (v) { if (!v.ok) return reject(new Error(v.error || fail)); resolve({ paymentId: resp.razorpay_payment_id, amount: v.amount, method: v.method, savedToDesk: v.savedToDesk }); })
                .catch(function () { reject(new Error(fail)); });
            } });
          rzp.on("payment.failed", function (ev) { payMsg((ev.error && ev.error.description) || "Payment failed. Please try again."); });
          rzp.open();
        });
      }).then(function (r) { busy(false); return r; }, function (e) { busy(false); throw e; });
    }
    function bookCod(order) {
      busy(true, "Placing your order…");
      return post("/api/cod-order/", { ref: order.id, items: items(), coupon: coupon, customer: cust(), website: form.website.value })
        .then(function (j) { busy(false); if (!j._ok) { var er = new Error(j.error || "Could not place the order."); er.codUnavailable = j.codUnavailable; throw er; } return j; },
              function () { busy(false); throw new Error("Could not reach the server."); });
    }
    function placeOrder(e) {
      e.preventDefault(); read(); payMsg("");
      if (!cart.length || !validate()) return;
      var t = totals();
      var order = { id: "MG" + Date.now().toString().slice(-7), items: cart.map(function (l) { var p = P[l.id]; return { id: l.id, n: p.n, s: p.s, p: p.p, qty: l.qty }; }),
        co: JSON.parse(JSON.stringify(co)), t: t, coupon: t.off ? coupon : "", at: new Date().toISOString() };
      payConfig(true).then(function (v) {
        applyConfig(v);
        if (co.pay === "online" && v.enabled) return payOnline(order).then(function (pd) { order.paid = pd; finish(order); }, function (err) { payMsg(err.message); });
        if (co.pay === "cod" && v.cod) return bookCod(order).then(function (j) { order.ship = j; order.t.total = j.total; finish(order); }, function (err) {
          payMsg(err.message + (err.codUnavailable ? "" : " You can also confirm the order on WhatsApp."));
          if (!err.codUnavailable) finish(order);
        });
        finish(order);
      });
    }
    function finish(order) {
      var t = order.t, c = order.co;
      var lines = order.items.map(function (i) { return "• " + i.n + " (" + i.s + ") × " + i.qty + " = " + rs(i.p * i.qty); }).join("\n");
      var pay = order.paid ? "PAID ONLINE ✅ " + rs(order.paid.amount) + " (Razorpay " + order.paid.paymentId + ")"
        : c.pay === "cod" ? "Cash on Delivery" + (order.ship && order.ship.awb ? " · Delhivery AWB " + order.ship.awb : "") : "Online (please send a payment link)";
      var msg = "New order " + order.id + "\n\n" + lines + "\n\nSubtotal: " + rs(t.sub) + (t.off ? "\nCoupon " + order.coupon + ": -" + rs(t.off) : "") + "\nTotal: " + rs(t.total) + "\nPayment: " + pay +
        "\n\nName: " + c.name + "\nPhone: +91 " + c.phone + (c.email ? "\nEmail: " + c.email : "") + "\nAddress: " + c.address + (c.landmark ? " (landmark: " + c.landmark + ")" : "") + ", " + c.city + ", " + c.state + " - " + c.pin;
      order.wa = waLink(msg);
      store.set("mg_last", order);
      cart = []; saveCart();
      location.href = "/order-success/";
    }
  }

  /* ---------- order confirmation ---------- */
  var ok = $("[data-success]");
  if (ok) {
    var o = store.get("mg_last", null);
    if (o && o.items) {
      var done = !!(o.paid || (o.ship && o.ship.ok));
      $("#okH").textContent = (o.paid ? "Payment received, " : done ? "Order placed, " : "Almost done, ") + (String(o.co.name || "").split(" ")[0] || "thank you") + "!";
      var box = o.paid ? '<p class="ck-good">✓ ' + rs(o.paid.amount) + ' paid online · Payment ID ' + esc(o.paid.paymentId) + '</p>'
        : o.ship && o.ship.awb ? '<p class="ck-good">✓ Booked with Delhivery · Tracking number <b>' + esc(o.ship.awb) + '</b> · <a href="' + esc(o.ship.trackUrl) + '" target="_blank" rel="noopener">Track parcel</a></p>'
        : o.ship && o.ship.ok ? '<p class="ck-good">✓ Order received. We will send your tracking number on WhatsApp once the parcel is booked.</p>' : "";
      var txt = done ? (o.paid ? "Payment received. We're packing your order and will share the tracking number on WhatsApp." : "Pay " + rs(o.t.total) + " in cash when the parcel arrives. Tap below if you'd like a copy of your order on WhatsApp.")
        : "Tap below to send your order on WhatsApp so we can confirm and ship it" + (o.co.pay === "online" ? ". We'll reply with a secure payment link for " + rs(o.t.total) + "." : ".");
      $("#okBody").innerHTML = box + '<p class="ck-muted">Order <b class="ck-oid">' + esc(o.id) + '</b>. ' + txt + '</p>' +
        '<a class="yb yb-fill ck-wabtn" href="' + esc(o.wa) + '" target="_blank" rel="noopener">' + (done ? "Send order details on WhatsApp" : "Confirm order on WhatsApp") + '</a>' +
        '<div class="ck-p ck-rec"><h2>Order ' + esc(o.id) + '</h2>' + o.items.map(function (i) { return '<div class="ck-row"><span>' + esc(i.n) + ' · ' + esc(i.s) + ' × ' + i.qty + '</span><b>' + rs(i.p * i.qty) + '</b></div>'; }).join("") +
        (o.t.off ? '<div class="ck-row g"><span>Coupon ' + esc(o.coupon) + '</span><span>−' + rs(o.t.off) + '</span></div>' : '') +
        '<div class="ck-row grand"><span>' + (o.paid ? "Paid" : o.co.pay === "cod" ? "Pay on delivery" : "To pay online") + '</span><span>' + rs(o.t.total) + '</span></div>' +
        '<p class="ck-muted">Delivering to ' + esc(o.co.name) + ', ' + esc(o.co.address) + (o.co.landmark ? ' (landmark: ' + esc(o.co.landmark) + ')' : '') + ', ' + esc(o.co.city) + ', ' + esc(o.co.state) + ' ' + esc(o.co.pin) + ' · +91 ' + esc(o.co.phone) + '</p></div>';
    }
  }
})();
