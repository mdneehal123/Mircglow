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
