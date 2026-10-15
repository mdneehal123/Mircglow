def qty_box(slug):
    return (f'<div class="qty-l">Quantity</div><div class="qty" data-qty="{slug}"><button type="button" data-step="-1" aria-label="Decrease quantity">−</button>'
            f'<input type="text" inputmode="numeric" value="1" readonly aria-label="Quantity"><button type="button" data-step="1" aria-label="Increase quantity">+</button></div>')

def buy_panel(p, hn="h2", eager=False):
    sv = p["mrp"] - p["price"]
    return (f'<div class="panel"><a class="panel-ph" href="/product/{p["slug"]}/" tabindex="-1" aria-hidden="true">{photo(p, "", eager=eager)}</a>'
            f'<{hn} class="panel-t"><a href="/product/{p["slug"]}/">{esc(p["name"])}{" · " + p["size"] if "parts" not in p else ""}</a></{hn}>'
            f'<p class="panel-pr"><s>{inr(p["mrp"])}</s> <b>{inr(p["price"])}</b> <span class="save">Save {inr(sv)}</span></p>'
            f'<p class="panel-tax">Taxes included. Free shipping across India.</p>'
            f'{qty_box(p["slug"])}'
            f'{buy_btn(p, "Buy Now on WhatsApp")}'
            f'<a class="yb yb-line" href="{wa("Hi Mirc Glow, I have a question about the " + p["name"] + ".")}" target="_blank" rel="noopener">Ask a question first</a>'
            f'<a class="panel-more" href="/product/{p["slug"]}/">{esc(p["name"])}: full details →</a>{PAY_CHIPS}</div>')

