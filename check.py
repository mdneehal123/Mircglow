#!/usr/bin/env python3
"""Checks the built site: links, meta, headings, schema, URL parity with WordPress."""
import json, os, re, sys, html
ROOT = os.path.dirname(os.path.abspath(__file__)); DIST = os.path.join(ROOT, "dist")
cfg = json.load(open(os.path.join(DIST, "vercel.json")))
redirect_src = [r["source"] for r in cfg["redirects"]]

def redirected(u):
    for s in redirect_src:
        if "(" in s and re.match("^" + s + "$", u): return True
        pat = "^" + re.sub(r":\w+[*+]?", ".*", s.replace(".", r"\.")) + "$"
        if re.match(pat, u): return True
    return False

def exists(u):
    u = u.split("#")[0].split("?")[0]
    if u in ("/feed/",): return True
    if u.startswith("/wp-content/uploads/"): return "upload"
    p = os.path.join(DIST, u.lstrip("/"))
    if u.endswith("/"): return os.path.exists(os.path.join(p, "index.html"))
    return os.path.exists(p)

pages = []
for d, _, fs in os.walk(DIST):
    for f in fs:
        if f.endswith(".html"): pages.append(os.path.join(d, f))
problems, uploads, titles, descs = [], set(), {}, {}
for f in sorted(pages):
    rel = "/" + os.path.relpath(f, DIST).replace("index.html", "")
    s = open(f, encoding="utf-8").read()
    t = re.search(r"<title>(.*?)</title>", s); dsc = re.search(r'<meta name="description" content="([^"]*)"', s)
    can = re.search(r'<link rel="canonical" href="([^"]+)"', s)
    if not t: problems.append(f"{rel}: no title")
    if not dsc or len(dsc.group(1)) < 50: problems.append(f"{rel}: weak description")
    if not can: problems.append(f"{rel}: no canonical")
    h1 = len(re.findall(r"<h1[\s>]", s))
    if h1 != 1: problems.append(f"{rel}: {h1} h1 tags")
    if t: titles.setdefault(html.unescape(t.group(1)), []).append(rel)
    if dsc: descs.setdefault(dsc.group(1), []).append(rel)
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, flags=re.S):
        try: json.loads(m)
        except Exception as e: problems.append(f"{rel}: bad JSON-LD {e}")
    ids = set(re.findall(r'\sid="([^"]+)"', s))
    for href in re.findall(r'(?:href|src)="([^"]+)"', s):
        if href.startswith(("http", "mailto:", "tel:", "data:")) or href.startswith("//"): continue
        if href.startswith("#"):
            if href[1:] and href[1:] not in ids: problems.append(f"{rel}: missing anchor {href}")
            continue
        if not href.startswith("/"): problems.append(f"{rel}: relative link {href}"); continue
        r = exists(href)
        if r == "upload": uploads.add(href.split("?")[0]); continue
        if not r:
            if redirected(href.split("#")[0]): problems.append(f"{rel}: links to redirected URL {href}")
            else: problems.append(f"{rel}: BROKEN {href}")
for t, us in titles.items():
    if len(us) > 1: problems.append(f"duplicate title '{t}': {us}")
for d, us in descs.items():
    if len(us) > 1: problems.append(f"duplicate description: {us}")

# shop pages stay out of Google; product prices on the pages match the server price table (api/_products.json)
sitemap = open(os.path.join(DIST, "sitemap.xml"), encoding="utf-8").read()
for u in ("/cart/", "/checkout/", "/order-success/"):
    f = os.path.join(DIST, u.strip("/"), "index.html")
    if not os.path.exists(f): problems.append(f"{u}: missing"); continue
    if 'name="robots" content="noindex' not in open(f, encoding="utf-8").read(): problems.append(f"{u}: should be noindex")
for f in pages:
    s = open(f, encoding="utf-8").read()
    if 'name="robots" content="noindex' in s:
        rel = "/" + os.path.relpath(f, DIST).replace("index.html", "")
        if f"<loc>https://mircglow.com{rel}</loc>" in sitemap: problems.append(f"{rel}: noindex page listed in sitemap")
