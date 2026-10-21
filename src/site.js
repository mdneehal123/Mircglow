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
  var bar = document.getElementById("pbar"), buy = document.querySelector("#buy [data-cart-add]");
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
/* Cart: kept only in this browser (localStorage "mg_cart" = [{id, qty}]). Checkout is at /checkout/. */
(function () {
  var K = "mg_cart";
  function get() { try { var c = JSON.parse(localStorage.getItem(K) || "[]"); return Array.isArray(c) ? c : []; } catch (e) { return []; } }
  function set(c) { try { localStorage.setItem(K, JSON.stringify(c)); } catch (e) {} count(); }
  function count() {
    var n = get().reduce(function (a, l) { return a + (l.qty || 0); }, 0);
    document.querySelectorAll("[data-cart-count]").forEach(function (b) { b.textContent = n; b.hidden = !n; });
  }
  function add(id, qty) {
    var c = get(), l = c.filter(function (x) { return x.id === id; })[0];
    if (l) l.qty = Math.min(10, l.qty + qty); else c.push({ id: id, qty: Math.min(10, qty) });
    set(c);
  }
  function toast(msg) {
    var t = document.getElementById("cart-toast");
    if (!t) { t = document.createElement("div"); t.id = "cart-toast"; t.className = "cart-toast"; t.setAttribute("role", "status"); document.body.appendChild(t); }
    t.innerHTML = msg; t.classList.add("on"); clearTimeout(t._h); t._h = setTimeout(function () { t.classList.remove("on"); }, 3500);
  }
  window.MGCart = { get: get, set: set, add: add, count: count };
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-cart-add]"); if (!b) return;
    e.preventDefault();
    var box = b.closest(".panel, .buy"); var q = box && box.querySelector(".qty input");
    var n = q ? parseInt(q.value, 10) || 1 : 1;
    add(b.getAttribute("data-cart-add"), n);
    if (b.hasAttribute("data-go")) { location.href = "/checkout/"; return; }
    toast('Added to cart · <a href="/checkout/">View cart &amp; checkout</a>');
  });
  count();
})();