def build_home():
    url = "/"
    hero = [PBY[s] for s in ["avocado-korean-night-cream","glutathione-cream","korean-glass-skin-kit"]]
    four = [PBY[s] for s in ["avocado-korean-night-cream","glutathione-cream","avocado-night-cream","avocado-face-cream"]]
    jposts = [POST_BY[s] for s in ["is-avocado-cream-good-for-your-skin","how-long-does-glutathione-cream-take-to-work","glass-skin-routine-for-indian-skin",
                                    "best-night-cream-for-glowing-skin","kojic-acid-vs-glutathione","how-to-apply-night-cream"]]
    faqs = [
     ("Can I pay Cash on Delivery?", "Yes. Choose Cash on Delivery when you order on WhatsApp, or ask for a secure online payment link if you prefer to pay first."),
     ("How do I order?", "Tap Buy Now on any cream. WhatsApp opens with your order already written. Add your name, address and pincode, send it, and we confirm your order on WhatsApp."),
     ("How long does delivery take?", "Shipping is free on every order, and most orders arrive in 3 to 7 days anywhere in India. You get a tracking number when your parcel is dispatched."),
     ("Which cream should I choose?", "Dry skin: begin with the Avocado Night Cream. Most skin types: the Avocado Korean Night Cream. Dull or uneven-looking skin: the Glutathione Cream. Not sure? The skin quiz takes under a minute."),
     ("Will it change my skin colour?", "No. Our creams are cosmetics for softer, smoother, brighter-looking skin. They do not change your natural skin tone, and we will never claim they do."),
     ("Can I return a cream?", "Yes. Unopened, sealed jars can be returned within 7 days of delivery. Damaged, wrong or expired items are replaced or refunded."),
    ]
    faq_html = "".join(f'<details{" open" if i==0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for i,(q,a) in enumerate(faqs))
    faq_html = faq_html.replace("The skin quiz", '<a href="/skin-quiz/">The skin quiz</a>')
    itemlist = {"@type":"ItemList","name":"Mirc Glow creams","itemListElement":[{"@type":"ListItem","position":i+1,"url":SITE+f"/product/{p['slug']}/","name":p["name"]} for i,p in enumerate(PRODUCTS)]}
    body = head("Mirc Glow | Avocado Night Creams & Korean-Inspired Skincare",
        "Shop Mirc Glow avocado creams in India: avocado night creams and a daily avocado face cream with aloe vera, vitamin B3 and kojic acid. Free shipping and Cash on Delivery.",
        url, extra=f'<link rel="preload" as="image" href="{hero[0]["img"]}" fetchpriority="high">' + ld(ORG, WEBSITE, itemlist, faq_ld(faqs)))
    body += header("/")

    def ticks(items):
        return '<ul class="ticks">' + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul>"
    ben = ""
    for p, extra in [(PBY["avocado-korean-night-cream"], ["Avocado, aloe vera, vitamin B3 and kojic acid"]),
                     (PBY["glutathione-cream"], ["Glutathione, vitamin C and kojic acid"])]:
        ben += (f'<div class="ben"><a href="/product/{p["slug"]}/" tabindex="-1" aria-hidden="true">{photo(p, "ben-ph")}</a><div class="ben-b">'
                f'<h3>{esc(p["name"])}</h3>{ticks(p["pts"] + extra)}{buy_btn(p, "Buy Now · " + inr(p["price"]))}</div></div>')
    sets = ""
    for p in SETS:
        sets += (f'<a class="setc" href="/product/{p["slug"]}/">{photo(p, "setc-ph")}<div class="setc-b"><span class="save">Save {inr(p["mrp"]-p["price"])}</span>'
                 f'<h3>{esc(p["name"])}</h3><p>{esc(p["lead"])}</p><p class="pc-pr"><b>{inr(p["price"])}</b> <s>{inr(p["mrp"])}</s></p><span class="bc-more">View set →</span></div></a>')
    concern = [("Dry, tight-feeling skin","Avocado Night Cream →","/product/avocado-night-cream/",PBY["avocado-night-cream"]),
               ("Dull, tired-looking skin","Glutathione Cream →","/product/glutathione-cream/",PBY["glutathione-cream"]),
               ("Uneven-looking tone","Korean Night Cream →","/product/avocado-korean-night-cream/",PBY["avocado-korean-night-cream"]),
               ("A gift for someone","Gift sets →","/skincare-gift-sets/",PBY["korean-glass-skin-kit"])]
    con = "".join(f'<a class="con" href="{u}">{photo(p, "con-ph")}<b>{esc(t)}</b><span>{esc(s)}</span></a>' for t,s,u,p in concern)
    day = [("☀️","1. Cleanse","Wash your face with a gentle cleanser and pat dry."),
           ("🥑","2. Moisturise",'A thin layer of <a href="/product/avocado-face-cream/">Avocado Glow Cream</a> for soft, comfortable skin.'),
           ("🧴","3. Protect","Finish with sunscreen every morning, especially with kojic acid in your routine.")]
    night = [("🌙","1. Cleanse","Wash away sunscreen and the day with a gentle cleanser."),
             ("✨","2. Treat",'A pea-sized amount of <a href="/product/glutathione-cream/">Glutathione Cream</a> on face and neck.'),
             ("😴","3. Seal",'Finish with an <a href="/product/avocado-night-cream/">Avocado Night Cream</a> as your last step.')]
    rit = lambda steps, cls: '<div class="rit">' + "".join(f'<div class="rit-c {cls}"><span class="rit-i" aria-hidden="true">{i}</span><b>{t}</b><p>{d}</p></div>' for i,t,d in steps) + "</div>"
    blog = "".join(post_card(p) for p in jposts)

    body += f'''<main id="main">
<section class="panels" aria-label="Best sellers"><div class="panels-in">{"".join(buy_panel(p, eager=(i==0)) for i,p in enumerate(hero))}</div></section>

<section class="intro"><div class="w">
<span class="eyebrow">Mirc Glow · <span lang="ko">유리 피부</span></span>
<h1>Mirc Glow avocado night creams &amp; Korean-inspired skincare</h1>
<p>Premium skincare with glutathione, kojic acid and avocado care, thoughtfully formulated for brighter-looking, smoother-looking skin. Every cream contains aloe vera, vitamin B3 and kojic acid. From {inr(349)} · Free shipping · Cash on Delivery.</p>
<div class="row"><a class="yb yb-dark" href="/shop/">Shop best sellers</a><a class="yb yb-line" href="/skin-quiz/">Take the skin quiz</a></div>
</div></section>

<section class="w bens" aria-label="Signature creams">{ben}</section>

<section class="w icons3" aria-label="What our creams do">
<div><span>💧</span><b>HYDRATES</b><p>Helps skin feel soft and comfortable.</p></div>
<div><span>🎯</span><b>EVEN-LOOKING</b><p>Kojic acid and vitamin B3 for a more even look.</p></div>
<div><span>✨</span><b>GLOW</b><p>For a smooth, radiant-looking finish.</p></div>
</section>

<section class="sec" aria-labelledby="h-prod"><div class="w">
<span class="eyebrow c">What we offer</span><h2 id="h-prod" class="sh c">Our Products</h2>
<div class="grid4">{"".join(card_html(p) for p in four)}</div>
<p class="c" style="margin-top:22px"><a class="yb yb-dark" href="/shop/">View all products</a></p>
</div></section>

<section class="sec" aria-labelledby="h-con"><div class="w">
<span class="eyebrow">Personalized picks</span><h2 id="h-con" class="sh">Shop by Concern</h2>
<div class="cons">{con}</div>
</div></section>

<section class="sec soft" aria-labelledby="h-sets"><div class="w">
<span class="eyebrow">Bundle and save</span><h2 id="h-sets" class="sh">Combos and Kits</h2>
<p class="sub2">Our creams paired into simple routines, for less than buying each jar alone.</p>
<div class="sets3">{sets}</div>
</div></section>

<section class="sec" aria-labelledby="h-day"><div class="w">
<span class="eyebrow">Morning ritual</span><h2 id="h-day" class="sh">Day Routine</h2><p class="sub2">Start your day with a simple 3-step routine.</p>
{rit(day, "d")}
<span class="eyebrow" style="margin-top:34px">Evening ritual</span><h2 class="sh">Night Routine</h2><p class="sub2">Wind down with a simple evening routine.</p>
{rit(night, "n")}
<p class="c" style="margin-top:22px"><a class="yb yb-line" href="/skincare-routine-builder/">Build my routine</a> <a class="yb yb-dark" href="/shop/">Buy Now</a></p>
</div></section>

<section class="sec" aria-labelledby="h-blog"><div class="w">
<div class="sh-row"><h2 id="h-blog" class="sh">Skincare guides</h2><a href="/blog/">View all</a></div>
<div class="slider" data-slider>{blog}</div>
<div class="slider-nav"><button type="button" data-prev aria-label="Previous guide">‹</button><span data-count>1 / {len(jposts)}</span><button type="button" data-next aria-label="Next guide">›</button></div>
</div></section>

<section class="sec" aria-labelledby="h-faq"><div class="w faqw">
<h2 id="h-faq" class="sh c">Questions, answered</h2>
<div class="faq">{faq_html}</div>
<p class="c" style="margin-top:18px"><a class="yb yb-line" href="/faq/">View all FAQs</a></p>
</div></section>

<section class="sec"><div class="w"><div class="closer">
<h2 class="sh">Your glow starts here</h2>
<p>Korean-inspired essentials for hydration, radiance and a smooth, glass-skin-inspired finish. Order in one WhatsApp message.</p>
<div class="row" style="justify-content:center"><a class="yb yb-wa" href="{WA_HELLO}" target="_blank" rel="noopener">{WA_SVG}<span>Order on WhatsApp</span></a><a class="yb yb-line" href="/about/">About Mirc Glow</a></div>
</div></div></section>
</main>
'''
    body += footer()
    write(url, body)

