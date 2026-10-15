def build_product(p):
    url = f"/product/{p['slug']}/"
    raw = read(os.path.join(SRC, "products", p["slug"] + ".html"))
    body_html, toc = add_h2_ids(lazy_imgs(raw))
    faqs = faqs_from(raw)
    crumbs = [("Home","/"),("Shop","/shop/")]
    crumbs.append((CATS[p["cats"][0]]["name"], cat_url(p["cats"][0])))
    crumbs.append((p["name"], url))
    sv = p["mrp"] - p["price"]; pct = round(sv * 100 / p["mrp"])
    save_note = "vs buying the creams separately" if "parts" in p else f"({pct}% off MRP)"
    pts = "".join(f"<li>{esc(x)}</li>" for x in p["pts"] + [f"Key ingredients: {', '.join(p['ing'][:3])}"])
    spec = (f'<dl class="spec"><dt>Size</dt><dd>{p["size"]}</dd><dt>Key ingredients</dt><dd>{esc(", ".join(p["ing"]))}</dd>'
            f'<dt>When to use</dt><dd>{esc(p["use"])}</dd><dt>Skin type</dt><dd>{esc(p["skin"])}</dd><dt>How long it lasts</dt><dd>{esc(p["lasts"])}</dd>'
            f'<dt>Full ingredient list</dt><dd>Printed on the pack</dd></dl>')
    toc_html = ('<nav class="toc" aria-label="Product details"><details open><summary>On this page</summary><ol>' + "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i,t in toc) + '</ol></details></nav>') if len(toc) >= 3 else ""
    if "parts" in p: others = [PBY[s] for s in p["parts"]] + [q for q in SETS if q["slug"] != p["slug"]]
    else: others = [q for q in SINGLES if q["slug"] != p["slug"]] + [s for s in SETS if p["slug"] in s["parts"]]
    others = others[:4]
    nodes = [ORG, product_ld(p, url), crumbs_ld(crumbs)]
    if faqs: nodes.append(faq_ld(faqs))
    out = head(p["rt"], p["rd"], url, og_type="product", image=p["img"],
               extra=f'<meta property="product:price:amount" content="{p["price"]}"><meta property="product:price:currency" content="INR"><meta property="product:availability" content="in stock"><link rel="preload" as="image" href="{p["img"]}" fetchpriority="high">' + ld(*nodes))
    out += header("/shop/")
    out += f'''<main id="main">{crumbs_html(crumbs)}
<div class="w pdp">
<div class="gallery"><div class="gal-box">{photo(p, "", eager=True, alt=strip_tags(p["h1"]))}<span class="pc-off">{pct}% off</span></div></div>
<div class="buy" id="buy">
<span class="eyebrow">Mirc Glow · {esc(p["tag"])}</span>
<h1 class="pdp-t">{esc(p["h1"])}</h1>
<p class="panel-pr"><s>{inr(p["mrp"])}</s> <b>{inr(p["price"])}</b> <span class="save">Save {inr(sv)}</span></p>
<p class="panel-tax">Taxes included. You save {inr(sv)} {save_note}. Free shipping across India.</p>
<p class="lead2">{esc(p["lead"])}</p>
{qty_box(p["slug"])}
{buy_btn(p, "Buy Now on WhatsApp")}
<a class="yb yb-line" href="{wa("Hi Mirc Glow, I have a question about the " + p["name"] + ".")}" target="_blank" rel="noopener">Ask a question first</a>
<p class="howpay">Tap Buy Now, add your name, address and pincode, and send. Pay by Cash on Delivery or a secure online link. We confirm every order on WhatsApp. First order? Mention <b>GLOW10</b> for 10% off.</p>
{PAY_CHIPS}
<ul class="ticks">{pts}</ul>
<div class="trust4"><div><span>🚚</span><b>Free shipping</b><small>3 to 7 days</small></div><div><span>💵</span><b>Cash on Delivery</b><small>Or pay online</small></div><div><span>↩️</span><b>7-day returns</b><small><a href="/returns-refunds/">Sealed jars</a></small></div><div><span>💬</span><b>WhatsApp help</b><small>{PHONE}</small></div></div>
{spec}
<p class="fine">Cosmetic product. Patch test before first use. Results vary from person to person. Does not change your natural skin tone.</p>
</div>
</div>
<section class="w details">{toc_html}<div class="prose">{body_html}</div></section>
<section class="sec soft" aria-labelledby="h-more"><div class="w"><span class="eyebrow">Pairs well with</span><h2 class="sh" id="h-more">You may also like</h2><div class="grid4">{"".join(card_html(q) for q in others)}</div></div></section>
</main>
<div class="pbar" id="pbar" hidden><div><b>{esc(p["name"])}</b><span>{inr(p["price"])}</span></div>{buy_btn(p, "Buy Now", "yb yb-fill yb-sm")}</div>
'''
    out += footer()
    write(url, out)

