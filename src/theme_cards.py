def order_msg(p, qty=1):
    q = f"{qty} x " if qty != 1 else ""
    return (f"Hi Mirc Glow, I'd like to order:\n• {q}{p['name']} ({p['size']}) – {inr(p['price'])} each\n\n"
            "Name:\nFull address with pincode:\nPayment: Cash on Delivery / pay online")

def buy_btn(p, label="Buy on WhatsApp", cls="yb yb-fill"):
    """WhatsApp order button. site.js swaps in the chosen quantity when a quantity box is on the page."""
    return (f'<a class="{cls}" href="{wa(order_msg(p))}" data-wa-order="{p["slug"]}" target="_blank" rel="noopener">'
            f'{WA_SVG}<span>{label}</span></a>')

PAY_CHIPS = ('<div class="chips-pay" aria-label="Payment options"><span>💵 Cash on Delivery</span><span>📱 UPI</span>'
             '<span>💳 Cards</span><span>🚚 Free shipping</span></div>')

def card_html(p, h="h3"):
    sv = p["mrp"] - p["price"]; pct = round(sv * 100 / p["mrp"])
    tile = photo(p, "pc-img")
    return (f'<article class="pc"><a href="/product/{p["slug"]}/" tabindex="-1" aria-hidden="true" class="pc-ph">{tile}'
            f'<span class="pc-off">{pct}% off</span></a>'
            f'<div class="pc-b"><{h} class="pc-t"><a href="/product/{p["slug"]}/">{esc(p["name"])}</a></{h}>'
            f'<p class="pc-m">{esc(p["meta"])} · {p["size"]}</p>'
            f'<p class="pc-pr"><b>{inr(p["price"])}</b> <s><span class="sr">MRP </span>{inr(p["mrp"])}</s></p>'
            f'{buy_btn(p, "Buy Now", "yb yb-fill yb-sm")}</div></article>')

def post_card(p, lead=False):
    t = TOPICS[p["topic"]][0]
    return (f'<a class="bc" href="/{p["slug"]}/"><span class="bc-tag">{esc(t)}</span><h3>{esc(p["title"])}</h3>'
            f'<span class="bc-d">{fmt_date(p["date"]).upper()}</span><p>{esc(p["ex"])}</p><span class="bc-more">Read more →</span></a>')