try:
    server = json.load(open(os.path.join(ROOT, "api", "_products.json"), encoding="utf-8"))["products"]
    for slug, sp in server.items():
        f = os.path.join(DIST, "product", slug, "index.html")
        m = re.search(r'property="product:price:amount" content="(\d+)"', open(f, encoding="utf-8").read()) if os.path.exists(f) else None
        if not m: problems.append(f"api/_products.json: no product page for {slug}")
        elif int(m.group(1)) != sp["price"]: problems.append(f"price mismatch {slug}: page {m.group(1)} vs checkout {sp['price']}")
except Exception as e: problems.append(f"api/_products.json unreadable: {e}")

# URL parity with the live WordPress site (published posts, pages, products, categories)
wp = """/ /shop/ /blog/ /about/ /contact/ /faq/ /ingredients/ /privacy/ /terms/ /avocado-cream/ /korean-night-cream/ /skincare-routine-builder/
/skincare-ingredient-glossary/ /skin-quiz/ /returns-refunds/ /shipping-policy/ /track-order/ /bulk-night-cream/ /skincare-gift-sets/
/avocado-cream-hindi/ /korean-night-cream-hindi/ /night-cream-in-kg-mumbai/ /night-cream-in-kg-delhi/ /night-cream-in-kg-bangalore/ /night-cream-in-kg-hyderabad/
/cart/ /checkout/ /my-account/
/product/korean-glass-skin-kit/ /product/night-cream-combo/ /product/day-and-night-cream-combo/ /product/avocado-korean-night-cream/ /product/glutathione-cream/ /product/avocado-night-cream/ /product/avocado-face-cream/
/product-category/night-creams/ /product-category/night-creams/avocado-night-creams/ /product-category/combos/ /category/skincare-guides/ /category/uncategorized/
/how-to-apply-night-cream/ /avocado-cream-for-dry-skin/ /night-cream-for-men/ /night-cream-for-oily-skin/ /best-night-cream-for-glowing-skin/ /kojic-acid-cream-for-dark-spots/
/glass-skin-routine-for-indian-skin/ /kojic-acid-vs-glutathione/ /how-to-use-glutathione-cream/ /how-long-does-glutathione-cream-take-to-work/ /glutathione-cream-side-effects/
/glutathione-cream-benefits/ /avocado-night-cream-side-effects/ /is-avocado-cream-good-for-your-skin/ /which-is-the-no-1-night-cream-in-india/ /is-avocado-cream-good-for-the-face/
/is-avocado-night-cream-good/ /is-avocado-good-for-skin-brightening/ /how-to-make-avocado-night-cream-at-home/ /can-i-use-avocado-night-cream-every-night/
/is-avocado-face-cream-good-for-glowing-skin/ /how-to-build-a-simple-night-skincare-routine/ /glass-skin-routine-steps-for-a-smooth-hydrated-looking-glow/
/glutathione-in-skincare-what-it-is-and-how-it-fits-into-a-routine/ /kojic-acid-in-skincare-a-guide-to-brightening-focused-care/
/korean-skincare-glass-skin-building-a-simple-glow-focused-routine/ /a-brighter-looking-skincare-routine-made-simple/
/sitemap_index.xml /robots.txt /feed/""".split()
served = redirected_n = 0
for u in wp:
    if exists(u): served += 1
    elif redirected(u): redirected_n += 1
    else: problems.append(f"WP URL lost: {u}")

print(f"pages checked: {len(pages)}")
print(f"WordPress URLs: {len(wp)} total, {served} served at the same address, {redirected_n} 301-redirected, {len(wp)-served-redirected_n} lost")
print(f"distinct upload files referenced: {len(uploads)}")
for u in sorted(uploads): print("  ", u)
print(f"problems: {len(problems)}")
for p in problems: print(" -", p)
sys.exit(1 if problems else 0)
