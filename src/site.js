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
    var n = q ? parseInt(q.value, 10) || 1 : 1; if (n < 2) return;
    try {
      var u = new URL(a.href); var t = u.searchParams.get("text") || "";
      t = t.replace("• ", "• " + n + " x ");
      u.searchParams.set("text", t); a.href = u.toString();
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
    nav.querySelector("[data-prev]").onclick = function () { s.scrollBy({ left: -step(), behavior: "smooth" }); };
    nav.querySelector("[data-next]").onclick = function () { s.scrollBy({ left: step(), behavior: "smooth" }); };
  });
})();
