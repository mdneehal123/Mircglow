NAV = [("Shop","/shop/"),("Night creams","/product-category/night-creams/"),("Combos","/product-category/combos/"),("Gift sets","/skincare-gift-sets/"),("Skincare guides","/blog/"),("About","/about/")]

ICONS = {
 "home": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
 "shop": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 8h14l-1 12H6zM9 8V6a3 3 0 0 1 6 0v2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
 "book": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2zM4 21V5M8 7h7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
 "quiz": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.5V14M12 17.2v.1" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
}

def header(active=""):
    nav = "".join(f'<a href="{u}"{" aria-current=\"page\"" if u==active else ""}>{n}</a>' for n,u in NAV)
    mob = "".join(f'<a href="{u}">{n}</a>' for n,u in [("Home","/")] + NAV + [("Skin quiz","/skin-quiz/"),("Track your order","/track-order/"),("FAQ","/faq/"),("Contact","/contact/")])
    return f'''<div class="ann"><span>Free shipping across India</span><span class="more">Cash on Delivery</span><span class="more">7-day returns</span><span>First order? Use <b>GLOW10</b></span></div>
<header class="hdr"><div class="w">
<details class="menu"><summary aria-label="Open menu"><span></span></summary><nav aria-label="Mobile">{mob}</nav></details>
<a class="word" href="/" aria-label="Mirc Glow home">MIRC<b>GLOW</b></a>
<nav class="nav" aria-label="Main">{nav}</nav>
<a class="hwa" href="{WA_HELLO}" target="_blank" rel="noopener" aria-label="Order on WhatsApp">{WA_SVG}<span>Order on WhatsApp</span></a>
</div></header>
'''

def footer(bar=True):
    tabs = (f'<nav class="tabs" aria-label="Quick links"><a href="/">{ICONS["home"]}<span>Home</span></a><a href="/shop/">{ICONS["shop"]}<span>Shop</span></a>'
            f'<a href="/blog/">{ICONS["book"]}<span>Guides</span></a><a href="/skin-quiz/">{ICONS["quiz"]}<span>Skin quiz</span></a>'
            f'<a class="tw" href="{WA_HELLO}" target="_blank" rel="noopener">{WA_SVG}<span>WhatsApp</span></a></nav>')
    fab = f'<a class="fab" href="{WA_HELLO}" target="_blank" rel="noopener" aria-label="Order on WhatsApp">{WA_SVG}</a>'
    return f'''<section class="trustbar" aria-label="Why shop with us"><div class="w">
<div><span>🚚</span><b>Free shipping</b><small>Across India, 3–7 days</small></div>
<div><span>💵</span><b>Cash on Delivery</b><small>Or pay online</small></div>
<div><span>↩️</span><b>7-day returns</b><small>On sealed jars</small></div>
<div><span>💬</span><b>WhatsApp help</b><small>Real people, real answers</small></div>
</div></section>
<footer class="ftr"><div class="w">
<div class="f-brand"><span class="word">MIRC<b>GLOW</b></span>
<p>Korean-inspired avocado and glutathione creams, made in Bhatkal, Karnataka.</p>
<p>Azad Nagar 4th Cross, Bhatkal,<br>Karnataka 581320, India<br>Phone &amp; WhatsApp <a href="tel:+919980881230">{PHONE}</a></p>
<a class="yb yb-wa yb-sm" href="{WA_HELLO}" target="_blank" rel="noopener">{WA_SVG}<span>Chat on WhatsApp</span></a></div>
<div><h2>Shop</h2><ul><li><a href="/shop/">All creams</a></li><li><a href="/product-category/night-creams/">Night creams</a></li><li><a href="/product-category/night-creams/avocado-night-creams/">Avocado creams</a></li><li><a href="/product-category/combos/">Combos and kits</a></li><li><a href="/skincare-gift-sets/">Gift sets</a></li><li><a href="/bulk-night-cream/">Bulk orders (kg)</a></li></ul></div>
<div><h2>Guides</h2><ul><li><a href="/blog/">Skincare guides</a></li><li><a href="/avocado-cream/">Avocado cream guide</a></li><li><a href="/korean-night-cream/">Korean night cream guide</a></li><li><a href="/skin-quiz/">Skin quiz</a></li><li><a href="/skincare-routine-builder/">Routine builder</a></li><li><a href="/skincare-ingredient-glossary/">Ingredient glossary</a></li></ul></div>
<div><h2>Help</h2><ul><li><a href="/track-order/">Track your order</a></li><li><a href="/shipping-policy/">Shipping policy</a></li><li><a href="/returns-refunds/">Returns and refunds</a></li><li><a href="/faq/">FAQ</a></li><li><a href="/contact/">Contact us</a></li></ul></div>
<div><h2>Mirc Glow</h2><ul><li><a href="/about/">About us</a></li><li><a href="/about-the-author/">About the author</a></li><li><a href="/editorial-policy/">Editorial policy</a></li><li><a href="/ingredients/">Ingredients</a></li><li><a href="/avocado-cream-hindi/" lang="hi">हिंदी में</a></li><li><a href="/privacy/">Privacy policy</a></li><li><a href="/terms/">Terms and conditions</a></li></ul></div>
<div class="base"><span>© 2026 Mirc Glow, Bhatkal, Karnataka</span><span>Cosmetic products. Results vary. Not intended to treat any skin condition.</span></div>
</div></footer>
{fab}{tabs}
<script src="{JS_HREF}" defer></script>
</body>
</html>
'''

def crumbs_html(items):
    lis = "".join(f'<li><a href="{u}">{esc(n)}</a></li>' if i < len(items)-1 else f'<li aria-current="page">{esc(n)}</li>' for i,(n,u) in enumerate(items))
    return f'<nav class="crumbs w" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'

