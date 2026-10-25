#!/usr/bin/env python3
"""Mirc Glow static site generator.

Reads body HTML from content/ and writes a complete static site to dist/,
keeping every WordPress URL (trailing-slash permalinks) unchanged.
Run:  python3 build.py
"""
import hashlib, html, json, os, re, shutil
from datetime import date
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "content")
DIST = os.path.join(ROOT, "dist")
SITE = "https://mircglow.com"
BRAND = "Mirc Glow"
PHONE = "+91 99808 81230"
WA_NUM = "919980881230"
TODAY = "2026-10-16"
import importlib.util as _ilu
_gs = _ilu.spec_from_file_location("geo", os.path.join(os.path.dirname(os.path.abspath(__file__)), "content", "geo.py")); GEO = _ilu.module_from_spec(_gs); _gs.loader.exec_module(GEO)

def qa_html(question_answers, heading="Short answers"):
    return f"<h2>{heading}</h2>" + "".join(f"<p><strong>{html.escape(q)}</strong> {html.escape(a)}</p>" for q, a in question_answers)

def at_glance_html():
    rows = "".join(f"<dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd>" for k, v in GEO.AT_A_GLANCE)
    return f'<section class="sec" aria-labelledby="h-glance"><div class="w"><div class="glance"><span class="eyebrow">Mirc Glow at a glance</span><h2 class="sh" id="h-glance">Quick facts about Mirc Glow</h2><dl>{rows}</dl></div></div></section>'

UP = "/wp-content/uploads/2026/09/"

# Razorpay payment links. Paste each product's link here when ready, e.g.
# "glutathione-cream": "https://rzp.io/l/xxxx". Empty = WhatsApp-only ordering.
PAYLINKS = {}

def esc(s): return html.escape(s, quote=True)
def wa(text): return f"https://wa.me/{WA_NUM}?text={quote(text, safe='')}"
def inr(n): return "₹" + f"{n:,}"

WA_HELLO = wa("Hi Mirc Glow, I'd like to order.")
WA_ASK = wa("Hi Mirc Glow, I have a question.")

# ---------------------------------------------------------------- products
PRODUCTS = [
 dict(id=66, slug="avocado-korean-night-cream", name="Avocado Korean Night Cream", size="25 g", grams=25,
      h1="MircGlow Avocado Korean Night Cream for Bright, Even-Looking Skin 25g",
      price=649, mrp=899, img=UP+"4ED0DC3B-11FA-4903-87CC-21E1887C89E5.png", jars=["Avocado Night"],
      ko="아보카도 나이트", tag="Signature", topic="avocado", when="Night",
      meta="For a glass-skin evening", best="Most skin types; a softer, more even-looking complexion",
      bg="linear-gradient(160deg,#FFF7F8,#F4D6DD)", cats=["night-creams","avocado-night-creams"],
      ing=["Avocado","Aloe vera","Vitamin B3 (niacinamide)","Kojic acid"], lasts="About 4 to 6 weeks at a pea-sized amount each night",
      skin="Most skin types, including combination", use="Evening, as the last step",
      rt="Avocado Korean Night Cream 25g: Best for Even-Looking Skin | Mirc Glow",
      rd="Buy Mirc Glow Avocado Korean Night Cream 25g online in India. An overnight cream with avocado, aloe vera, vitamin B3 and kojic acid. Cash on Delivery available.",
      lead="Wake up to skin that feels soft, smooth and hydrated. Our Korean-inspired avocado night cream pairs avocado with aloe vera, vitamin B3 and kojic acid for a more even-looking, glass-skin finish.",
      pts=["Skin feels hydrated and smooth by morning", "Vitamin B3 and kojic acid for a more even-looking tone", "A pea-sized amount a night; a jar lasts 4 to 6 weeks"]),
 dict(id=302, slug="glass-glow-cream", name="Glass Glow Cream", size="30 g", grams=30,
      h1="Mirc Glow Glass Glow Cream with Glutathione, Niacinamide & Alpha Arbutin – 30g",
      price=2499, mrp=2999, img="/wp-content/uploads/2026/10/mirc-glow-glass-glow-cream-glutathione-30g.png", jars=["Glass Glow"],
      ko="글래스 글로우", tag="Premium", topic="glutathione", when="Night (or day with sunscreen)",
      meta="Glutathione with 4 skin-loving actives", best="A complete glass-skin step: glow, hydration and an even-looking tone",
      bg="linear-gradient(160deg,#FBFCF7,#E3ECD8)", cats=["night-creams"], full=True,
      ing=["Glutathione","Niacinamide","Hyaluronic acid","Centella asiatica","Alpha arbutin"], lasts="About 6 to 8 weeks at a pea-sized amount each night",
      skin="Most skin types, including oily and combination", use="Evening as the last step; mornings only with sunscreen",
      rt="Glass Glow Cream with Glutathione & Alpha Arbutin 30g | Mirc Glow",
      rd="Buy Mirc Glow Glass Glow Cream 30g in India: glutathione, niacinamide, hyaluronic acid, centella and alpha arbutin for a radiant glass skin glow. Free shipping.",
      lead="One cream for the whole glass-skin look: glutathione and alpha arbutin for a brighter, more even-looking tone, hyaluronic acid for plump hydration, niacinamide for smoother-looking pores and centella for a calm feel.",
      pts=["Brighter, more even-looking skin with daily sunscreen", "Plump, dewy hydration from hyaluronic acid", "Five actives in one step instead of several serums"]),
 dict(id=24, slug="glutathione-cream", name="Glutathione Cream", size="30 g", grams=30,
      h1="Mirc Glow Glutathione Cream with Vitamin C & Kojic Acid – 30g",
      price=1499, mrp=1999, img=UP+"5D782746-D1F2-496B-8449-5B8149C43004-1.png", jars=["Glutathione"],
      ko="글루타치온", tag="Radiance", topic="glutathione", when="Night",
      meta="With vitamin C and kojic acid", best="Dull or uneven-looking skin; a radiant-looking finish",
      bg="linear-gradient(160deg,#FCF8FF,#E7DDF1)", cats=["night-creams"],
      ing=["Glutathione","Vitamin C","Kojic acid","Aloe vera","Vitamin B3 (niacinamide)"], lasts="About 4 to 6 weeks at a pea-sized amount each night",
      skin="Normal, dry and combination skin; thin layers for oily skin", use="Evening, after cleansing",
      rt="Glutathione Cream with Vitamin C & Kojic Acid 30g: Best for Glow | Mirc Glow",
      rd="Buy Mirc Glow Glutathione Cream 30g online in India. With glutathione, vitamin C and kojic acid for hydrated, radiant-looking skin. Cash on Delivery available.",
      lead="For skin that looks dull and tired. Glutathione, vitamin C and kojic acid work together overnight for a brighter, more radiant-looking finish, with aloe vera and vitamin B3 for comfort.",
      pts=["A radiant-looking glow for dull, tired skin", "Three glow-focused ingredients in one night cream", "Use at night, with sunscreen every morning"]),
 dict(id=23, slug="avocado-night-cream", name="Avocado Night Cream", size="30 g", grams=30,
      h1="Mirc Glow Avocado Night Cream — Kojic Acid, 30g",
      price=649, mrp=949, img=UP+"04BCBF62-EE16-4594-B65C-BDA805C264CB-1.png", jars=["Avocado Rich"],
      ko="아보카도 크림", tag="Best value", topic="avocado", when="Night",
      meta="Rich comfort for dry skin", best="Dry or tight-feeling skin; the best value per gram",
      bg="linear-gradient(160deg,#FFF9F5,#F7E1D6)", cats=["night-creams","avocado-night-creams"],
      ing=["Avocado","Aloe vera","Vitamin B3 (niacinamide)","Kojic acid"], lasts="About 4 to 6 weeks at a pea-sized amount each night",
      skin="Dry and normal skin", use="Evening, as the last step",
      rt="Avocado Night Cream with Kojic Acid 30g: Best for Dry Skin | Mirc Glow",
      rd="Buy Mirc Glow Avocado Night Cream 30g online in India. A rich avocado night cream with aloe vera, vitamin B3 and kojic acid. Free shipping and Cash on Delivery.",
      lead="Our richest cream for dry, tight-feeling skin. Avocado and aloe vera cushion skin overnight, while vitamin B3 and kojic acid help it look more even. The biggest jar and the best value per gram.",
      pts=["Dry, tight skin feels soft and comfortable by morning", "Best value: 30 g for ₹649", "A pea-sized amount a night; a jar lasts 4 to 6 weeks"]),
 dict(id=22, slug="avocado-face-cream", name="Avocado Glow Cream", size="10 g", grams=10,
      h1="Avocado Glow Nourishing Skin Cream – 10g",
      price=349, mrp=449, img=UP+"2DFA2551-B14E-43F6-8929-E39538EC9628-1.png", jars=["Avocado Day"],
      ko="글로우 크림", tag="Try me", topic="avocado", when="Day or night",
      meta="A light first step", best="First-time buyers, travel, and daytime under sunscreen",
      bg="linear-gradient(160deg,#F8FCFA,#DDECE4)", cats=["night-creams","avocado-night-creams"],
      ing=["Avocado","Aloe vera","Vitamin B3 (niacinamide)","Kojic acid"], lasts="About 2 to 3 weeks of daily use",
      skin="All skin types; very little for oily skin", use="Morning under sunscreen, or at night",
      rt="Avocado Face Cream 10g – ₹349, Free Shipping & COD | Mirc Glow",
      rd="Buy Mirc Glow Avocado Face Cream 10g online in India. A nourishing avocado moisturiser for soft, smooth, radiant-looking skin. Cash on Delivery available.",
      lead="A light avocado cream for every day: soft, comfortable skin without a heavy feel, under sunscreen in the morning or on its own at night. The 10 g jar is the easiest way to try Mirc Glow.",
      pts=["Soft, comfortable skin without a heavy feel", "Light enough to wear under sunscreen and make-up", "The easiest way to try Mirc Glow for the first time"]),
 dict(id=301, slug="avocado-glow-cream-15g", name="Avocado Glow Cream 15g", size="15 g", grams=15,
      h1="Mirc Glow Avocado Glow Cream with Aloe Vera – 15g",
      price=399, mrp=599, img="/wp-content/uploads/2026/10/mirc-glow-avocado-glow-cream-15g.png", jars=["Avocado Glow"],
      ko="아보카도 글로우", tag="New", topic="avocado", when="Day or night",
      meta="Avocado and aloe vera, nothing more", best="A simple, gentle daily moisturiser",
      bg="linear-gradient(160deg,#F7FBF2,#DCEBCF)", cats=["night-creams","avocado-night-creams"], full=True,
      ing=["Avocado","Aloe vera"], lasts="About 3 to 4 weeks of daily use",
      skin="All skin types; a thin layer for oily skin", use="Morning under sunscreen, or at night",
      rt="Avocado Glow Cream 15g with Aloe Vera: Gentle Daily Cream | Mirc Glow",
      rd="Buy Mirc Glow Avocado Glow Cream 15g online in India. A whipped avocado and aloe vera moisturiser for soft, fresh-looking skin. Free shipping and COD.",
      lead="Our gentlest avocado cream: whipped avocado and aloe vera, nothing more. A soft, cooling daily moisturiser for anyone who wants a simple formula without kojic acid or niacinamide.",
      pts=["Soft, smooth-feeling skin, morning or night", "Light, cooling feel from aloe vera", "Our simplest formula: no kojic acid or niacinamide"]),
 dict(id=262, slug="day-and-night-cream-combo", name="Day & Night Combo", size="10 g + 30 g", grams=40,
      h1="Day and Night Cream Combo – Mirc Glow Avocado Glow 10g + Avocado Night Cream 30g",
      price=849, mrp=998, img="/wp-content/uploads/2026/10/mirc-glow-day-and-night-cream-combo.png", jars=["Day","Night"],
      ko="데이 & 나이트", tag="Set", topic="avocado", when="Morning and night",
      meta="Avocado Glow 10 g and Avocado Night Cream 30 g", best="A complete, simple moisturising routine",
      bg="linear-gradient(150deg,#FFF6F1,#FBE3D8)", cats=["combos"],
      ing=["Avocado","Aloe vera","Vitamin B3 (niacinamide)","Kojic acid"], lasts="Day cream about 2 to 3 weeks; night cream about 4 to 6 weeks",
      skin="Dry, normal and combination skin", use="Day cream in the morning, night cream in the evening",
      rt="Day and Night Cream Combo: 2 Best Avocado Creams, 1 Routine | Mirc Glow",
      rd="Buy the Mirc Glow day and night cream combo online in India: Avocado Glow 10g for the day and Avocado Night Cream 30g for the night. Free shipping and COD.",
      lead="Two avocado creams: the light Avocado Glow Nourishing Skin Cream for the morning and the rich Avocado Night Cream with Kojic Acid for the evening.",
      pts=["Avocado Glow Nourishing Skin Cream, 10 g (day)","Avocado Night Cream with Kojic Acid, 30 g (night)","Save ₹149 vs buying the two jars separately"],
      parts=["avocado-face-cream","avocado-night-cream"]),
 dict(id=263, slug="night-cream-combo", name="Night Cream Combo", size="30 g + 30 g", grams=60,
      h1="Night Cream Combo – Mirc Glow Glutathione Cream 30g + Avocado Night Cream 30g",
      price=1799, mrp=2148, img="/wp-content/uploads/2026/10/mirc-glow-night-cream-combo.png", jars=["Glutathione","Avocado"],
      ko="나이트 듀오", tag="Set", topic="glutathione", when="Night (alternate or layer)",
      meta="Glutathione Cream and Avocado Night Cream", best="Radiance and deep nourishment in one evening routine",
      bg="linear-gradient(150deg,#FBF4FF,#EADFF3)", cats=["combos"],
      ing=["Glutathione","Vitamin C","Avocado","Kojic acid","Aloe vera","Vitamin B3 (niacinamide)"], lasts="About two months when you alternate the jars",
      skin="Dull, dry or uneven-looking skin", use="Alternate nights at first, then layer",
      rt="Night Cream Combo: 2 Best Creams for Glow and Soft Skin | Mirc Glow",
      rd="Buy the Mirc Glow night cream combo online in India: Glutathione Cream 30g plus Avocado Night Cream 30g for radiant-looking, nourished skin. Free shipping and COD.",
      lead="Our Glutathione Cream with vitamin C and kojic acid, paired with the rich Avocado Night Cream. Radiance-focused care and deep nourishment for your evenings.",
      pts=["Glutathione Cream with Vitamin C and Kojic Acid, 30 g","Avocado Night Cream with Kojic Acid, 30 g","Save ₹349 vs buying the two jars separately"],
      parts=["glutathione-cream","avocado-night-cream"]),
 dict(id=303, slug="glass-glow-night-duo", name="Glass Glow Night Duo", size="30 g + 30 g", grams=60,
      h1="Glass Glow Night Duo – Mirc Glow Glass Glow Cream 30g + Avocado Night Cream 30g",
      price=2699, mrp=3148, img="/wp-content/uploads/2026/10/mirc-glow-glass-glow-night-duo.png", jars=["Glass Glow","Avocado"],
      ko="글래스 듀오", tag="Set", topic="glutathione", when="Night (alternate or layer)",
      meta="Glass Glow Cream and Avocado Night Cream", best="A radiant glass-skin look plus rich overnight comfort",
      bg="linear-gradient(150deg,#F8FBF3,#E1EBD5)", cats=["combos"],
      ing=["Glutathione","Niacinamide","Hyaluronic acid","Centella asiatica","Alpha arbutin","Avocado","Aloe vera","Kojic acid"], lasts="About two months when you alternate the jars",
      skin="Dull, dry or uneven-looking skin", use="Alternate nights at first, then layer",
      rt="Glass Glow Night Duo: Glass Glow + Avocado Night Cream | Mirc Glow",
      rd="Buy the Mirc Glow Glass Glow Night Duo: Glass Glow Cream 30g with glutathione and alpha arbutin plus Avocado Night Cream 30g. Free shipping and COD in India.",
      lead="Our premium Glass Glow Cream paired with the rich Avocado Night Cream: a radiant, even-looking glass-skin look and soft, comfortable skin by morning.",
      pts=["Glass Glow Cream, 30 g","Avocado Night Cream with Kojic Acid, 30 g","Save ₹449 vs buying the two jars separately"],
      parts=["glass-glow-cream","avocado-night-cream"]),
 dict(id=264, slug="korean-glass-skin-kit", name="Korean Glass Skin Kit", size="30 g + 25 g + 10 g", grams=65,
      h1="Korean Glass Skin Kit – 3 Mirc Glow Korean-Inspired Creams",
      price=1999, mrp=2497, img="/wp-content/uploads/2026/10/mirc-glow-korean-glass-skin-kit.png", jars=["Glow","Night","Day"],
      ko="유리 피부 키트", tag="Full ritual", topic="routine", when="Morning and night",
      meta="Three creams for a complete routine", best="Beginners who want the full morning and night routine",
      bg="linear-gradient(150deg,#FFF5F7,#F3D3DB)", cats=["combos"],
      ing=["Glutathione","Vitamin C","Avocado","Kojic acid","Aloe vera","Vitamin B3 (niacinamide)"], lasts="Night creams about two months together; day cream about 2 to 3 weeks",
      skin="All skin types; thin layers for oily skin", use="Day cream in the morning; night creams in the evening",
      rt="Korean Glass Skin Kit: 3 Best Creams for a Dewy Glow | Mirc Glow",
      rd="Buy the Mirc Glow Korean glass skin kit online in India: 3 Korean-inspired creams for a complete morning and night routine. Free shipping and Cash on Delivery.",
      lead="Three Korean-inspired creams: the Glutathione Cream for radiance, the Avocado Korean Night Cream for nourishment, and the Avocado Glow cream for the day.",
      pts=["Glutathione Cream, 30 g","Avocado Korean Night Cream, 25 g","Avocado Glow Nourishing Skin Cream, 10 g","Save ₹498 vs buying the three jars separately"],
      parts=["glutathione-cream","avocado-korean-night-cream","avocado-face-cream"]),
]
PBY = {p["slug"]: p for p in PRODUCTS}
SINGLES = [p for p in PRODUCTS if "parts" not in p]
SETS = [p for p in PRODUCTS if "parts" in p]
CATS = {
 "night-creams": dict(name="Night Creams", h1="Night cream for face", ko="나이트 크림 · NIGHT CREAMS", parent=None,
     rt="Night Cream for Face: Buy Online in India | Mirc Glow",
     rd="Buy night cream online in India from ₹349: avocado, glutathione and Glass Glow night creams. Choose by skin type and age. Free shipping and Cash on Delivery.",
     intro="Korean-inspired creams for the last step of your evening routine. Most contain aloe vera, vitamin B3 and kojic acid, and each has its own job."),
 "avocado-night-creams": dict(name="Avocado Night Creams", h1="Avocado night creams", ko="아보카도 · AVOCADO CARE", parent="night-creams",
     rt="Avocado Night Creams for Nourishing Evening Care | Mirc Glow",
     rd="Shop Mirc Glow avocado night creams and avocado face creams in India, from ₹349. Avocado with aloe vera, vitamin B3 and kojic acid. Free shipping and COD.",
     intro="Rich, cushioned avocado creams for skin that feels dry or tight after washing. Pick by jar size and the time of day you want to use it."),
 "combos": dict(name="Combos and Kits", h1="Combos and kits", ko="세트 · SETS", parent=None,
     rt="Combos and Kits - Mirc Glow",
     rd="Mirc Glow skincare combos and kits: our creams paired into simple routines at a lower price than buying them separately.",
     intro="Our creams paired into simple routines. Every set costs less than buying the same jars one by one."),
}
def cat_url(c):
    return f"/product-category/{c}/" if not CATS[c]["parent"] else f"/product-category/{CATS[c]['parent']}/{c}/"

# ---------------------------------------------------------------- posts
D1, D2, D3, D4 = "2026-09-19", "2026-09-23", "2026-10-03", "2026-10-04"
HUB = {  # consolidated post -> hub it now points to
 "is-avocado-cream-good-for-the-face": "is-avocado-cream-good-for-your-skin",
 "is-avocado-good-for-skin-brightening": "is-avocado-cream-good-for-your-skin",
 "is-avocado-face-cream-good-for-glowing-skin": "is-avocado-cream-good-for-your-skin",
 "a-brighter-looking-skincare-routine-made-simple": "is-avocado-night-cream-good",
 "glass-skin-routine-steps-for-a-smooth-hydrated-looking-glow": "glass-skin-routine-for-indian-skin",
 "korean-skincare-glass-skin-building-a-simple-glow-focused-routine": "glass-skin-routine-for-indian-skin",
 "kojic-acid-in-skincare-a-guide-to-brightening-focused-care": "kojic-acid-cream-for-dark-spots",
 "glutathione-in-skincare-what-it-is-and-how-it-fits-into-a-routine": "glutathione-cream-benefits",
}
P = lambda slug, title, ex, rt, rd, d, topic: dict(slug=slug, title=title, ex=ex, rt=rt, rd=rd, date=d, topic=topic)
POSTS = [
 P("how-to-apply-night-cream","How to Apply Night Cream the Right Way","Most people use too much night cream and apply it at the wrong moment. Here is how to apply night cream properly, in about a minute.","How to Use Night Cream: 6 Steps to Apply It Right | Mirc Glow","Most people use too much and apply it at the wrong time. Learn how to apply night cream in 6 easy steps, how much to use, and what order to follow.",D4,"night"),
 P("avocado-day-cream","Avocado Day Cream: How to Use It in the Morning","Can you use avocado cream in the day? Yes. How an avocado day cream differs from a night cream, how to use it under sunscreen, and which skin types need one.","Avocado Day Cream: How to Use It and Day vs Night Cream | Mirc Glow","Avocado day cream explained: how to use avocado cream in the morning under sunscreen, avocado day vs night cream, and which skin types need one.","2026-10-16","avocado"),
 P("avocado-cream-for-dry-skin","Avocado Cream for Dry Skin: Why It Works and How to Use It","Dry, tight skin after washing? Here is why avocado cream for dry skin makes sense, how to apply it so it actually helps, and what to change in winter.","Avocado Night Cream for Dry Skin: 5 Ways to Use It | Mirc Glow","Dry, tight skin after washing? See why avocado cream for dry skin makes sense, 5 simple ways to use it so it really helps, and what to change in winter.",D4,"avocado"),
 P("night-cream-for-men","Night Cream for Men: A Simple Guide to Getting Started","A no-fuss guide to night cream for men: why it helps, how to choose one, and a two-minute evening routine.","Night Cream for Men: 5 Easy Steps to Better-Looking Skin | Mirc Glow","A no-fuss guide to night cream for men in India: why it helps, how to choose one, and 5 easy steps for a two-minute evening routine.",D4,"night"),
 P("night-cream-for-oily-skin","Night Cream for Oily Skin: How to Choose and Use One","Yes, oily skin needs a night cream. Learn how to choose a night cream for oily skin, how much to use, and the mistakes that cause shine and breakouts.","Best Night Cream for Oily Skin (2026): 6 Rules + Picks | Mirc Glow","Does oily skin need a night cream? Yes. Learn 6 simple rules for choosing and using a night cream for oily skin without shine, heaviness or breakouts.",D4,"night"),
 P("best-night-cream-for-glowing-skin","Best Night Cream in India (2026): How to Choose for Glowing Skin","Looking for the best night cream? Quick picks by skin type and budget, the ingredients to look for, and how to use it for glowing skin in India.","Best Night Cream in India (2026): Picks by Skin Type | Mirc Glow","Looking for the best night cream in India? See quick picks by skin type and budget, the 7 things to check, the ingredients that matter, and how to use it.",D3,"night"),
 P("kojic-acid-cream-for-dark-spots","Kojic Acid Cream for Dark Spots: How to Use It and What to Expect","Kojic acid cream for dark spots: what it is, how to use it, how long it takes, and how to avoid irritation.","Kojic Acid Cream for Dark Spots: 7 Tips for Best Results | Mirc Glow","Using kojic acid cream for dark spots? Learn what it is, how to apply it, how long it takes, and 7 simple tips to get better results without irritation.",D3,"kojic"),
 P("glass-skin-routine-for-indian-skin","Glass Skin Routine for Indian Skin: 6 Simple Steps","A glass skin routine for Indian skin, adapted for heat, humidity and strong sun. Six simple steps for morning and night.","Glass Skin Routine for Indian Skin: 6 Simple Steps That Work | Mirc Glow","Follow this glass skin routine for Indian skin: 6 simple steps adapted for heat, humidity and strong sun, with morning and night routines for every skin type.",D3,"routine"),
 P("kojic-acid-vs-glutathione","Kojic Acid vs Glutathione: Which Is Right for Your Skin?","Kojic acid vs glutathione: what each ingredient is, how they differ, whether you can use them together, and which one suits your skin.","Kojic Acid vs Glutathione: 5 Key Differences Explained | Mirc Glow","Kojic acid vs glutathione: learn the 5 key differences, which ingredient suits your skin goal, and whether you can safely use both together.",D3,"kojic"),
 P("how-to-use-glutathione-cream","How to Use Glutathione Cream: A Step-by-Step Routine","How to use glutathione cream the right way: when to apply it, how much to use, what to pair it with, and the mistakes to avoid.","How to Use Glutathione Cream: 5 Easy Steps for Best Results | Mirc Glow","Learn how to use glutathione cream in 5 easy steps: when to apply it, how much to use, what to pair it with, and the common mistakes to avoid.",D3,"glutathione"),
 P("how-long-does-glutathione-cream-take-to-work","How Long Does Glutathione Cream Take to Work?","How long does glutathione cream take to work? A week-by-week timeline of what to expect, and five habits that help.","How Long Does Glutathione Cream Take to Work? 12-Week Guide | Mirc Glow","How long does glutathione cream take to work? See an honest week-by-week timeline over 12 weeks, plus 5 simple habits that help you get better results.",D3,"glutathione"),
 P("glutathione-cream-side-effects","Glutathione Cream Side Effects: What Is Known and How to Stay Safe","Glutathione cream side effects are uncommon and usually mild. Learn what to watch for, who should be careful, and how to start safely.","Glutathione Cream Side Effects: 4 Things to Watch For | Mirc Glow","Glutathione cream side effects are uncommon and usually mild. Learn the 4 things to watch for, who should be careful, and how to patch test and start safely.",D3,"glutathione"),
 P("glutathione-cream-benefits","Glutathione Cream Benefits: A Simple Guide for Beginners","Glutathione cream benefits explained in plain words: what it can do for how your skin looks, what it cannot do, and how to get the most from it.","Glutathione Cream Benefits: 6 Honest Facts for Beginners | Mirc Glow","Glutathione cream benefits explained in plain words: 6 honest facts on what it can do for how your skin looks, what it cannot do, and how to use it well.",D3,"glutathione"),
 P("avocado-night-cream-side-effects","Avocado Night Cream Side Effects: What to Know Before You Start","Avocado night cream side effects are uncommon and usually mild. Learn who should be careful, how to patch test, and how to start safely.","Avocado Night Cream Side Effects: 5 Things to Know | Mirc Glow","Avocado night cream side effects are uncommon and usually mild. Learn the 5 things to watch for, who should be careful, and how to patch test before you start.",D3,"avocado"),
 P("is-avocado-cream-good-for-your-skin","Is Avocado Cream Good for Your Skin and Face?","Is avocado cream good for your skin and face? What it can and cannot do, who it suits, whether it helps skin look brighter, and how to use it morning and night.","Is Avocado Cream Good for Your Skin and Face? Honest Guide | Mirc Glow","Is avocado cream good for your skin and face? What it can and cannot do, which skin types it suits, whether it helps skin look brighter, and how to use it.",D2,"avocado"),
 P("which-is-the-no-1-night-cream-in-india","Which Is the No. 1 Night Cream in India?","A practical guide to choosing a night cream that suits your skin type, comfort preferences, and glow-focused routine.","Which Is the No. 1 Night Cream in India? How to Choose | Mirc Glow","Which is the no. 1 night cream in India? Learn what to consider when choosing a night cream based on ingredients, skin needs, texture and routine.",D2,"night"),
 P("is-avocado-cream-good-for-the-face","Is Avocado Cream Good for the Face?","Learn how avocado cream can support a comfortable, moisturized-looking complexion and how to choose a formula that fits your routine.","Is Avocado Cream Good for the Face? | Mirc Glow","Is avocado cream good for the face? Learn how avocado-based creams can fit into a simple skincare routine and what to consider when choosing one.",D2,"avocado"),
 P("is-avocado-night-cream-good","Is Avocado Night Cream Good?","Learn how avocado night cream can support a comfortable, moisturized-looking complexion and how to choose a formula for your evening routine.","Avocado Night Cream Benefits: Is It Good for Skin? | Mirc Glow","Is avocado night cream good for your skincare routine? Learn about its potential benefits, how to use it, and what to consider when choosing a formula.",D2,"avocado"),
 P("is-avocado-good-for-skin-brightening","Is Avocado Good for Skin Brightening?","Learn how avocado cream can support a comfortable, moisturized-looking complexion and fit into a simple glow-focused skincare routine.","Is Avocado Good for Skin Brightening? | Mirc Glow","Is avocado good for skin brightening? Learn what avocado can offer in a skincare routine and what to consider when choosing an avocado-based formula.",D2,"avocado"),
 P("how-to-make-avocado-night-cream-at-home","How to Make Avocado Night Cream at Home?","Learn how to make a simple fresh avocado night cream at home, how to use it safely, and when a ready-made formula may be more practical.","How to Make Avocado Night Cream at Home? | Mirc Glow","Learn how to make avocado night cream at home, explore simple ingredients and skincare considerations, and discover what to know before using homemade formulas.",D2,"avocado"),
 P("can-i-use-avocado-night-cream-every-night","Can I Use Avocado Night Cream Every Night?","Can you use avocado night cream every night? Learn how to introduce it into your evening routine, when to adjust use, and how to choose a comfortable finish.","Can I Use Avocado Night Cream Every Night? | Mirc Glow","Can you use avocado night cream every night? Learn how to use night cream comfortably and what to consider for your evening skincare routine.",D2,"avocado"),
 P("is-avocado-face-cream-good-for-glowing-skin","Is Avocado Face Cream Good for Glowing Skin?","Discover whether avocado face cream can support a glowing-looking complexion, what to look for in a formula, and how to use it in a simple skincare routine.","Is Avocado Face Cream Good for Glowing Skin? | Mirc Glow","Can avocado face cream help skin look glowing? What avocado does, what it cannot do, and how to use it in a simple glow routine.",D2,"avocado"),
 P("how-to-build-a-simple-night-skincare-routine","How to Build a Simple Night Skincare Routine","A calm, easy evening routine in four steps: cleanse, tone, treat and moisturise. What to use, in what order, and how long it takes.","Simple Night Skincare Routine: 4 Easy Steps | Mirc Glow","Build a simple night skincare routine in 4 easy steps: cleanse, tone, treat and moisturise. What to use, in what order, and how long it takes.",D1,"routine"),
 P("glass-skin-routine-steps-for-a-smooth-hydrated-looking-glow","Glass Skin Routine: Steps for a Smooth, Hydrated-Looking Glow","Simple steps for a smooth, hydrated-looking glow inspired by a glass-skin ritual.","Glass Skin Routine Steps for a Smooth, Dewy Look | Mirc Glow","The basic glass skin routine steps for a smooth, hydrated-looking glow, and how to keep the routine light enough to follow every day.",D1,"routine"),
 P("glutathione-in-skincare-what-it-is-and-how-it-fits-into-a-routine","Glutathione in Skincare: What It Is and How It Fits Into a Routine","An approachable guide to glutathione in brightening-focused skincare routines.","Glutathione in Skincare: What It Is and How to Use It | Mirc Glow","What glutathione is, why it appears in brightening-focused skincare, and where it fits in a simple morning and night routine.",D1,"glutathione"),
 P("kojic-acid-in-skincare-a-guide-to-brightening-focused-care","Kojic Acid in Skincare: A Guide to Brightening-Focused Care","Learn how kojic acid can fit into a considered, brightening-focused skincare routine.","Kojic Acid in Skincare: What It Does and How to Use It | Mirc Glow","What kojic acid is, why it is used in skincare for a more even-looking tone, and how to add it to your routine without irritation.",D1,"kojic"),
 P("korean-skincare-glass-skin-building-a-simple-glow-focused-routine","Korean Skincare & Glass Skin: Building a Simple Glow-Focused Routine","Build a simple Korean skincare-inspired routine for a smooth, hydrated-looking glow.","Korean Skincare and Glass Skin: A Simple Routine | Mirc Glow","What Korean skincare and glass skin really mean, and how to build a simple glow-focused routine without ten steps.",D1,"routine"),
 P("a-brighter-looking-skincare-routine-made-simple","Avocado Night Cream: Benefits for Hydrated, Nourished-Looking Skin","Discover how avocado-inspired night care can help skin feel hydrated, soft, and nourished-looking.","Avocado Night Cream Benefits for Soft, Nourished Skin | Mirc Glow","The main avocado night cream benefits for dry and tired-looking skin, how it works overnight, and how to use it for the best feel by morning.",D1,"avocado"),
]
POST_BY = {p["slug"]: p for p in POSTS}
LIVE_POSTS = [p for p in POSTS if p["slug"] not in HUB]
TOPICS = {
 "avocado": ("Avocado", "avocado-korean-night-cream"),
 "glutathione": ("Glutathione", "glutathione-cream"),
 "kojic": ("Kojic acid", "avocado-korean-night-cream"),
 "routine": ("Routines", "korean-glass-skin-kit"),
 "night": ("Night cream", "avocado-korean-night-cream"),
 "concern": ("Dark spots & tone", "glass-glow-cream"),
 "ingredient": ("Ingredients", "glass-glow-cream"),
}

# ---------------------------------------------------------------- pages
G = lambda slug, title, rt, rd, kind, crumb=None, img=None, lang="en", alt=None: dict(slug=slug, title=title, rt=rt, rd=rd, kind=kind, crumb=crumb or title, img=img, lang=lang, alt=alt)
PAGES = [
 G("avocado-cream","Avocado Cream","Avocado Cream: 4 Best Picks for Soft, Nourished Skin | Mirc Glow","Shop avocado cream by Mirc Glow in India. Compare 4 avocado creams with aloe vera, vitamin B3 and kojic acid, from ₹349, and find the right one for your skin.","legacy",img=UP+"04BCBF62-EE16-4594-B65C-BDA805C264CB.png",alt="avocado-cream-hindi"),
 G("korean-night-cream","Korean Night Cream","Korean Night Cream: 3 Best Picks for a Glass Skin Glow | Mirc Glow","Shop Korean night cream by Mirc Glow in India. Compare 3 Korean-inspired night creams with avocado, vitamin B3 and kojic acid, from ₹649, and learn how to use them.","legacy",img=UP+"4ED0DC3B-11FA-4903-87CC-21E1887C89E5.png",alt="korean-night-cream-hindi"),
 G("avocado-cream-hindi","एवोकाडो क्रीम (Avocado Cream in Hindi)","एवोकाडो क्रीम के फायदे और इस्तेमाल का तरीका | Mirc Glow","एवोकाडो क्रीम क्या है, चेहरे के लिए इसके फायदे क्या हैं और इसे कैसे लगाएं? आसान हिंदी में जानकारी, साथ में Mirc Glow की 3 एवोकाडो क्रीम की तुलना।","plain",crumb="एवोकाडो क्रीम",lang="hi",alt="avocado-cream",img=UP+"04BCBF62-EE16-4594-B65C-BDA805C264CB.png"),
 G("avocado-night-cream-benefits-hindi","एवोकाडो नाइट क्रीम के फायदे (Avocado Night Cream Ke Fayde)","Avocado Night Cream Benefits in Hindi: 7 फायदे | Mirc Glow","एवोकाडो नाइट क्रीम के फायदे (avocado night cream ke fayde) आसान हिंदी में: रात भर नमी, मुलायम त्वचा, कैसे लगाएं, किस स्किन के लिए सही है और FAQ।","plain",crumb="एवोकाडो नाइट क्रीम के फायदे",lang="hi",img=UP+"04BCBF62-EE16-4594-B65C-BDA805C264CB-1.png"),
 G("korean-night-cream-hindi","कोरियन नाइट क्रीम (Korean Night Cream in Hindi)","कोरियन नाइट क्रीम क्या है? फायदे और लगाने का सही तरीका | Mirc Glow","कोरियन नाइट क्रीम क्या होती है, इसके फायदे क्या हैं और इसे कैसे लगाएं? आसान हिंदी में पूरी जानकारी, साथ में Mirc Glow की 3 नाइट क्रीम की तुलना।","plain",crumb="कोरियन नाइट क्रीम",lang="hi",alt="korean-night-cream",img=UP+"4ED0DC3B-11FA-4903-87CC-21E1887C89E5.png"),
 G("skin-quiz","Skin Quiz","Skin Quiz: Find Your Best Cream in 4 Easy Questions | Mirc Glow","Take the Mirc Glow skin quiz. Answer 4 easy questions about your skin and get a cream recommendation with tips on how to use it.","legacy"),
 G("skincare-routine-builder","Skincare Routine Builder","Skincare Routine Builder: 5 Easy Korean-Style Routines | Mirc Glow","Use our skincare routine builder to get a simple morning and night routine for dry, oily, combination, normal or sensitive skin, Korean style.","legacy"),
 G("skincare-ingredient-glossary","Skincare Ingredient Glossary","Skincare Ingredient Glossary: 15 Essential K-Beauty Actives | Mirc Glow","A plain-English skincare ingredient glossary. Learn what PDRN, exosomes, tranexamic acid, niacinamide, kojic acid, glutathione and 9 more actually do.","legacy"),
 G("skincare-gift-sets","Diwali Skincare Gift Sets","Diwali Skincare Gift Sets: 3 Best Glow Kits from ₹849 | Mirc Glow","Looking for a Diwali skincare gift? Choose from 3 Mirc Glow gift sets from ₹849, with avocado night creams and glutathione cream. Free shipping and Cash on Delivery.","legacy",crumb="Gift sets",img=UP+"2DFA2551-B14E-43F6-8929-E39538EC9628-1.png"),
 G("avocado-cream-in-kg","Avocado Cream in Kg","Avocado Night Cream 1 Kg & Avocado Cream in Kg: Bulk | Mirc Glow","Buy avocado night cream 1 kg and avocado cream in kg from Mirc Glow. Bulk wholesale for salons, parlours and resellers across India. Price per kg on WhatsApp.","plain",crumb="Avocado Cream in Kg",img="/wp-content/uploads/2026/10/mirc-glow-avocado-cream-1kg-tubs.jpg",alt="avocado-cream-in-kg-hindi"),
 G("avocado-cream-in-kg-hindi","एवोकाडो क्रीम 1 किलो (Avocado Cream in Kg)","एवोकाडो क्रीम 1 किलो: थोक में एवोकाडो नाइट क्रीम | Mirc Glow","एवोकाडो क्रीम और एवोकाडो नाइट क्रीम 1 किलो या ज़्यादा थोक में खरीदें। सैलून, पार्लर और रीसेलर के लिए पूरे भारत में डिलीवरी। किलो का रेट WhatsApp पर।","plain",crumb="एवोकाडो क्रीम 1 किलो",img="/wp-content/uploads/2026/10/mirc-glow-avocado-cream-1kg-tubs.jpg",lang="hi",alt="avocado-cream-in-kg"),
 G("bulk-night-cream","Bulk Night Cream in Kg","Night Cream in Kg: Bulk Avocado Night Cream Wholesale Supply | Mirc Glow","Buy night cream in kg from Mirc Glow. Avocado night cream in kg and glutathione cream wholesale for salons, resellers and brands in India. Get a quote on WhatsApp.","legacy",crumb="Bulk orders",img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"),
 G("night-cream-in-kg-mumbai","Night Cream in Kg in Mumbai","Night Cream in Kg in Mumbai: Wholesale Bulk Supply | Mirc Glow","Night cream in kg in Mumbai for salons, parlours and resellers. Avocado night cream wholesale by the kilo or in jars. Get the price per kg on WhatsApp.","legacy",crumb="Mumbai",img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"),
 G("night-cream-in-kg-delhi","Night Cream in Kg in Delhi","Night Cream in Kg in Delhi: Wholesale Bulk Supply | Mirc Glow","Night cream in kg in Delhi NCR for salons, parlours and resellers. Avocado night cream wholesale by the kilo or in jars. Ask for the price per kg.","legacy",crumb="Delhi",img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"),
 G("night-cream-in-kg-bangalore","Night Cream in Kg in Bangalore","Night Cream in Kg in Bangalore: Wholesale Bulk Supply | Mirc Glow","Night cream in kg in Bangalore from a Karnataka brand. Avocado night cream wholesale for salons, resellers and new brands. Ask for the price per kg.","legacy",crumb="Bangalore",img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"),
 G("night-cream-in-kg-hyderabad","Night Cream in Kg in Hyderabad","Night Cream in Kg in Hyderabad: Wholesale Bulk Supply | Mirc Glow","Night cream in kg in Hyderabad for salons, bridal studios and resellers. Avocado night cream wholesale by the kilo or in jars. Get the price per kg.","legacy",crumb="Hyderabad",img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"),
 G("about","About","About Mirc Glow | Korean-Inspired Skincare from Karnataka","Mirc Glow is a skincare brand from Bhatkal, Karnataka, making avocado and glutathione creams with aloe vera, vitamin B3 and kojic acid. Meet the brand.","legacy",crumb="About us"),
 G("ingredients","Ingredients","Our Ingredients: Glutathione, Kojic Acid and Avocado | Mirc Glow","The ingredients in Mirc Glow creams, glutathione, kojic acid, vitamin C, vitamin B3, avocado and aloe vera, and what each one does for how skin looks and feels.","legacy"),
 G("faq","FAQ","FAQ: Orders, Delivery, Returns and Using Our Creams | Mirc Glow","Answers to common questions about Mirc Glow: Cash on Delivery, free shipping, 7-day returns, which cream to choose and how to use it safely.","legacy"),
 G("contact","Contact","Contact Mirc Glow | WhatsApp +91 99808 81230","Contact Mirc Glow for order help, product advice or bulk orders. WhatsApp or call +91 99808 81230. Azad Nagar, Bhatkal, Karnataka.","legacy"),
 G("about-the-author","About the Author","About the Author: Mohammed Nihal, Founder | Mirc Glow","Mohammed Nihal runs Mirc Glow from Bhatkal, Karnataka, and writes our guides on night creams, avocado skincare, glutathione and kojic acid, and how they are made.","plain",crumb="About the author"),
 G("editorial-policy","Editorial Policy","Editorial Policy: How We Write Our Skincare Guides | Mirc Glow","How Mirc Glow writes, fact-checks and updates its skincare guides, who writes them, and the claims we will never make about our creams.","plain"),
 G("track-order","Track Your Order","Track Your Order | Mirc Glow","Track your Mirc Glow order. Find your tracking number, check your delivery status, and get help on WhatsApp if your parcel is delayed.","plain"),
 G("shipping-policy","Shipping Policy","Shipping Policy | Mirc Glow","Mirc Glow offers free shipping across India with delivery in 3 to 7 days. Cash on Delivery and secure online payment are available.","plain"),
 G("returns-refunds","Returns and Refunds","Returns and Refunds Policy | Mirc Glow","Mirc Glow accepts returns of unopened, sealed jars within 7 days of delivery, and of damaged, wrong or expired items. Refunds are made in 5 to 7 working days.","plain"),
 G("privacy","Privacy Policy","Privacy Policy | Mirc Glow","How Mirc Glow collects, uses and protects your personal information when you visit mircglow.com or place an order.","plain"),
 G("terms","Terms and Conditions","Terms and Conditions | Mirc Glow","The terms that apply when you use mircglow.com or order from Mirc Glow, including pricing, payment, delivery and returns.","plain"),
]
CITY = {"avocado-cream-in-kg","avocado-cream-in-kg-hindi","night-cream-in-kg-mumbai","night-cream-in-kg-delhi","night-cream-in-kg-bangalore","night-cream-in-kg-hyderabad"}

# ---------------------------------------------------------------- scheduled content (content/plan/schedule.json)
# Each item goes live on its date (India time). Vercel Cron (api/publish.js) starts a fresh Vercel build every morning; Vercel runs build.py itself, so no GitHub activity is needed.
import datetime as _dt
NOW_IST = os.environ.get("MG_DATE") or (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=5, minutes=30)).date().isoformat()
PLAN = json.load(open(os.path.join(SRC, "plan", "schedule.json"), encoding="utf-8"))
UNPUBLISHED = {m["slug"] for m in PLAN if m["date"] > NOW_IST}
for _m in PLAN:
    if _m["slug"] in UNPUBLISHED: continue
    if _m["kind"] == "post":
        POSTS.append(P(_m["slug"], _m["title"], _m["ex"], _m["rt"], _m["rd"], _m["date"], _m["topic"]))
        if _m.get("quick"): GEO.QUICK[_m["slug"]] = (_m["quick"], _m.get("facts", []))
    elif _m["kind"] == "hindi":
        PAGES.append(G(_m["slug"], _m["title"], _m["rt"], _m["rd"], "plain", crumb=_m["title"].split("(")[0].strip(), lang="hi"))
    elif _m["kind"] == "regional":
        PAGES.append(G(_m["slug"], _m["title"], _m["rt"], _m["rd"], "plain", crumb=_m["title"].split("(")[0].strip(), lang=_m["lang"]))
    elif _m["kind"] == "bulk":
        PAGES.append(G(_m["slug"], _m["title"], _m["rt"], _m["rd"], "plain", crumb=_m["title"], img="/wp-content/uploads/2026/10/mirc-glow-avocado-cream-1kg-tubs.jpg"))
        CITY.add(_m["slug"])
    elif _m["kind"] == "city":
        PAGES.append(G(_m["slug"], _m["title"], _m["rt"], _m["rd"], "legacy", crumb=_m["title"].replace("Night Cream in Kg in ", ""), img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"))
        CITY.add(_m["slug"])
POST_BY = {p["slug"]: p for p in POSTS}
LIVE_POSTS = [p for p in POSTS if p["slug"] not in HUB]

# ---------------------------------------------------------------- helpers
def read(path):
    with open(path, encoding="utf-8") as f: return f.read()

def write(urlpath, content):
    if UNPUBLISHED and isinstance(content, str) and "<a " in content:
        # links to scheduled pages that are not out yet show as plain text until their release day
        content = re.sub(r'<a [^>]*href="(?:https://mircglow\.com)?/(%s)/"[^>]*>(.*?)</a>' % "|".join(map(re.escape, UNPUBLISHED)), r"\2", content, flags=re.S)
    rel = urlpath.strip("/")
    out = os.path.join(DIST, rel, "index.html") if not rel.endswith((".xml",".txt",".html",".json")) else os.path.join(DIST, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f: f.write(content)

def slugify(t):
    t = re.sub(r"<[^>]+>", "", t); t = html.unescape(t).lower()
    t = re.sub(r"[^a-z0-9ऀ-ॿ]+", "-", t).strip("-")
    return t[:60] or "section"

def strip_tags(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()

def add_h2_ids(body):
    seen, toc = set(), []
    def rep(m):
        attrs, inner = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        hid = idm.group(1) if idm else slugify(inner)
        base, n = hid, 2
        while hid in seen: hid = f"{base}-{n}"; n += 1
        seen.add(hid); toc.append((hid, strip_tags(inner)))
        if idm: return m.group(0)
        return f'<h2 id="{hid}"{attrs}>{inner}</h2>'
    return re.sub(r"<h2([^>]*)>(.*?)</h2>", rep, body, flags=re.S), toc

def lazy_imgs(body):
    def rep(m):
        tag = m.group(0)
        if "loading=" not in tag and "fetchpriority" not in tag: tag = tag.replace("<img ", '<img loading="lazy" ', 1)
        if "decoding=" not in tag: tag = tag.replace("<img ", '<img decoding="async" ', 1)
        if "width=" not in tag:
            src = re.search(r'src="(/[^"]+)"', tag)
            fp = src and os.path.join(ROOT, src.group(1).lstrip("/"))
            if fp and os.path.exists(fp):
                try:
                    from PIL import Image as _I
                    w, h = _I.open(fp).size
                    tag = tag.replace("<img ", f'<img width="{w}" height="{h}" ', 1)
                except Exception: pass
        return tag
    body = re.sub(r"<img [^>]*>", rep, body)
    # serve a light WebP copy of big PNG/JPG content images (creates it once, next to the original)
    def pic(m):
        pre, tag = m.group(1), m.group(2)
        if pre.rstrip().endswith("<picture>"): return m.group(0)
        src = re.search(r'src="(/wp-content/[^"]+\.(?:png|jpe?g))"', tag)
        if not src: return m.group(0)
        fp = os.path.join(ROOT, src.group(1).lstrip("/")); wp = re.sub(r"\.(png|jpe?g)$", ".mg.webp", fp)
        if not os.path.exists(fp): return m.group(0)
        if not os.path.exists(wp):
            try:
                from PIL import Image as _I
                im = _I.open(fp); im.thumbnail((1200, 1200)); im.save(wp, "WEBP", quality=80, method=6)
            except Exception: return m.group(0)
        w = re.sub(r"\.(png|jpe?g)$", ".mg.webp", src.group(1))
        return f'{pre}<picture><source srcset="{w}" type="image/webp">{tag}</picture>'
    return re.sub(r"(.{0,12})(<img [^>]*>)", pic, body, flags=re.S)

def build_llms_full():
    """One plain-text file with every indexable page's short answer, key facts and FAQs, for AI assistants."""
    import html as _h
    def txt(x): return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", x))).strip()
    rows = []
    for root, _, files in os.walk(DIST):
        if "index.html" not in files: continue
        s = open(os.path.join(root, "index.html"), encoding="utf-8").read()
        if 'name="robots" content="noindex' in s: continue
        url = SITE + "/" + os.path.relpath(root, DIST).replace(".", "").strip("/") + "/"
        url = url.replace("//", "/").replace("https:/", "https://") if url != SITE + "//" else SITE + "/"
        c = re.search(r'<link rel="canonical" href="([^"]+)"', s)
        if c and c.group(1).rstrip("/") != url.rstrip("/"): continue
        t = re.search(r"<title>(.*?)</title>", s, re.S)
        q = re.search(r'<aside class="quick"[^>]*>.*?<p>(.*?)</p>(?:<ul>(.*?)</ul>)?', s, re.S)
        if not q:
            q2 = re.search(r"<p><strong>(?:Short answer|Quick answer|छोटा जवाब):?</strong>:?(.*?)</p>", s, re.S)
        faqs = []
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try: d = json.loads(m.group(1))
            except Exception: continue
            for node in (d.get("@graph", [d]) if isinstance(d, dict) else d):
                if isinstance(node, dict) and node.get("@type") == "FAQPage":
                    faqs += [(e["name"], e["acceptedAnswer"]["text"]) for e in node.get("mainEntity", [])]
        block = [f"## {txt(t.group(1)) if t else url}", f"URL: {url}"]
        if q:
            block.append(f"Short answer: {txt(q.group(1))}")
            if q.group(2): block += [f"- {txt(x)}" for x in re.findall(r"<li>(.*?)</li>", q.group(2), re.S)]
        elif q2: block.append(f"Short answer: {txt(q2.group(1))}")
        for a, b in faqs[:8]: block.append(f"Q: {txt(a)}\nA: {txt(b)}")
        rows.append((0 if "/product/" in url else 1 if url.count("/") <= 4 else 2, url, "\n".join(block)))
    rows.sort()
    head_ = [f"# {BRAND}: full answers file", "", f"> Every public page on {SITE} with its short answer, key facts and common questions, so AI assistants can read and quote the site in one go. Prices in INR. Mirc Glow creams are cosmetics: they do not change natural skin tone or treat skin conditions. Orders: WhatsApp {PHONE}.", f"Summary index: {SITE}/llms.txt", "", ""]
    write("/llms-full.txt", "\n".join(head_) + "\n\n".join(r[2] for r in rows) + "\n")

def faqs_from(body):
    """Pull Q&A pairs from <details>, FAQ-style h3 lists, and 'Short answers' blocks."""
    out = []
    for q, a in re.findall(r"<details[^>]*>\s*<summary>(.*?)</summary>(.*?)</details>", body, flags=re.S):
        out.append((strip_tags(q), strip_tags(a)))
    for sec in re.finditer(r"<h2[^>]*>([^<]*(?:FAQ|[Qq]uestions|Short answers|सवाल)[^<]*)</h2>(.*?)(?=<h2|\Z)", body, flags=re.S):
        chunk = sec.group(2)
        for q, a in re.findall(r"<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|\Z)", chunk, flags=re.S):
            if strip_tags(a): out.append((strip_tags(q), strip_tags(a)))
        for q, a in re.findall(r"<p><strong>([^<]*\?)</strong>(.*?)</p>", chunk, flags=re.S):
            out.append((strip_tags(q), strip_tags(a)))
    seen, res = set(), []
    for q, a in out:
        if q not in seen and len(a) > 1: seen.add(q); res.append((q, a))
    return res[:12]

def words(body): return len(strip_tags(body).split())

def fmt_date(d):
    y, m, dd = d.split("-"); M = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    return f"{int(dd)} {M[int(m)-1]} {y}"

WA_SVG = '<svg class="ic-wa" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .2-1.2c-.1-.1-.3-.2-.5-.3Z"/></svg>'

def jar(label, extra=""):
    return f'<div class="jar{extra}"><div class="lid"></div><div class="glass"><div class="lbl"><b>Mirc Glow</b><i></i><span>{esc(label)}</span></div></div><div class="refl"></div></div>'

def photo(p, cls="tile", eager=False, alt=None):
    """Product photo with a glossy CSS jar fallback if the upload is missing."""
    fb = jar(p["jars"][0]) if len(p["jars"]) == 1 else '<div class="jars">' + "".join(jar(j) for j in p["jars"]) + "</div>"
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    a = esc(alt or f'{BRAND} {p["name"]} {p["size"]}')
    cls = (cls + " full") if p.get("full") else cls
    return (f'<div class="ph {cls}" style="background:{p["bg"]}">'
            f'<picture>{webp_src(p["img"])}<img src="{p["img"]}" alt="{a}" width="800" height="800" {load} decoding="async" onerror="this.closest(\'.ph\').classList.add(\'noimg\');this.parentNode.remove()"></picture>{fb}</div>')

def webp_src(img):
    """Light WebP copy for browsers; the original file stays at its WordPress address."""
    if img.endswith(".png") and os.path.exists(os.path.join(ROOT, img.lstrip("/")[:-4] + ".mg.webp")):
        return f'<source srcset="{img[:-4]}.mg.webp" type="image/webp">'
    return ""

def order_msg(p, qty=1):
    q = f"{qty} x " if qty != 1 else ""
    return (f"Hi Mirc Glow, I'd like to order:\n• {q}{p['name']} ({p['size']}) – {inr(p['price'])} each\n\n"
            "Name:\nFull address with pincode:\nPayment: Cash on Delivery / pay online")

def wa_btn(p, label="Order on WhatsApp", cls="yb yb-wa2"):
    """WhatsApp order button. site.js swaps in the chosen quantity when a quantity box is on the page."""
    return (f'<a class="{cls}" href="{wa(order_msg(p))}" data-wa-order="{p["slug"]}" target="_blank" rel="noopener">'
            f'{WA_SVG}<span>{label}</span></a>')

def buy_btn(p, label="Buy Now", cls="yb yb-fill", go=True):
    """Website checkout button: adds the product (and the chosen quantity) to the cart; Buy Now goes straight to checkout."""
    label = label.replace(" on WhatsApp", "")
    go_attr = ' data-go="1"' if go else ""
    return f'<button type="button" class="{cls}" data-cart-add="{p["slug"]}"{go_attr}>{label}</button>'

CART_SVG = ('<svg class="ic-cart" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2.5 3h2.6l2.4 12.2a1.6 1.6 0 0 0 1.6 1.3h8.7a1.6 1.6 0 0 0 1.6-1.2L21.5 7H6"/></svg>')

PAY_CHIPS = ('<div class="chips-pay" aria-label="Payment options"><span>💵 Cash on Delivery</span><span>📱 UPI</span>'
             '<span>💳 Cards</span><span>🚚 Free shipping</span></div>')


# ---------------------------------------------------------------- benefit banners (photo + benefits)
BANNERS = {
 "avocado-korean-night-cream": dict(tone="avo", eb="Avocado · Vitamin B3 · Kojic acid", h="Wake up to softer, smoother-looking skin",
     c=[("💧","Overnight hydration"),("✨","More even-looking glow"),("🌙","Glass-skin night step")]),
 "avocado-glow-cream-15g": dict(tone="avo", eb="Avocado · Aloe vera", h="Simple, gentle daily moisture",
     c=[("🥑","Whipped avocado cream"),("🌿","Cooling aloe vera"),("☀️","Day or night")]),
 "glass-glow-cream": dict(tone="avo", eb="Glutathione · Niacinamide · Alpha arbutin", h="Your one-step glass skin glow",
     c=[("✨","Radiant, even-looking tone"),("💧","Hyaluronic acid hydration"),("🌿","Calming centella")]),
 "glass-glow-night-duo": dict(tone="gold", eb="Glass Glow · Avocado Night", h="Glow and comfort, two steps",
     c=[("✨","Radiant, even-looking tone"),("🥑","Rich overnight comfort"),("🌙","Alternate or layer")]),
 "glutathione-cream": dict(tone="gold", eb="Glutathione · Vitamin C · Kojic acid", h="For dull, tired-looking skin",
     c=[("✨","Radiant-looking finish"),("🎯","More even-looking tone"),("🌙","A pea-sized amount at night")]),
 "avocado-night-cream": dict(tone="cream", eb="Avocado · Aloe vera · Kojic acid", h="Rich comfort for dry, tight skin",
     c=[("🥑","Nourishing, cushioned feel"),("💧","Soft and comfortable by morning"),("🌿","With soothing aloe vera")]),
 "avocado-face-cream": dict(tone="peach", eb="Light daily cream · 10 g", h="The easiest way to try Mirc Glow",
     c=[("☀️","Light enough for daytime"),("👜","Handy travel-size jar"),("🥑","Avocado, aloe vera and B3")]),
 "day-and-night-cream-combo": dict(tone="avo", eb="Day + night routine", h="One simple routine, morning to night",
     c=[("☀️","Avocado Glow for the day"),("🌙","Avocado Night Cream for the night"),("₹","Costs less than buying both")]),
 "night-cream-combo": dict(tone="gold", eb="Treat + seal", h="Glow treatment and deep comfort, together",
     c=[("✨","Glutathione Cream to treat"),("🥑","Avocado Night Cream to seal"),("₹","Costs less than buying both")]),
 "korean-glass-skin-kit": dict(tone="lilac", eb="3 creams · full routine", h="Your complete Korean glass-skin kit",
     c=[("✨","Glutathione Cream"),("🥑","Avocado Korean Night Cream"),("☀️","Avocado Glow for mornings")]),
}

def banner(p, h="p"):
    b = BANNERS[p["slug"]]
    img = p["img"]; ws = webp_src(img)
    chips = "".join(f'<li><span aria-hidden="true">{i}</span>{esc(t)}</li>' for i, t in b["c"])
    return (f'<a class="bn bn-{b["tone"]}" href="/product/{p["slug"]}/">'
            f'<div class="bn-t"><span class="bn-e">{esc(b["eb"])}</span><{h} class="bn-h">{esc(b["h"])}</{h}><ul class="bn-c">{chips}</ul>'
            f'<span class="bn-p"><b>{inr(p["price"])}</b> <s>{inr(p["mrp"])}</s><em>Shop now →</em></span></div>'
            f'<div class="bn-ph"><picture>{ws}<img src="{img}" alt="{esc(BRAND + " " + p["name"])}" width="600" height="600" loading="lazy" decoding="async"></picture></div></a>')

def banner_strip(items, title="Why you'll love them", eyebrow="Benefits at a glance"):
    return (f'<section class="sec" aria-label="{esc(title)}"><div class="w"><span class="eyebrow">{esc(eyebrow)}</span><h2 class="sh">{esc(title)}</h2>'
            f'<div class="bns" data-slider>{"".join(banner(p) for p in items)}</div>'
            f'<div class="slider-nav"><button type="button" data-prev aria-label="Previous">‹</button><span data-count>1 / {len(items)}</span><button type="button" data-next aria-label="Next">›</button></div></div></section>')

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

# ---------------------------------------------------------------- schema
ORG_ID = SITE + "/#organization"
RETURN_POLICY = {"@type":"MerchantReturnPolicy","applicableCountry":"IN","returnPolicyCategory":"https://schema.org/MerchantReturnFiniteReturnWindow","merchantReturnDays":7,"returnMethod":"https://schema.org/ReturnByMail","returnFees":"https://schema.org/FreeReturn","merchantReturnLink":SITE+"/returns-refunds/"}
SHIPPING = {"@type":"OfferShippingDetails","shippingRate":{"@type":"MonetaryAmount","value":0,"currency":"INR"},"shippingDestination":{"@type":"DefinedRegion","addressCountry":"IN"},
            "deliveryTime":{"@type":"ShippingDeliveryTime","handlingTime":{"@type":"QuantitativeValue","minValue":0,"maxValue":2,"unitCode":"DAY"},"transitTime":{"@type":"QuantitativeValue","minValue":3,"maxValue":7,"unitCode":"DAY"}}}
ORG = {"@type":"OnlineStore","@id":ORG_ID,"name":BRAND,"url":SITE+"/","logo":SITE+"/assets/logo.png",
       "description":"Korean-inspired skincare brand from Bhatkal, Karnataka, India, making avocado night creams, glutathione cream and the Glass Glow Cream, and supplying night cream and avocado cream in kg for salons and resellers.",
       "telephone":PHONE.replace(" ",""),"address":{"@type":"PostalAddress","streetAddress":"Azad Nagar 4th Cross","addressLocality":"Bhatkal","addressRegion":"Karnataka","postalCode":"581320","addressCountry":"IN"},
       "areaServed":{"@type":"Country","name":"India"},"currenciesAccepted":"INR","paymentAccepted":"Cash on Delivery, UPI, card",
       "contactPoint":{"@type":"ContactPoint","telephone":PHONE.replace(" ",""),"contactType":"customer service","areaServed":"IN","availableLanguage":["English","Hindi"]},
       "hasMerchantReturnPolicy":RETURN_POLICY,"foundingLocation":{"@type":"Place","name":"Bhatkal, Karnataka, India"},
       "founder":{"@type":"Person","name":"Mohammed Nihal","url":SITE+"/about-the-author/"},
       "knowsAbout":["Night cream","Avocado cream","Avocado night cream","Glutathione cream","Kojic acid","Niacinamide","Alpha arbutin","Hyaluronic acid","Centella asiatica","Korean skincare","Glass skin routine","Bulk night cream supply"],
       "brand":{"@type":"Brand","name":BRAND}}
WEBSITE = {"@type":"WebSite","@id":SITE+"/#website","url":SITE+"/","name":BRAND,"inLanguage":"en-IN","publisher":{"@id":ORG_ID}}

def crumbs_ld(items):
    return {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":SITE+u} for i,(n,u) in enumerate(items)]}

def faq_ld(faqs):
    return {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}

def product_ld(p, url):
    d = {"@type":"Product","@id":SITE+url+"#product","name":strip_tags(p["h1"]),"description":p["rd"].replace("Buy ","",1),
         "image":[SITE+p["img"]],"sku":f"MG-{p['id']}","brand":{"@type":"Brand","name":BRAND},"category":"Skin care > Face moisturiser",
         "additionalProperty":[{"@type":"PropertyValue","name":"Size","value":p["size"]},{"@type":"PropertyValue","name":"Key ingredients","value":", ".join(p["ing"])}],
         "offers":{"@type":"Offer","url":SITE+url,"priceCurrency":"INR","price":str(p["price"]),"priceValidUntil":"2027-03-31",
                   "availability":"https://schema.org/InStock","itemCondition":"https://schema.org/NewCondition","seller":{"@id":ORG_ID},
                   "shippingDetails":SHIPPING,"hasMerchantReturnPolicy":RETURN_POLICY}}
    if "parts" in p: d["isRelatedTo"] = [{"@type":"Product","name":PBY[s]["name"],"url":SITE+f"/product/{s}/"} for s in p["parts"]]
    # extra real photos shown on the page
    try:
        extra = re.findall(r'<img[^>]*src="(/wp-content/[^"]+)"', read(os.path.join(SRC, "products", p["slug"] + ".html")))
    except Exception: extra = []
    d["image"] = [SITE + p["img"]] + [SITE + x for x in extra if x != p["img"]][:4]
    d["mpn"] = f"MG-{p['id']}"
    d["weight"] = {"@type":"QuantitativeValue","value":p["grams"],"unitCode":"GRM"}
    d["countryOfOrigin"] = {"@type":"Country","name":"India"}
    d["manufacturer"] = {"@id":ORG_ID}
    d["audience"] = {"@type":"PeopleAudience","suggestedMinAge":18}
    d["offers"]["priceSpecification"] = [{"@type":"UnitPriceSpecification","price":p["price"],"priceCurrency":"INR"},
        {"@type":"UnitPriceSpecification","priceType":"https://schema.org/StrikethroughPrice","price":p["mrp"],"priceCurrency":"INR"}]
    return d

def ld(*nodes):
    return '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@graph":list(nodes)}, ensure_ascii=False, separators=(",",":")).replace("</","<\\/") + "</script>"

# ---------------------------------------------------------------- layout
CSS_HREF = None
JS_HREF = None
LANG_TAG = {"en":"en-IN","hi":"hi-IN","ta":"ta-IN","te":"te-IN","mr":"mr-IN","bn":"bn-IN"}
LANG_NAME = {"ta":"தமிழ்","te":"తెలుగు","mr":"मराठी","bn":"বাংলা"}

def head(title, desc, url, *, lang="en", og_type="website", image=None, canonical=None, alts=None, extra="", robots="index, follow, max-image-preview:large, max-snippet:-1"):
    canonical = canonical or SITE + url
    image = SITE + (image or PBY["avocado-korean-night-cream"]["img"])
    hl = ""
    if alts:
        for code, u in alts: hl += f'<link rel="alternate" hreflang="{code}" href="{SITE+u}">'
    return f'''<!doctype html>
<html lang="{LANG_TAG.get(lang, 'en-IN')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="{robots}">
{hl}
<meta property="og:locale" content="{LANG_TAG.get(lang, 'en-IN').replace('-', '_')}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" href="/favicon-96x96.png" type="image/png" sizes="96x96"><link rel="icon" href="/favicon-192x192.png" type="image/png" sizes="192x192"><link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="{CSS_HREF}">
<link rel="alternate" type="application/rss+xml" title="{BRAND} Journal" href="{SITE}/feed/">
<script>addEventListener("error",function(e){{var t=e.target;if(t&&t.tagName==="IMG"&&!t.onerror)t.classList.add("broken")}},true)</script>
{extra}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''

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
<a class="hwa" href="{WA_HELLO}" target="_blank" rel="noopener" aria-label="Order on WhatsApp">{WA_SVG}<span>Order on WhatsApp</span></a><a class="hcart" href="/checkout/" aria-label="Cart">{CART_SVG}<span class="hcart-n" data-cart-count hidden>0</span></a>
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
<div><h2>Shop</h2><ul><li><a href="/shop/">All creams</a></li><li><a href="/product-category/night-creams/">Night creams</a></li><li><a href="/product-category/night-creams/avocado-night-creams/">Avocado creams</a></li><li><a href="/product-category/combos/">Combos and kits</a></li><li><a href="/skincare-gift-sets/">Gift sets</a></li><li><a href="/bulk-night-cream/">Bulk orders (kg)</a></li><li><a href="/avocado-cream-in-kg/">Avocado cream in kg</a></li></ul></div>
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

# ---------------------------------------------------------------- page builders
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

def fk_top():
    """Marketplace-style top of the home page (search, category circles, offer slider, coupons, deals, grids)."""
    P_ = PBY
    # search: product + guide names; site.js sends the shopper straight to the matching page
    opts = [(p["name"] + " " + p["size"], f"/product/{p['slug']}/") for p in PRODUCTS] + \
           [("Avocado cream in kg (bulk)", "/avocado-cream-in-kg/"), ("Night cream in kg (bulk)", "/bulk-night-cream/"), ("Gift sets", "/skincare-gift-sets/"), ("Skin quiz", "/skin-quiz/")] + \
           [(p["title"], f"/{p['slug']}/") for p in LIVE_POSTS[:40]]
    dl = "".join(f'<option value="{esc(n)}" data-u="{u}"></option>' for n, u in opts)
    search = (f'<form class="fk-search" action="/shop/" role="search" data-fk-search><label class="sr" for="fk-q">Search Mirc Glow</label>'
              f'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M10 3a7 7 0 0 1 5.6 11.2l4.6 4.6-1.4 1.4-4.6-4.6A7 7 0 1 1 10 3Zm0 2a5 5 0 1 0 0 10 5 5 0 0 0 0-10Z"/></svg>'
              f'<input id="fk-q" name="q" list="fk-list" placeholder="Search avocado cream, glutathione, kg…" autocomplete="off"><datalist id="fk-list">{dl}</datalist></form>')
    circ = [("Night creams", cat_url("night-creams"), P_["avocado-night-cream"]), ("Avocado", cat_url("avocado-night-creams"), P_["avocado-korean-night-cream"]),
            ("Glass Glow", "/product/glass-glow-cream/", P_["glass-glow-cream"]), ("Glutathione", "/product/glutathione-cream/", P_["glutathione-cream"]),
            ("Combos", cat_url("combos"), P_["night-cream-combo"]), ("Gift sets", "/skincare-gift-sets/", P_["korean-glass-skin-kit"]),
            ("Bulk (kg)", "/avocado-cream-in-kg/", None), ("Guides", "/blog/", None)]
    def circle(t, u, p):
        if p: ph = photo(p, "fk-cph")
        elif "kg" in u: ph = '<div class="ph fk-cph full"><picture><source srcset="/wp-content/uploads/2026/10/mirc-glow-avocado-cream-1kg-tubs.mg.webp" type="image/webp"><img src="/wp-content/uploads/2026/10/mirc-glow-avocado-cream-1kg-tubs.jpg" alt="" width="800" height="800" loading="lazy"></picture></div>'
        else: ph = '<div class="ph fk-cph fk-cico" aria-hidden="true">📖</div>'
        return f'<a class="fk-c" href="{u}">{ph}<span>{esc(t)}</span></a>'
    circles = '<nav class="fk-cats" aria-label="Shop by category">' + "".join(circle(*c) for c in circ) + "</nav>"
    gg, duo, a15, kit = P_["glass-glow-cream"], P_["glass-glow-night-duo"], P_["avocado-glow-cream-15g"], P_["korean-glass-skin-kit"]
    pct = lambda p: round((p["mrp"] - p["price"]) * 100 / p["mrp"])
    slides = [
     ("fk-s1", "New launch", "Glass Glow Cream", f"Glutathione + alpha arbutin + niacinamide · {inr(gg['price'])} <s>{inr(gg['mrp'])}</s>", "Shop now", "/product/glass-glow-cream/", gg, True),
     ("fk-s2", "Combo offer", "Save up to " + inr(max(p["mrp"] - p["price"] for p in SETS)), "Day & night, glow duos and the full glass skin kit", "See combos", cat_url("combos"), duo, False),
     ("fk-s3", "Under ₹400", "Avocado Glow Cream 15g", f"Avocado + aloe vera · {inr(a15['price'])} <s>{inr(a15['mrp'])}</s> · {pct(a15)}% off", "Buy now", "/product/avocado-glow-cream-15g/", a15, False),
     ("fk-s4", "For salons", "Avocado cream in kg", "From 1 kg · sample before bulk · all-India delivery", "Get price per kg", "/avocado-cream-in-kg/", None, False),
    ]
    def slide(cls, eb, h, sub, cta, u, p, first):
        if p:
            img = (f'<picture>{webp_src(p["img"])}<img src="{p["img"]}" alt="{esc(BRAND + " " + p["name"])}" width="800" height="800" '
                   f'{"fetchpriority=\"high\"" if first else "loading=\"lazy\""} decoding="async"></picture>')
        else:
            img = '<picture><source srcset="/wp-content/uploads/2026/10/mirc-glow-avocado-cream-1kg-tubs.mg.webp" type="image/webp"><img src="/wp-content/uploads/2026/10/mirc-glow-avocado-cream-1kg-tubs.jpg" alt="Mirc Glow avocado cream 1 kg bulk tub" width="800" height="800" loading="lazy"></picture>'
        return (f'<a class="fk-slide {cls}" href="{u}"><div class="fk-st"><span class="fk-eb">{eb}</span><b>{esc(h)}</b><span class="fk-sub">{sub}</span>'
                f'<span class="fk-cta">{cta} ›</span></div><div class="fk-si">{img}</div></a>')
    slider = (f'<section class="fk-hero" aria-label="Offers"><div class="fk-slides" data-fk-slider>{"".join(slide(*x) for x in slides)}</div>'
              f'<div class="fk-dots" aria-hidden="true">{"".join("<i></i>" for _ in slides)}</div></section>')
    coupons = ('<section class="fk-offers" aria-label="Offers for you"><h2 class="fk-h">Offers for you</h2><div class="fk-row">'
               '<div class="fk-cp"><b>GLOW10</b><span>Extra 10% off your first order. Mention the code on WhatsApp.</span></div>'
               '<div class="fk-cp"><b>FREE delivery</b><span>On every order, anywhere in India. Usually 3–7 days.</span></div>'
               '<div class="fk-cp"><b>Cash on Delivery</b><span>Pay when it arrives, or ask for a UPI / card link.</span></div>'
               '<div class="fk-cp"><b>7-day returns</b><span>On sealed jars. Damaged or wrong items replaced.</span></div></div></section>')
    def deal(p):
        return (f'<a class="fk-d" href="/product/{p["slug"]}/">{photo(p, "fk-dph")}<span class="fk-dn">{esc(p["name"])}</span>'
                f'<span class="fk-dp"><em>{pct(p)}% off</em> <s>{inr(p["mrp"])}</s> <b>{inr(p["price"])}</b></span><span class="fk-free">Free delivery</span></a>')
    deals = sorted(PRODUCTS, key=pct, reverse=True)
    deals_html = (f'<section class="fk-deals" aria-labelledby="fk-deals-h"><div class="fk-dh"><h2 id="fk-deals-h" class="fk-h">Top deals</h2>'
                  f'<span class="fk-pill">Up to {pct(deals[0])}% off</span><a href="/shop/">View all ›</a></div><div class="fk-row">{"".join(deal(p) for p in deals)}</div></section>')
    def gcard(p):
        return (f'<article class="fk-g"><a href="/product/{p["slug"]}/" class="fk-ga">{photo(p, "fk-gph")}'
                f'{"<span class=\"fk-new\">NEW</span>" if p["tag"] in ("New","Premium") else ""}</a>'
                f'<div class="fk-gb"><h3><a href="/product/{p["slug"]}/">{esc(p["name"])}</a></h3><p class="fk-gm">{esc(p["meta"])} · {p["size"]}</p>'
                f'<p class="fk-dp"><em>{pct(p)}% off</em> <s>{inr(p["mrp"])}</s> <b>{inr(p["price"])}</b></p><p class="fk-free">Free delivery · COD</p>'
                f'{buy_btn(p, "Buy now", "yb yb-fill yb-sm")}</div></article>')
    grid = (f'<section class="fk-grid" aria-labelledby="h-prod"><div class="fk-dh"><h2 id="h-prod" class="fk-h">All creams</h2><a href="/shop/">View all ›</a></div>'
            f'<div class="fk-gr">{"".join(gcard(p) for p in SINGLES)}</div></section>')
    def price_tile(t, sub, u, p):
        return f'<a class="fk-pt" href="{u}">{photo(p, "fk-ptph")}<b>{t}</b><span>{sub}</span></a>'
    budget = ('<section class="fk-budget" aria-labelledby="fk-b-h"><h2 id="fk-b-h" class="fk-h">Shop by budget</h2><div class="fk-pts">'
              + price_tile("Under ₹500", "Avocado Glow creams", "/product/avocado-glow-cream-15g/", a15)
              + price_tile("Under ₹1,000", "Night creams & combo", "/product/avocado-night-cream/", P_["avocado-night-cream"])
              + price_tile("Under ₹2,000", "Glutathione & kits", "/product/glutathione-cream/", P_["glutathione-cream"])
              + price_tile("Premium", "Glass Glow range", "/product/glass-glow-cream/", gg) + "</div></section>")
    sets_row = ('<section class="fk-deals" aria-labelledby="h-sets2"><div class="fk-dh"><h2 id="h-sets2" class="fk-h">Combos &amp; kits</h2>'
                f'<a href="{cat_url("combos")}">View all ›</a></div><div class="fk-row">{"".join(deal(p) for p in SETS)}</div></section>')
    intro = ('<section class="fk-intro"><h1 id="h-home">Mirc Glow avocado night creams &amp; Korean-inspired skincare</h1>'
             '<p>Avocado, glutathione and glass-skin creams made in Karnataka, for smoother, brighter-looking skin. Order in one WhatsApp message: free shipping across India, Cash on Delivery and 7-day returns.</p>' + qbox("Mirc Glow is a Korean-inspired skincare brand from Bhatkal, Karnataka, India. It sells avocado night creams (from ₹349), a glutathione cream (₹1,499) and the Glass Glow Cream (₹2,499) online across India, with free shipping, Cash on Delivery, 7-day returns on sealed jars and orders on WhatsApp +91 99808 81230. Salons can buy night cream in kg.", label="In short") + '</section>')
    BR="/wp-content/uploads/2026/10/brands/"
    def otile(href, img, name, sub, webp=True):
        pic = (f'<picture><source srcset="{BR}{img}.webp" type="image/webp"><img src="{BR}{img}.jpg" alt="{esc(name)}" width="300" height="300" loading="lazy" decoding="async"></picture>' if webp
               else f'<img src="{BR}{img}.jpg" alt="{esc(name)}" width="300" height="300" loading="lazy" decoding="async">')
        return f'<a class="ob-t" href="{href}" target="_blank" rel="noopener">{pic}<b>{esc(name)}</b><span>{esc(sub)}</span></a>'
    GX="https://glutanex.co.in/product/"
    gx = [("glutanex-glutathione-night-cream","glutanex-glutathione-night-cream-30g","Glutathione Night Cream","30 g"),
          ("glutanex-gluta-boost-face-wash","glutanex-gluta-boost-glutathione-face-wash-100ml","Gluta Boost Face Wash","100 ml"),
          ("glutanex-aqua-fresh-shower-gel","glutanex-aqua-fresh-glutathione-shower-gel-100ml","Aqua Fresh Shower Gel","100 ml"),
          ("glutanex-glow-duo-night-cream-face-wash","glutanex-glow-duo-glutathione-cream-face-wash","Glow Duo","Night cream + face wash"),
          ("glutanex-glow-trio-night-cream-face-wash-shower-gel","glutanex-glow-trio-night-cream-face-wash-shower-gel","Glow Trio","Night cream + face wash + shower gel"),
          ("glutanex-face-wash-shower-gel-combo","glutanex-face-wash-and-shower-gel-combo","Face Wash + Shower Gel","Combo"),
          ("glutanex-night-cream-shower-gel-combo","glutanex-night-cream-and-shower-gel-combo","Night Cream + Shower Gel","Combo")]
    FP="https://www.fairnpink.in/product/"
    fp = [("fair-n-pink-advance-radiance-cream","product-1080","Advance Radiance Cream","10 g · ₹999"),
          ("fair-n-pink-advance-radiance-cream-pack-of-2","merchant-pack-2","Pack of 2","2 x 10 g · ₹1,899"),
          ("fair-n-pink-advance-radiance-cream-pack-of-3","merchant-pack-3","Pack of 3","3 x 10 g · ₹2,699")]
    brands = ('<section class="ob" aria-labelledby="h-ob"><p class="ob-eye">The Mirc family</p><h2 id="h-ob" class="fk-h">Our other brands</h2>'
        '<p class="ob-lead">Two more skincare brands from the same team in Karnataka, made with the same care.</p><div class="ob-grid">'
        '<article class="ob-b ob-dark"><p class="ob-k">Glutathione skincare</p><h3>GlutaNex</h3>'
        '<p class="ob-d">Glutathione night cream, face wash and shower gel for brighter-looking skin, face and body. Launching soon.</p>'
        '<div class="ob-row">' + "".join(otile(GX+sl+"/", im, n, sub + " · Launching soon") for sl,im,n,sub in gx) + '</div>'
        '<a class="ob-cta" href="https://glutanex.co.in/" target="_blank" rel="noopener">Visit GlutaNex</a></article>'
        '<article class="ob-b ob-light"><p class="ob-k">Radiance care</p><h3>Fair N Pink</h3>'
        '<p class="ob-d">Advance Radiance Cream in a 10 g jar, with value packs of 2 and 3. Free shipping across India.</p>'
        '<div class="ob-row">' + "".join(otile(FP+sl+"/", im, n, sub, webp=False) for sl,im,n,sub in fp) + '</div>'
        '<a class="ob-cta" href="https://www.fairnpink.in/" target="_blank" rel="noopener">Visit Fair N Pink</a></article></div></section>')
    return f'<div class="fk">{search}{circles}{slider}{intro}{coupons}{deals_html}{grid}{budget}{sets_row}{brands}</div>'

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
     ("Which cream should I choose?", "Dry skin: the Avocado Night Cream. Most skin types: the Avocado Korean Night Cream. Dull skin: the Glutathione Cream. A complete glass-skin step: the Glass Glow Cream. Want the simplest formula: Avocado Glow Cream 15g. Not sure? The skin quiz takes under a minute."),
     ("Will it change my skin colour?", "No. Our creams are cosmetics for softer, smoother, brighter-looking skin. They do not change your natural skin tone, and we will never claim they do."),
     ("Can I return a cream?", "Yes. Unopened, sealed jars can be returned within 7 days of delivery. Damaged, wrong or expired items are replaced or refunded."),
    ]
    faq_html = "".join(f'<details{" open" if i==0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for i,(q,a) in enumerate(faqs))
    faq_html = faq_html.replace("The skin quiz", '<a href="/skin-quiz/">The skin quiz</a>')
    itemlist = {"@type":"ItemList","name":"Mirc Glow creams","itemListElement":[{"@type":"ListItem","position":i+1,"url":SITE+f"/product/{p['slug']}/","name":p["name"]} for i,p in enumerate(PRODUCTS)]}
    body = head("Mirc Glow | Avocado Night Creams & Korean-Inspired Skincare",
        "Shop Mirc Glow avocado night creams, glutathione and Glass Glow creams in India. Avocado, kojic acid and niacinamide care. Free shipping and Cash on Delivery.",
        url, extra=f'<link rel="preload" as="image" href="/wp-content/uploads/2026/10/mirc-glow-glass-glow-cream-glutathione-30g.mg.webp" type="image/webp" fetchpriority="high"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&display=swap">' + ld(ORG, WEBSITE, itemlist, faq_ld(faqs)))
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
{fk_top()}
{RECENT_HTML}

<section class="sec" aria-labelledby="h-con"><div class="w">
<span class="eyebrow">Personalized picks</span><h2 id="h-con" class="sh">Shop by Concern</h2>
<div class="cons">{con}</div>
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

{at_glance_html()}

<section class="sec"><div class="w"><div class="closer">
<h2 class="sh">Your glow starts here</h2>
<p>Korean-inspired essentials for hydration, radiance and a smooth, glass-skin-inspired finish. Order in one WhatsApp message.</p>
<div class="row" style="justify-content:center"><a class="yb yb-wa" href="{WA_HELLO}" target="_blank" rel="noopener">{WA_SVG}<span>Order on WhatsApp</span></a><a class="yb yb-line" href="/about/">About Mirc Glow</a></div>
</div></div></section>
</main>
'''
    body += footer()
    write(url, body)

def compare_table(items):
    rows = "".join(f'<tr><td><a href="/product/{p["slug"]}/">{esc(p["name"])}</a></td><td>{p["size"]}</td><td>{inr(p["price"])} <s style="color:var(--muted)">{inr(p["mrp"])}</s></td>'
                   f'<td>about {inr(round(p["price"]/p["grams"]))}</td><td>{esc(p["when"])}</td><td>{esc(p["best"])}</td></tr>' for p in items)
    return f'<div class="tbl"><table><caption class="sr">Mirc Glow creams compared</caption><thead><tr><th scope="col">Cream</th><th scope="col">Size</th><th scope="col">Price</th><th scope="col">Per gram</th><th scope="col">When</th><th scope="col">Best for</th></tr></thead><tbody>{rows}</tbody></table></div>'

def list_quick(h1, items):
    lo, hi = min(items, key=lambda p: p["price"]), max(items, key=lambda p: p["price"])
    val = min(items, key=lambda p: p["price"] / p["grams"])
    t = (f"{BRAND} has {len(items)} {'products' if h1.lower().startswith('shop') else h1.lower()} from {inr(lo['price'])} ({lo['name']}, {lo['size']}) to {inr(hi['price'])} ({hi['name']}). "
         f"Best value per gram: {val['name']} ({val['size']}, {inr(val['price'])}). Every order ships free across India with Cash on Delivery.")
    return qbox(t, label="In short")

def listing(url, title, desc, h1, ko, intro, items, crumbs, active_chip, extra_html=""):
    chips = [("All","/shop/"),("Night creams","/product-category/night-creams/"),("Avocado","/product-category/night-creams/avocado-night-creams/"),("Combos and kits","/product-category/combos/")]
    chip_html = "".join(f'<a href="{u}"{" aria-current=\"page\"" if u==active_chip else ""}>{n}</a>' for n,u in chips)
    il = {"@type":"ItemList","name":h1,"numberOfItems":len(items),"itemListElement":[{"@type":"ListItem","position":i+1,"url":SITE+f"/product/{p['slug']}/","name":p["name"]} for i,p in enumerate(items)]}
    cp = {"@type":"CollectionPage","@id":SITE+url,"url":SITE+url,"name":h1,"description":desc,"isPartOf":{"@id":SITE+"/#website"}}
    fq = faqs_from(extra_html) if extra_html else []
    body = head(title, desc, url, extra=ld(ORG, cp, il, crumbs_ld(crumbs), *([faq_ld(fq)] if fq else [])))
    body += header("/shop/")
    body += f'<main id="main">{crumbs_html(crumbs)}<div class="w ptop"><span class="lab">{ko}</span><h1 class="dsp">{esc(h1)}</h1><p>{esc(intro)}</p>{list_quick(h1, items)}<nav class="chips" aria-label="Categories">{chip_html}</nav></div>'
    body += f'<section class="w" style="padding-bottom:clamp(48px,6vw,90px)"><div class="grid4">{"".join(card_html(p, "h2") for p in items)}</div></section>'
    body += banner_strip(items, "Benefits at a glance", "Why you'll love them")
    singles = [p for p in items]
    body += f'<section class="w" style="padding-bottom:clamp(56px,8vw,110px)" aria-labelledby="h-cmp"><div class="head"><span class="lab">Compare</span><h2 class="dsp" id="h-cmp" style="font-size:clamp(2rem,4vw,3rem)">Side by <em>side</em></h2><p>Price per gram, best time of day and who each one suits.</p></div>{compare_table(singles)}</section>'
    body += extra_html
    body += f'''<section class="band tight" style="background:var(--milk)"><div class="w"><div class="promise">
<div><span class="ic">✦</span><b>Free shipping</b><span>On every order in India</span></div>
<div><span class="ic">₹</span><b>Cash on Delivery</b><span>Or a secure online payment link</span></div>
<div><span class="ic">7</span><b>Easy returns</b><span>Sealed jars within 7 days</span></div>
<div><span class="ic">✉</span><b>How to order</b><span>Tap Order, send the WhatsApp message, we confirm</span></div>
</div></div></section></main>'''
    body += footer()
    write(url, body)

def NIGHT_GUIDE():
    """Buying guide that makes the Night Creams shop page the main 'night cream' page."""
    live = {p["slug"] for p in LIVE_POSTS} | {g["slug"] for g in PAGES}
    groups = [("By skin type", ["night-cream-for-dehydrated-skin","night-cream-for-skin-barrier","night-cream-for-rough-skin-texture","lightweight-night-cream-for-humid-weather","night-cream-for-oily-skin","night-cream-for-dry-skin-in-winter","night-cream-for-combination-skin","night-cream-for-sensitive-skin","night-cream-for-normal-skin"]),
              ("By age and person", ["night-cream-for-teenagers","night-cream-in-your-20s","avocado-night-cream-for-30s","night-cream-for-mature-skin","night-cream-for-fine-lines","night-cream-for-men"]),
              ("By concern", ["night-cream-for-uneven-skin-tone","night-cream-for-dull-skin","night-cream-for-acne-marks-and-dark-spots","night-cream-for-tanned-skin","avocado-night-cream-for-pigmentation-prone-skin","best-night-cream-for-glowing-skin"]),
              ("Choosing and buying", ["best-night-cream-for-indian-skin","night-cream-price-in-india","affordable-vs-premium-night-cream","ingredients-to-look-for-in-a-night-cream","night-cream-with-vitamin-c","retinol-night-cream-for-beginners"]),
              ("How to use", ["how-to-moisturise-skin-overnight","how-to-apply-night-cream","how-much-night-cream-to-use","night-cream-vs-day-cream","night-cream-vs-moisturizer","can-i-use-night-cream-in-the-day","is-night-cream-necessary","night-cream-benefits","night-cream-side-effects"]),
              ("हिंदी में", ["dark-spots-ke-liye-night-cream","glowing-skin-ke-liye-night-routine","night-cream-ke-fayde-aur-nuksan","night-cream-kaise-lagaye","night-cream-kab-lagana-chahiye","night-cream-din-mein-laga-sakte-hain","oily-skin-ke-liye-night-cream"])]
    title = {**{p["slug"]: p["title"] for p in LIVE_POSTS}, **{g["slug"]: g["title"] for g in PAGES}}
    cols = "".join(f'<div><h3>{esc(h)}</h3><ul>' + "".join(f'<li><a href="/{x}/">{esc(title[x])}</a></li>' for x in xs if x in live) + "</ul></div>" for h, xs in groups)
    return NG_HTML.replace("{cols}", cols)

NG_HTML = """<section class="w ng" style="padding-bottom:clamp(48px,7vw,90px)">
<div class="prose">
<h2>How to choose a night cream</h2>
<p>A night cream is a moisturiser made for the hours you sleep: usually richer than a day cream, with no sunscreen, and often with ingredients for a smoother, more even-looking tone. Choose by your skin type first, then by what you want it to do.</p>
<table><thead><tr><th>Your skin</th><th>Look for</th><th>Mirc Glow pick</th></tr></thead><tbody>
<tr><td>Dry or tight</td><td>A rich, cushioned cream</td><td><a href="/product/avocado-night-cream/">Avocado Night Cream</a>, 30 g, ₹649</td></tr>
<tr><td>Normal or combination</td><td>A medium texture, used in a pea-sized amount</td><td><a href="/product/avocado-korean-night-cream/">Avocado Korean Night Cream</a>, 25 g, ₹649</td></tr>
<tr><td>Oily or acne-prone</td><td>A thin layer of a lighter cream</td><td><a href="/product/glass-glow-cream/">Glass Glow Cream</a>, or a thin layer of the Korean Night Cream</td></tr>
<tr><td>Dull or uneven-looking</td><td>Glutathione, niacinamide, kojic acid or alpha arbutin, with sunscreen every morning</td><td><a href="/product/glutathione-cream/">Glutathione Cream</a> or <a href="/product/glass-glow-cream/">Glass Glow Cream</a></td></tr>
<tr><td>Sensitive, or new to skincare</td><td>A short, simple formula; patch test first</td><td><a href="/product/avocado-glow-cream-15g/">Avocado Glow Cream 15g</a> (avocado and aloe vera only)</td></tr>
</tbody></table>
<h2>Night cream by age</h2>
<p><strong>Teens:</strong> a gentle moisturiser is usually enough; skip strong actives unless a doctor advises (<a href="/night-cream-for-teenagers/">night cream for teenagers</a>). <strong>20s:</strong> a light night cream and daily sunscreen (<a href="/night-cream-in-your-20s/">night cream in your 20s</a>). <strong>30s and older:</strong> a richer cream every night, with ingredients such as niacinamide for a smoother, more even look.</p>
<h2>How to use a night cream</h2>
<ol><li>Wash your face and pat dry.</li><li>Apply serum first if you use one.</li><li>Take a pea-sized amount and spread it gently upwards over face and neck.</li><li>Use it as the last step, 20 to 30 minutes before sleep.</li><li>Wear sunscreen every morning, especially with kojic acid, glutathione or alpha arbutin.</li></ol>
<h2>Night cream questions</h2>
<h3>Which night cream is best for my face?</h3><p>The one that suits your skin type: rich creams for dry skin, lighter textures for oily skin, and glow-focused ingredients for dull or uneven-looking skin. Use the table above, or take the <a href="/skin-quiz/">skin quiz</a>.</p>
<h3>Is night cream necessary?</h3><p>Not for everyone. It helps most if your skin feels dry or tight in the morning, or if you want ingredients that work while you sleep. Read <a href="/is-night-cream-necessary/">is night cream necessary</a>.</p>
<h3>Can I use night cream every day?</h3><p>Yes. Most night creams are made for nightly use. Patch test first and use a pea-sized amount.</p>
<h3>Does night cream change skin colour?</h3><p>No. A night cream can help skin look smoother, fresher and more even, but it does not change your natural skin tone.</p>
<h3>What is the price of Mirc Glow night cream?</h3><p>From ₹349 for the 10 g Avocado Glow cream to ₹2,499 for the 30 g Glass Glow Cream, with free shipping and Cash on Delivery across India. Salons can also buy <a href="/bulk-night-cream/">night cream in kg</a>.</p>
</div>
<div class="ng-guides"><h2 class="az-h">Night cream guides</h2><div class="ng-cols">{cols}</div></div>
</section>"""

def build_shop():
    help_html = f'''<section class="w" style="padding-bottom:clamp(56px,8vw,110px)"><div class="brief"><div><span class="lab">How ordering works</span><h2 class="dsp" style="margin-top:14px">Order in <em>one message</em>.</h2></div>
<div class="say"><p>Tap <b>Order</b> on any cream. WhatsApp opens with your order already written. Add your name, address and pincode, choose Cash on Delivery or online payment, and send. We confirm the order and share the tracking number when it ships.</p>
<p>Not sure which cream to choose? Take the <a class="link" href="/skin-quiz/">skin quiz</a> or <a class="link" href="{WA_ASK}" target="_blank" rel="noopener">ask us on WhatsApp</a>.</p></div></div></section>'''
    listing("/shop/","Shop Avocado Night Cream and Glutathione Cream | Mirc Glow",
            "Shop all Mirc Glow creams and combos from ₹349: avocado night creams, glutathione cream and glass skin kits. Free shipping and Cash on Delivery across India.",
            "Shop all creams", '<span lang="ko">컬렉션</span> · THE COLLECTION',
            "Six Korean-inspired creams and four sets. Free shipping across India, Cash on Delivery, and 7-day returns on sealed jars.",
            PRODUCTS, [("Home","/"),("Shop","/shop/")], "/shop/", help_html)
    for c, d in CATS.items():
        items = [p for p in PRODUCTS if c in p["cats"]]
        cr = [("Home","/"),("Shop","/shop/")]
        if d["parent"]: cr.append((CATS[d["parent"]]["name"], cat_url(d["parent"])))
        cr.append((d["name"], cat_url(c)))
        listing(cat_url(c), d["rt"], d["rd"], d["h1"], d["ko"], d["intro"], items, cr, cat_url(c), NIGHT_GUIDE() if c == "night-creams" else "")

def related_posts(p, n=3):
    pool = [q for q in LIVE_POSTS if q["topic"] == p["topic"]]
    if p in pool:
        i = pool.index(p); pool = pool[i+1:] + pool[:i]
    same = [q for q in pool if q["slug"] != p["slug"]]
    other = [q for q in LIVE_POSTS if q["topic"] != p["topic"] and q["slug"] != p["slug"]]
    return (same + other)[:n]

def guide_note():
    return f'''<aside class="note"><b>About this guide</b><p>Written by <a href="/about-the-author/">Mohammed Nihal</a>, founder of Mirc Glow, in Bhatkal, Karnataka, and reviewed on {fmt_date(TODAY)}. This is general skincare information, not medical advice. If you have a skin condition, are pregnant, or get a reaction that does not settle, please see a dermatologist.</p><p>Questions about our creams? WhatsApp <a href="{WA_ASK}" target="_blank" rel="noopener">{PHONE}</a>. Free shipping · Cash on Delivery · <a href="/returns-refunds/">7-day returns</a> on sealed jars.</p></aside>'''

BUYBOX_SKIP = {"avocado-cream", "avocado-cream-in-kg", "avocado-cream-in-kg-hindi", "buy-avocado-night-cream-online"}
def wants_buybox(slug, topic=None):
    return slug not in BUYBOX_SKIP and (topic == "avocado" or "avocado" in slug)

def avocado_buybox(lang="en"):
    picks = [("avocado-glow-cream-15g", "Gentle: avocado + aloe vera"), ("avocado-korean-night-cream", "With niacinamide + kojic acid"), ("avocado-night-cream", "Richest, for dry skin")]
    lab, foot = ("एवोकाडो क्रीम खरीदें", "फ्री शिपिंग · कैश ऑन डिलीवरी · सील जार पर 7 दिन रिटर्न") if lang == "hi" else ("Shop avocado creams", "Free shipping · Cash on Delivery · 7-day returns on sealed jars")
    items = "".join(f'<li><a href="/product/{s}/"><b>{esc(PBY[s]["name"].replace(" 15g", ""))} <small>{PBY[s]["size"]}</small></b><span>{t}</span><em>{inr(PBY[s]["price"])}</em></a></li>' for s, t in picks)
    return (f'<aside class="buybox" aria-label="{lab}"><span class="buybox-l">{lab}</span><ul>{items}</ul>'
            f'<p>{foot} · <a href="{wa("Hi Mirc Glow, I want to order an avocado cream.")}" target="_blank" rel="noopener">Order on WhatsApp</a></p></aside>')

def with_buybox(raw, lang="en"):
    """Place the avocado buy box just before the second <h2> (after the opening section)."""
    box = avocado_buybox(lang)
    i = raw.find("<h2"); j = raw.find("<h2", i + 3) if i >= 0 else -1
    k = j if j > 0 else i
    return raw[:k] + box + raw[k:] if k > 0 else raw + box

def product_cta(p):
    return (f'<aside class="pcta" aria-label="Featured cream">{photo(p, "", alt=p["name"])}<div><span class="lab">From this guide</span><h2>{esc(p["name"])} · {p["size"]}</h2><p>{esc(p["lead"])}</p>'
            f'<div class="row"><span class="price">{inr(p["price"])} <s>{inr(p["mrp"])}</s></span><a class="order" href="{wa(order_msg(p))}" target="_blank" rel="noopener">Order on WhatsApp</a><a class="link" href="/product/{p["slug"]}/">Details</a></div></div></aside>')

def quick_box(p):
    q = GEO.QUICK.get(p["slug"])
    if not q: return f'<div class="short"><p>{esc(p["ex"])}</p></div>'
    facts = "".join(f"<li>{esc(x)}</li>" for x in q[1])
    return f'<aside class="quick" aria-label="Quick answer"><span class="quick-l">Quick answer</span><p>{esc(q[0])}</p><ul>{facts}</ul></aside>'

def build_post(p):
    url = f"/{p['slug']}/"
    raw = read(os.path.join(SRC, "posts", p["slug"] + ".html"))
    if p["slug"] in GEO.SHORT_ANSWERS: raw += qa_html(GEO.SHORT_ANSWERS[p["slug"]])
    if url in VIDEO_ON:
        k = raw.find("<h2")
        raw = (raw[:k] + video_html(url) + raw[k:]) if k > 0 else video_html(url) + raw
    if wants_buybox(p["slug"], p["topic"]): raw = with_buybox(raw)
    body_html, toc = add_h2_ids(lazy_imgs(raw))
    faqs = faqs_from(raw)
    mins = max(2, round(words(raw) / 200))
    hub = HUB.get(p["slug"])
    canonical = SITE + f"/{hub}/" if hub else None
    topic_name, prod_slug = TOPICS[p["topic"]]
    prod = PBY[prod_slug]
    crumbs = [("Home","/"),("Journal","/blog/")]
    pc = next((c for c, v in WPCATS.items() if p["slug"] in v[2] and len(v[2]) > 1), None)
    if pc: crumbs.append((WPCATS[pc][0], f"/category/{pc}/"))
    crumbs.append((p["title"], url))
    art = {"@type":"BlogPosting","@id":SITE+url+"#article","headline":p["title"],"description":p["rd"],"datePublished":p["date"]+"T09:00:00+05:30","dateModified":TODAY+"T09:00:00+05:30",
           "author":{"@type":"Person","name":"Mohammed Nihal","url":SITE+"/about-the-author/","jobTitle":"Founder, Mirc Glow"},"publisher":{"@id":ORG_ID},"mainEntityOfPage":SITE+url,
           "image":SITE+prod["img"],"inLanguage":"en-IN","articleSection":topic_name,"wordCount":words(raw),"isPartOf":{"@id":SITE+"/#website"},
           "about":[{"@type":"Thing","name":topic_name}]}
    nodes = [ORG, art, crumbs_ld(crumbs)] + ([video_ld(url)] if url in VIDEO_ON else [])
    if faqs: nodes.append(faq_ld(faqs))
    out = head(p["rt"], p["rd"], url, og_type="article", image=prod["img"], canonical=canonical,
               extra=f'<meta property="article:published_time" content="{p["date"]}T09:00:00+05:30"><meta property="article:modified_time" content="{TODAY}T09:00:00+05:30">' + ld(*nodes))
    out += header("/blog/")
    merged = f'<p class="merged"><b>Updated guide.</b> We have combined this topic into one fuller, up-to-date guide: <a href="/{hub}/">{esc(POST_BY[hub]["title"])}</a>.</p>' if hub else ""
    toc_html = ""
    if len(toc) >= 3:
        toc_html = '<nav class="toc" aria-label="On this page"><details open><summary>On this page</summary><ol>' + "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i,t in toc) + '</ol></details></nav>'
    else:
        toc_html = '<div></div>'
    rel = "".join(post_card(q) for q in related_posts(p))
    out += f'''<main id="main">{crumbs_html(crumbs)}
<article>
<header class="w art-top"><span class="lab">{esc(topic_name)}</span><h1 class="dsp">{esc(p["title"])}</h1>
<div class="byline"><span>By <a href="/about-the-author/"><b>Mohammed Nihal</b></a>, founder</span><span>Published <time datetime="{p["date"]}">{fmt_date(p["date"])}</time></span><span>Updated <time datetime="{TODAY}">{fmt_date(TODAY)}</time></span><span>{mins} min read</span></div>
{merged}
{quick_box(p)}
</header>
<div class="w layout">{toc_html}<div><div class="prose">{body_html}</div>{product_cta(prod)}{guide_note()}</div></div>
</article>
<section class="band tight" style="background:var(--milk)" aria-labelledby="h-rel"><div class="w"><div class="head"><span class="lab">Keep reading</span><h2 class="dsp" id="h-rel" style="font-size:clamp(2rem,4vw,3rem)">Related <em>guides</em></h2></div><div class="posts">{rel}</div></div></section>
</main>
'''
    out += footer()
    write(url, out)

def build_blog():
    order = ["routine","night","avocado","glutathione","kojic"]
    hubs = [POST_BY[s] for s in ["is-avocado-cream-good-for-your-skin","glass-skin-routine-for-indian-skin","glutathione-cream-benefits"]]
    chips = "".join(f'<a href="#t-{t}">{TOPICS[t][0]}</a>' for t in order)
    secs = ""
    for t in order:
        items = sorted([p for p in LIVE_POSTS if p["topic"] == t], key=lambda x: x["date"], reverse=True)
        secs += f'<section class="w" id="t-{t}" style="padding-bottom:clamp(48px,6vw,80px);scroll-margin-top:110px"><h2 class="dsp" style="font-size:clamp(2rem,4vw,3rem);margin-bottom:28px">{TOPICS[t][0]}</h2><div class="posts">{"".join(post_card(p) for p in items)}</div></section>'
    tools = '''<section class="band tight" style="background:var(--milk)"><div class="w"><div class="head"><span class="lab">Tools</span><h2 class="dsp" style="font-size:clamp(2rem,4vw,3rem)">Find your <em>routine</em></h2></div>
<div class="grid3"><a class="post" href="/skin-quiz/"><div class="art t-night"><em>Quiz</em></div><h3>Skin quiz</h3><p>Four questions, one cream recommendation.</p></a>
<a class="post" href="/skincare-routine-builder/"><div class="art t-routine"><em>Routine</em></div><h3>Skincare routine builder</h3><p>Morning and night steps for your skin type.</p></a>
<a class="post" href="/skincare-ingredient-glossary/"><div class="art t-kojic"><em>Glossary</em></div><h3>Ingredient glossary</h3><p>15 skincare ingredients in plain English.</p></a></div></div></section>'''
    for url, title, desc, h1, crumbs in [
        ("/blog/","Skincare Blog: Night Cream, Glutathione and Glass Skin Guides | Mirc Glow","Plain-English skincare guides from Mirc Glow on night creams, glutathione, kojic acid, avocado care and glass skin routines for Indian skin.","The journal",[("Home","/"),("Journal","/blog/")]),
    ]:
        il = {"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":SITE+f"/{p['slug']}/"} for i,p in enumerate(LIVE_POSTS)]}
        cp = {"@type":"CollectionPage","@id":SITE+url,"url":SITE+url,"name":h1,"description":desc}
        out = head(title, desc, url, extra=ld(ORG, cp, il, crumbs_ld(crumbs)))
        out += header("/blog/")
        out += f'''<main id="main">{crumbs_html(crumbs)}<div class="w ptop"><span class="lab"><span lang="ko">가이드</span> · Skincare guides</span><h1 class="dsp">{esc(h1)}</h1>{qbox(f"The Mirc Glow journal has {len(LIVE_POSTS)} free skincare guides for Indian skin and weather, on night creams, avocado cream, glutathione, kojic acid, dark spots and glass skin routines, plus Hindi guides. Each guide opens with a short answer and is written by founder Mohammed Nihal.", label="In short")}<p>Honest, plain-English guides to night creams, glutathione, kojic acid and glass skin routines for Indian weather. Written by the Mirc Glow team; general information, not medical advice.</p><nav class="chips" aria-label="Topics">{chips}</nav></div>
<section class="w" style="padding-bottom:clamp(48px,6vw,80px)"><h2 class="lab" style="margin-bottom:22px">Start here</h2><div class="journal">{"".join(post_card(p) for p in hubs)}</div></section>
{secs}{tools}</main>'''
        out += footer()
        write(url, out)

FBT = {"glass-glow-cream":"avocado-night-cream","avocado-night-cream":"avocado-face-cream","glutathione-cream":"avocado-night-cream",
       "avocado-korean-night-cream":"avocado-glow-cream-15g","avocado-face-cream":"avocado-night-cream","avocado-glow-cream-15g":"avocado-korean-night-cream"}

def fbt_html(p):
    """Amazon-style 'Frequently bought together': this cream + its natural partner, one WhatsApp message for both."""
    if p["slug"] not in FBT: return ""
    q = PBY[FBT[p["slug"]]]; total = p["price"] + q["price"]
    msg = (f"Hi Mirc Glow, I'd like to order:\n• {p['name']} ({p['size']}) – {inr(p['price'])}\n• {q['name']} ({q['size']}) – {inr(q['price'])}\n"
           f"Total: {inr(total)}\n\nName:\nFull address with pincode:\nPayment: Cash on Delivery / pay online")
    combo = next((c for c in SETS if set(c["parts"]) == {p["slug"], q["slug"]}), None)
    alt = (f'<p class="az-alt">Or get both as the <a href="/product/{combo["slug"]}/">{esc(combo["name"])}</a> for <b>{inr(combo["price"])}</b> '
           f'and save {inr(total - combo["price"])}.</p>') if combo else ""
    item = lambda x, this: (f'<a class="az-fi" href="/product/{x["slug"]}/">{photo(x, "az-fph")}<span>{"<b>This item:</b> " if this else ""}{esc(x["name"])} '
                            f'<small>{x["size"]}</small></span><b class="az-fp">{inr(x["price"])}</b></a>')
    return (f'<section class="w az-fbt" aria-labelledby="h-fbt"><h2 id="h-fbt" class="az-h">Frequently bought together</h2>'
            f'<div class="az-fbox"><div class="az-fitems">{item(p, True)}<span class="az-plus" aria-hidden="true">+</span>{item(q, False)}</div>'
            f'<div class="az-ftot"><p>Total price: <b>{inr(total)}</b></p><a class="yb yb-fill" href="{wa(msg)}" target="_blank" rel="noopener">{WA_SVG}<span>Buy both on WhatsApp</span></a>{alt}</div></div></section>')

def compare_html(p):
    """Amazon-style 'Compare with similar items' table."""
    pool = SINGLES if "parts" not in p else SETS
    items = [p] + [q for q in pool if q["slug"] != p["slug"]][:3]
    pct = lambda x: round((x["mrp"] - x["price"]) * 100 / x["mrp"])
    head = "".join(f'<th scope="col"><a href="/product/{x["slug"]}/">{photo(x, "az-cph")}<span>{"This item: " if x is p else ""}{esc(x["name"])}</span></a></th>' for x in items)
    rows = [("Price", lambda x: f'<b>{inr(x["price"])}</b> <s>{inr(x["mrp"])}</s> <em>{pct(x)}% off</em>'), ("Size", lambda x: x["size"]),
            ("Key ingredients", lambda x: esc(", ".join(x["ing"][:5]))), ("Best for", lambda x: esc(x["best"])), ("When to use", lambda x: esc(x["when"])),
            ("", lambda x: buy_btn(x, "Buy", "yb yb-fill yb-sm") if x is not p else '<span class="az-cur">You are viewing this</span>')]
    body = "".join(f'<tr><th scope="row">{t}</th>' + "".join(f"<td>{f(x)}</td>" for x in items) + "</tr>" for t, f in rows)
    return (f'<section class="w az-cmp" aria-labelledby="h-cmp"><h2 id="h-cmp" class="az-h">Compare with similar items</h2>'
            f'<div class="az-cwrap"><table><thead><tr><td></td>{head}</tr></thead><tbody>{body}</tbody></table></div></section>')

RECENT_HTML = '<section class="w az-recent" data-recent hidden aria-labelledby="h-recent"><h2 id="h-recent" class="az-h">Your recently viewed items</h2><div class="az-rrow"></div></section>'

def qbox(text, facts=(), label="Quick answer", lang="en"):
    lab = "छोटा जवाब" if lang == "hi" else label
    lis = "".join(f"<li>{esc(x)}</li>" for x in facts)
    return f'<aside class="quick" aria-label="{esc(lab)}"><span class="quick-l">{esc(lab)}</span><p>{esc(text)}</p>{"<ul>" + lis + "</ul>" if lis else ""}</aside>'

def product_quick(p):
    pg = round(p["price"] / p["grams"], 1)
    if "parts" in p:
        parts = " and ".join(PBY[x]["name"] for x in p["parts"])
        sep = sum(PBY[x]["price"] for x in p["parts"])
        t = (f"The {BRAND} {p['name']} is a set of {parts} ({p['size']}). It costs {inr(p['price'])} (MRP {inr(p['mrp'])}), "
             f"{inr(sep - p['price'])} less than buying the jars separately, with free shipping and Cash on Delivery across India. Best for: {p['best'].lower()}.")
    else:
        t = (f"{BRAND} {p['name']} is a {p['size']} Korean-inspired face cream made in Karnataka, India, with {', '.join(p['ing'][:-1]).lower()} and {p['ing'][-1].lower()}. "
             f"It costs {inr(p['price'])} (MRP {inr(p['mrp'])}), about {inr(int(pg)) if pg == int(pg) else '₹' + str(pg)} per gram. Best for: {p['best'].lower()}.")
    facts = [f"Use: {p['use']}", f"Skin type: {p['skin']}", f"A jar lasts: {p['lasts'].lower()}", "Free shipping, Cash on Delivery, 7-day returns on sealed jars"]
    return qbox(t, facts, "In short")

def city_quick(g):
    city = g["crumb"]
    t = (f"Yes. {BRAND} supplies night cream in kg in {city}: avocado night cream, avocado cream and glutathione cream by the kilo, from 1 kg, "
         f"couriered from Bhatkal, Karnataka, usually in 3 to 7 days. Send the cream, quantity and your city on WhatsApp ({PHONE}) for the price per kg.")
    return qbox(t, ["From 1 kg", "Sample before a bulk order", "Price per kg falls as quantity rises", "For salons, parlours, resellers and new brands"])

PAGE_QUICK = {
 "avocado-cream": ("Avocado cream is a rich moisturiser made with avocado that helps skin feel soft and comfortable. Mirc Glow makes four avocado creams from ₹349 to ₹649: the 10 g and 15 g Avocado Glow creams for daytime and first-time use, and the 30 g Avocado Night Cream and 25 g Avocado Korean Night Cream for nights.",
                   ["Dry skin: Avocado Night Cream 30 g (₹649)", "Most skin types: Avocado Korean Night Cream 25 g (₹649)", "Simplest formula: Avocado Glow Cream 15 g, avocado + aloe vera (₹399)", "Use a pea-sized amount; sunscreen every morning"]),
 "korean-night-cream": ("A Korean night cream is the last, sealing step of a K-beauty evening routine, used for a hydrated, glass-skin look by morning. Mirc Glow makes Korean-inspired night creams in India from ₹649, including the Avocado Korean Night Cream, the Glutathione Cream and the Glass Glow Cream.",
                   ["Apply a pea-sized amount as the last step at night", "Avocado Korean Night Cream: most skin types", "Glass Glow Cream: glutathione, niacinamide, hyaluronic acid, centella, alpha arbutin", "Free shipping and Cash on Delivery in India"]),
 "bulk-night-cream": ("Yes, Mirc Glow sells night cream in kg. Avocado night cream, avocado cream and glutathione cream are supplied by weight from 1 kg to salons, parlours, resellers and new brands across India. Message the cream, quantity and city on WhatsApp for the price per kg.",
                   ["From 1 kg; larger orders get a lower rate per kg", "1 kg fills about 33 jars of 30 g", "Sample available before a bulk order", "Shipped from Bhatkal, Karnataka, usually in 3 to 7 days"]),
 "skincare-gift-sets": ("Mirc Glow skincare gift sets cost ₹849 to ₹2,699: the Day & Night Combo, the Night Cream Combo, the Glass Glow Night Duo and the three-cream Korean Glass Skin Kit. Each costs less than buying the jars separately and ships free across India.",
                   ["Under ₹1,000: Day & Night Combo (₹849)", "Premium: Glass Glow Night Duo (₹2,699)", "Full routine: Korean Glass Skin Kit (₹1,999)"]),
 "ingredients": ("Most Mirc Glow creams are built on aloe vera, vitamin B3 (niacinamide) and kojic acid, plus a hero ingredient such as avocado or glutathione. Avocado Glow Cream 15 g is avocado and aloe vera only, and Glass Glow Cream uses glutathione, niacinamide, hyaluronic acid, centella asiatica and alpha arbutin.", []),
 "avocado-cream-hindi": ("एवोकाडो क्रीम एक मॉइस्चराइज़र है जो त्वचा को मुलायम और आरामदायक महसूस कराती है। Mirc Glow की चार एवोकाडो क्रीम ₹349 से ₹649 तक हैं: दिन के लिए हल्की Avocado Glow क्रीम और रात के लिए Avocado Night Cream व Avocado Korean Night Cream।", []),
 "korean-night-cream-hindi": ("कोरियन नाइट क्रीम K-beauty रात के रूटीन का आख़िरी स्टेप है, जो सुबह तक त्वचा को नमी भरी और ग्लास-स्किन जैसी दिखाने में मदद करती है। Mirc Glow की कोरियन-इंस्पायर्ड नाइट क्रीम ₹649 से शुरू होती हैं।", []),
}
PAGE_QUICK.update({
 "about": ("Mirc Glow is a Korean-inspired skincare brand from Bhatkal, Karnataka, India, founded by Mohammed Nihal. It makes avocado night creams, a glutathione cream and the Glass Glow Cream (₹349 to ₹2,499), sells them through mircglow.com and WhatsApp with free shipping and Cash on Delivery across India, and supplies night cream in kg to salons and resellers.",
           ["Founded by Mohammed Nihal in Bhatkal, Karnataka", "6 face creams and 4 sets, ₹349 to ₹2,699", "Orders on WhatsApp +91 99808 81230", "Cosmetic claims only: no fairness or whitening promises"]),
 "faq": ("Mirc Glow ships free across India in about 3 to 7 days, accepts Cash on Delivery or an online payment link, and takes back sealed jars within 7 days. You order by tapping Buy Now, which opens WhatsApp with your order written; most creams are used as the last step at night, with sunscreen every morning.", []),
 "shipping-policy": ("Shipping is free on every Mirc Glow order within India. Most orders arrive in 3 to 7 days, and you get a tracking number on WhatsApp or SMS when the parcel is dispatched. Cash on Delivery is available. We do not ship outside India.", []),
 "returns-refunds": ("Unopened, sealed Mirc Glow jars can be returned within 7 days of delivery. Damaged, wrong or expired items are replaced or refunded; tell us on WhatsApp with a photo. Refunds are made within 5 to 7 working days after the return is checked. Opened jars cannot be returned for hygiene reasons.", []),
 "contact": ("Contact Mirc Glow on WhatsApp or phone at +91 99808 81230, or write to us at Azad Nagar 4th Cross, Bhatkal, Karnataka 581320, India. WhatsApp is the fastest way to order, ask about a cream or get a bulk quote.", []),
 "track-order": ("To track a Mirc Glow order, use the tracking number we send on WhatsApp or SMS when your parcel is dispatched, or message +91 99808 81230 with your name and order details. Most orders arrive in 3 to 7 days.", []),
 "skin-quiz": ("The Mirc Glow skin quiz asks four quick questions about your skin type, main concern and routine, then suggests one cream. It takes under a minute and needs no sign-up.", []),
 "skincare-ingredient-glossary": ("This glossary explains 15 common skincare ingredients in plain English, including avocado, aloe vera, niacinamide (vitamin B3), kojic acid, glutathione, vitamin C, alpha arbutin, hyaluronic acid and centella asiatica, with what each does and who it suits.", []),
 "skincare-routine-builder": ("The routine builder gives you a simple morning and night skincare routine for your skin type in a few taps: cleanse, moisturise and protect in the morning; cleanse, treat and seal at night.", []),
 "about-the-author": ("Mirc Glow's skincare guides are written by founder Mohammed Nihal in Bhatkal, Karnataka. They are general skincare information, checked against established ingredient knowledge, and avoid medical, fairness or guaranteed-result claims.", []),
 "privacy": ("Mirc Glow collects only what it needs to deliver and support your order: your name, address, phone number, email if you share it, and what you ordered. Online payments go through a secure payment gateway, so we never see your card or UPI details. We share details only with couriers, payment gateways, our service providers and authorities where the law requires, and we do not sell your personal information. The site needs no account or login.", []),
 "terms": ("These terms apply when you use mircglow.com or order from Mirc Glow. Our products are cosmetics, not medicines, and results vary. Prices are in Indian Rupees, with any taxes confirmed before you pay; you can pay online or by Cash on Delivery. Orders are placed on WhatsApp or through a payment link, and paid orders we cancel are refunded in full. Patch test before first use.", []),
 "editorial-policy": ("Mirc Glow guides are written in plain English or Hindi by the founder, reviewed and dated, and updated when facts or prices change. We never claim a cosmetic changes skin colour, treats a medical condition or works in a fixed number of days.", []),
})
for _hub_slug, _hub in HUB.items():
    if _hub in GEO.QUICK and _hub_slug not in GEO.QUICK:
        GEO.QUICK[_hub_slug] = GEO.QUICK[_hub]
PLAN_QUICK = {m["slug"]: (m["quick"], m.get("facts", [])) for m in PLAN if m.get("quick") and m["kind"] == "bulk"}
PAGE_QUICK.update(PLAN_QUICK)

REVIEWS = [r for r in json.load(open(os.path.join(SRC, "reviews.json"), encoding="utf-8"))["reviews"] if r.get("text") and 1 <= int(r.get("rating", 0)) <= 5]

def reviews_for(p):
    slugs = {p["slug"]} | set(p.get("parts", []))
    return [r for r in REVIEWS if r["product"] == p["slug"]] if "parts" not in p else [r for r in REVIEWS if r["product"] in slugs]

def stars(n):
    full = int(n + 0.5)
    return f'<span class="rv-st" aria-label="{n:.1f} out of 5 stars">' + "★" * full + "☆" * (5 - full) + "</span>"

def reviews_html(p):
    rs = reviews_for(p)
    msg = (f"Hi Mirc Glow, here is my review of the {p['name']} ({p['size']}):\n\nRating (1 to 5 stars): \nMy review: \n"
           "First name and city (shown with the review): ")
    btn = f'<a class="yb yb-line rv-btn" href="{wa(msg)}" target="_blank" rel="noopener">{WA_SVG}<span>Write a review on WhatsApp</span></a>'
    if not rs:
        return (f'<section class="w rv" aria-labelledby="h-rv"><h2 id="h-rv" class="az-h">Customer reviews</h2>'
                f'<div class="rv-empty"><p>No reviews yet for the {esc(p["name"])}. Bought it? Tell us how your skin feels: your review helps other shoppers.</p>{btn}</div></section>')
    avg = sum(int(r["rating"]) for r in rs) / len(rs)
    items = "".join(f'<article class="rv-i">{stars(int(r["rating"]))}<p>{esc(r["text"])}</p><span class="rv-by">{esc(r["name"])}, {esc(r.get("city",""))} · {fmt_date(r["date"])}</span></article>' for r in sorted(rs, key=lambda r: r["date"], reverse=True)[:20])
    return (f'<section class="w rv" aria-labelledby="h-rv"><h2 id="h-rv" class="az-h">Customer reviews</h2>'
            f'<div class="rv-sum">{stars(avg)} <b>{avg:.1f} out of 5</b> · {len(rs)} review{"s" if len(rs) > 1 else ""}</div><div class="rv-list">{items}</div>{btn}</section>')

def reviews_ld(p, d):
    rs = reviews_for(p)
    if not rs: return d
    avg = sum(int(r["rating"]) for r in rs) / len(rs)
    d["aggregateRating"] = {"@type":"AggregateRating","ratingValue":f"{avg:.1f}","reviewCount":len(rs),"bestRating":5,"worstRating":1}
    d["review"] = [{"@type":"Review","author":{"@type":"Person","name":r["name"]},"datePublished":r["date"],"reviewBody":r["text"],
                    "reviewRating":{"@type":"Rating","ratingValue":int(r["rating"]),"bestRating":5}} for r in rs[:10]]
    return d

AMZ_URL = "https://www.amazon.in/s?k=Magical+Touch+Avocado+Korean+Night+Cream"
AMZ_FOR = {"avocado-korean-night-cream", "avocado-night-cream"}
AMZ_REVIEWS = [  # copied word for word from verified-purchase reviews on Amazon.in (Magical Touch listing, same formula)
 ("Valkesh A.", 5, "18 July 2026", "Value for money", "I've been using Avocado Korean Night Cream regularly, and my skin feels deeply nourished, soft, and hydrated. My dullness has reduced, and my face looks healthier."),
 ("Prinkal K.", 5, "15 July 2026", "Very satisfied with this seller.", "Really impressed with this avocado night cream. It feels lightweight, absorbs quickly, and leaves my skin soft, smooth, and well-hydrated by morning. Great for daily use!"),
 ("Purushottam K.", 5, "15 July 2026", "Good Product", "Loved this avocado night cream. It's lightweight, absorbs quickly, and leaves my skin feeling fresh and moisturized."),
 ("Poulami M.", 3, "7 September 2026", "Not so good", "গন্ধ টা খুব তীব্র not so good (translation: the smell is very strong)"),
]

def amazon_reviews_html(p):
    if p["slug"] not in AMZ_FOR: return ""
    items = "".join(f'<article class="rv-i">{stars(r)}<b class="rv-t">{esc(t)}</b><p>{esc(x)}</p><span class="rv-by">{esc(n)} · Verified purchase on Amazon.in · {d}</span></article>' for n, r, d, t, x in AMZ_REVIEWS)
    return (f'<section class="w rv rv-amz" aria-labelledby="h-amz"><h2 id="h-amz" class="az-h">Reviews from Amazon.in</h2>'
            f'<p class="rv-note">Our avocado night cream is also sold on Amazon.in under our sister label <b>Magical Touch</b> (Avocado Korean Night Cream, same formula: avocado, aloe vera, vitamin B3 and kojic acid). '
            f'Below is a selection of recent verified-purchase reviews from there, including a critical one, copied word for word. Results vary from person to person.</p>'
            f'<div class="rv-list">{items}</div></section>')

# Videos: content/videos.json lists each video (name, description, src mp4, thumb jpg, date, dur "PT30S", pages it appears on).
# A page shows its video above the first H2, with VideoObject schema and a video entry in the sitemap.
VIDEOS = json.load(open(os.path.join(SRC, "videos.json"), encoding="utf-8"))
VIDEO_BY_URL = {u: v for v in VIDEOS for u in v["pages"]}
VIDEO_ON = set(VIDEO_BY_URL)

def video_html(url):
    if url not in VIDEO_ON: return ""
    v = VIDEO_BY_URL[url]
    return (f'<figure class="vid"><video controls preload="none" playsinline width="720" height="1280" poster="{v["thumb"]}">'
            f'<source src="{v["src"]}" type="video/mp4"></video><figcaption>{esc(v["name"])} ({int(re.sub(r"[^0-9]", "", v.get("dur", "PT30S")) or 30)} seconds)</figcaption></figure>')

def video_ld(url):
    v = VIDEO_BY_URL[url]
    return {"@type":"VideoObject","@id":SITE+url+"#video","name":v["name"],"description":v["description"],"thumbnailUrl":[SITE+v["thumb"]],
            "uploadDate":v["date"],"duration":v["dur"],"contentUrl":SITE+v["src"],"publisher":{"@id":ORG_ID},"inLanguage":"en-IN"}

def rating_line(p):
    rs = reviews_for(p)
    if not rs:
        amz = ' <a class="rl rl-amz" href="#h-amz">See Amazon.in reviews ›</a>' if p["slug"] in AMZ_FOR else ""
        return '<a class="rl rl-0" href="#h-rv"><span class="rv-st" aria-hidden="true">☆☆☆☆☆</span> Be the first to review</a>' + amz
    avg = sum(int(r["rating"]) for r in rs) / len(rs)
    return f'<a class="rl" href="#h-rv"><span class="rl-b">{avg:.1f} ★</span> {len(rs)} rating{"s" if len(rs) > 1 else ""} &amp; reviews</a>'

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
    nodes = [ORG, reviews_ld(p, product_ld(p, url)), crumbs_ld(crumbs)] + ([video_ld(url)] if url in VIDEO_ON else [])
    if faqs: nodes.append(faq_ld(faqs))
    out = head(p["rt"], p["rd"], url, og_type="product", image=p["img"],
               extra=f'<meta property="product:price:amount" content="{p["price"]}"><meta property="product:price:currency" content="INR"><meta property="product:availability" content="in stock"><link rel="preload" as="image" href="{p["img"][:-4]}.mg.webp" type="image/webp" fetchpriority="high">' + ld(*nodes))
    out += header("/shop/")
    out += f'''<main id="main">{crumbs_html(crumbs)}
<div class="w pdp">
<div class="gallery"><div class="gal-box">{photo(p, "", eager=True, alt=strip_tags(p["h1"]))}<span class="pc-off">{pct}% off</span></div></div>
<div class="buy" id="buy">
<span class="eyebrow">Mirc Glow · {esc(p["tag"])}</span>
<h1 class="pdp-t">{esc(p["h1"])}</h1>
{rating_line(p)}
<p class="panel-pr"><s>{inr(p["mrp"])}</s> <b>{inr(p["price"])}</b> <span class="save">Save {inr(sv)}</span></p>
<p class="panel-tax">Taxes included. You save {inr(sv)} {save_note}. Free shipping across India.</p>
<p class="az-del" data-del><b>FREE delivery</b> in 3–7 days across India · Cash on Delivery available</p>
<p class="lead2">{esc(p["lead"])}</p>
{qty_box(p["slug"])}
<div class="buy2">{buy_btn(p, "Buy Now")}{buy_btn(p, "Add to Cart", "yb yb-line", go=False)}</div>
{wa_btn(p, "Order on WhatsApp instead")}
<p class="howpay">Pay online with UPI or card ({PREPAID_PCT}% off), or choose Cash on Delivery at checkout. First order? Use code <b>GLOW10</b> for 10% off. Questions? <a href="{wa("Hi Mirc Glow, I have a question about the " + p["name"] + ".")}" target="_blank" rel="noopener">Ask us on WhatsApp</a>.</p>
{PAY_CHIPS}
<ul class="ticks">{pts}</ul>
<div class="trust4"><div><span>🚚</span><b>Free shipping</b><small>3 to 7 days</small></div><div><span>💵</span><b>Cash on Delivery</b><small>Or pay online</small></div><div><span>↩️</span><b>7-day returns</b><small><a href="/returns-refunds/">Sealed jars</a></small></div><div><span>💬</span><b>WhatsApp help</b><small>{PHONE}</small></div></div>
{spec}
<p class="fine">Cosmetic product. Patch test before first use. Results vary from person to person. Does not change your natural skin tone.</p>
</div>
</div>
<section class="w" aria-label="Benefits">{banner(p)}</section>
{fbt_html(p)}
<section class="w" aria-label="Video">{video_html(url)}</section>
<section class="w details">{toc_html}<div class="prose">{product_quick(p)}{body_html}</div></section>
{compare_html(p)}
{reviews_html(p)}
{amazon_reviews_html(p)}
{RECENT_HTML}
<section class="sec soft" aria-labelledby="h-more"><div class="w"><span class="eyebrow">Pairs well with</span><h2 class="sh" id="h-more">You may also like</h2><div class="grid4">{"".join(card_html(q) for q in others)}</div></div></section>
</main>
<script type="application/json" id="rv-item">{json.dumps({"u": url, "n": p["name"], "i": p["img"][:-4] + ".mg.webp" if p["img"].endswith(".png") else p["img"], "p": inr(p["price"]), "m": inr(p["mrp"])}, ensure_ascii=False)}</script>
<div class="pbar" id="pbar" hidden><div><b>{esc(p["name"])}</b><span>{inr(p["price"])}</span></div>{buy_btn(p, "Buy Now", "yb yb-fill yb-sm")}</div>
'''
    out += footer()
    write(url, out)

def build_page(g):
    url = f"/{g['slug']}/"
    raw = read(os.path.join(SRC, "pages", g["slug"] + ".html"))
    if g["slug"] in GEO.PAGE_ANSWERS: raw += qa_html(GEO.PAGE_ANSWERS[g["slug"]])
    if g["slug"] in GEO.HINDI_FAQ: raw += "<h2>अक्सर पूछे जाने वाले सवाल (FAQ)</h2>" + "".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in GEO.HINDI_FAQ[g["slug"]])
    if g["lang"] == "hi":
        others = [x for x in PAGES if x["lang"] == "hi" and x["slug"] != g["slug"]]
        raw += "<h2>और हिंदी गाइड</h2><ul>" + "".join(f'<li><a href="/{x["slug"]}/">{esc(x["title"])}</a></li>' for x in others) + "</ul>"
    if g["kind"] != "legacy" and wants_buybox(g["slug"]): raw = with_buybox(raw, g["lang"])
    raw = lazy_imgs(raw)
    faqs = faqs_from(raw)
    if g["kind"] != "legacy" and g["slug"] in PAGE_QUICK and "</h1>" in raw:
        raw = raw.replace("</h1>", "</h1>" + qbox(*PAGE_QUICK[g["slug"]], lang=g["lang"]), 1)
    if g["slug"] in CITY: cr = [("Home","/"),("Bulk orders","/bulk-night-cream/"),(g["crumb"], url)]
    else: cr = [("Home","/"),(g["crumb"], url)]
    alts = None
    if g["alt"]:
        en, hi = (g["slug"], g["alt"]) if g["lang"] == "en" else (g["alt"], g["slug"])
        alts = [("en-IN", f"/{en}/"), ("hi-IN", f"/{hi}/"), ("x-default", f"/{en}/")]
    ptype = {"about":"AboutPage","contact":"ContactPage","faq":"FAQPage"}.get(g["slug"], "WebPage")
    wp = {"@type":ptype if ptype != "FAQPage" else "WebPage","@id":SITE+url,"url":SITE+url,"name":g["title"],"description":g["rd"],"inLanguage":LANG_TAG.get(g["lang"], "en-IN"),"isPartOf":{"@id":SITE+"/#website"},"dateModified":TODAY}
    nodes = [ORG, wp, crumbs_ld(cr)]
    if g["slug"] in CITY or g["slug"] == "bulk-night-cream":
        city = g["crumb"] if g["slug"].startswith("night-cream-in-kg-") else None
        nodes.append({"@type":"Service","@id":SITE+url+"#service","name":g["title"],"serviceType":"Wholesale supply of night cream and avocado cream by the kilogram",
            "provider":{"@id":ORG_ID},"areaServed":({"@type":"City","name":city,"containedInPlace":{"@type":"Country","name":"India"}} if city else {"@type":"Country","name":"India"}),
            "audience":{"@type":"BusinessAudience","audienceType":"Salons, beauty parlours, resellers and skincare brands"},
            "availableChannel":{"@type":"ServiceChannel","servicePhone":{"@type":"ContactPoint","telephone":"+919980881230","contactType":"sales"},"serviceUrl":SITE+url},
            "offers":{"@type":"Offer","eligibleQuantity":{"@type":"QuantitativeValue","minValue":1,"unitCode":"KGM"},"priceCurrency":"INR","availability":"https://schema.org/InStock","url":SITE+url}})
    if faqs: nodes.append(faq_ld(faqs))
    out = head(g["rt"], g["rd"], url, lang=g["lang"], image=g["img"], alts=alts, extra=ld(*nodes))
    out += header()
    qk = city_quick(g) if g["slug"].startswith("night-cream-in-kg-") else (qbox(*PAGE_QUICK[g["slug"]], lang=g["lang"]) if g["slug"] in PAGE_QUICK else "")
    if g["kind"] == "legacy":
        if qk and "</h1>" in raw:
            j = raw.find("</p>", raw.index("</h1>"))
            raw = raw[:j+4] + qk + raw[j+4:] if j > 0 else raw.replace("</h1>", "</h1>" + qk, 1)
        out += f'<main id="main" class="lg">{crumbs_html(cr)}{raw}{at_glance_html() if g["slug"]=="about" else ""}</main>'
    else:
        out += f'<main id="main" class="plain">{crumbs_html(cr)}<div class="w"><article class="prose">{raw}<p style="margin-top:3em;font-size:.85rem;color:var(--muted)">{"अंतिम अपडेट" if g["lang"]=="hi" else "Last reviewed"}: {fmt_date(TODAY)}</p></article></div></main>'
    out += footer()
    write(url, out)


WPCATS = {  # WordPress post categories (same URLs as on WordPress)
 "night-cream-guides": ("Night Creams","How to choose and use a night cream in India: by skin type, for men, for oily and dry skin, and step-by-step night routines.",
   ["how-to-apply-night-cream","night-cream-for-men","night-cream-for-oily-skin","best-night-cream-for-glowing-skin","which-is-the-no-1-night-cream-in-india","how-to-build-a-simple-night-skincare-routine"]),
 "avocado-skincare": ("Avocado Skincare","Honest guides to avocado cream and avocado night cream: what avocado does for skin, who it suits, side effects, and how to use it.",
   ["avocado-day-cream","avocado-cream-for-dry-skin","avocado-night-cream-side-effects","is-avocado-cream-good-for-your-skin","is-avocado-night-cream-good","how-to-make-avocado-night-cream-at-home","can-i-use-avocado-night-cream-every-night"]),
 "glutathione-kojic-acid": ("Glutathione and Kojic Acid","Plain-English guides to glutathione cream and kojic acid cream: benefits, how long they take, side effects, how to use them and how they compare.",
   ["kojic-acid-cream-for-dark-spots","kojic-acid-vs-glutathione","how-to-use-glutathione-cream","how-long-does-glutathione-cream-take-to-work","glutathione-cream-side-effects","glutathione-cream-benefits"]),
 "korean-skincare-glass-skin": ("Korean Skincare and Glass Skin","Korean skincare made simple for Indian skin: glass skin routines adapted for heat, humidity and strong sun.",
   ["glass-skin-routine-for-indian-skin"]),
}

WPCATS["skincare-routines"] = ("Skincare Routines", "Simple skincare routines for Indian weather: winter, summer, monsoon, oily skin and busy working days, plus how to layer serums and creams.", [])
WPCATS["dark-spots-uneven-skin-tone"] = ("Dark Spots and Uneven Skin Tone", "Honest guides to dark spots, acne marks, pigmentation and uneven-looking skin tone: causes, routines, ingredients and realistic timelines.", [])
WPCATS["skincare-ingredients"] = ("Skincare Ingredients", "Plain-English guides to skincare ingredients: niacinamide, vitamin C, retinol, alpha arbutin, kojic acid and how to introduce actives safely.", [])
_TOPIC_CAT = {"avocado": "avocado-skincare", "glutathione": "glutathione-kojic-acid", "kojic": "glutathione-kojic-acid", "night": "night-cream-guides", "routine": "skincare-routines", "concern": "dark-spots-uneven-skin-tone", "ingredient": "skincare-ingredients"}
for _m in PLAN:
    if _m["kind"] == "post" and _m["slug"] not in UNPUBLISHED:
        WPCATS[_TOPIC_CAT[_m["topic"]]][2].insert(0, _m["slug"])

def build_wpcats():
    for slug,(name,desc,posts) in WPCATS.items():
        url=f"/category/{slug}/"; items=[POST_BY[x] for x in posts]
        crumbs=[("Home","/"),("Skincare guides","/blog/"),(name,url)]
        cp={"@type":"CollectionPage","@id":SITE+url,"url":SITE+url,"name":name,"description":desc,"isPartOf":{"@id":SITE+"/#website"}}
        robots = "index, follow, max-image-preview:large, max-snippet:-1" if len(items) > 1 else "noindex, follow"
        out=head(f"{name} %s Skincare Guides | Mirc Glow" % "-", desc, url, robots=robots, extra=ld(ORG,cp,crumbs_ld(crumbs)))
        out+=header("/blog/")
        out+=f'<main id="main">{crumbs_html(crumbs)}<div class="w ptop"><span class="eyebrow">Skincare guides</span><h1 class="dsp">{esc(name)}</h1><p>{esc(desc)}</p>{qbox(f"Mirc Glow has {len(items)} guides on {name.lower()}, written in plain English by founder Mohammed Nihal and reviewed for Indian skin and weather. Start with: " + "; ".join(p["title"] for p in items[:3]) + ".", label="In short") if items else ""}</div><section class="w" style="padding-bottom:40px"><div class="posts">{"".join(post_card(p) for p in items)}</div></section></main>'
        out+=footer()
        write(url,out)

def build_checkout():
    """/checkout/ (cart, address, Pay online or Cash on Delivery) and /order-success/. Both noindex."""
    hj = hashlib.sha1(read(os.path.join(ROOT, "src", "checkout.js")).encode()).hexdigest()[:8]
    shutil.copy(os.path.join(ROOT, "src", "checkout.js"), os.path.join(DIST, "assets", f"checkout.{hj}.js"))
    def img(p):
        w = p["img"][:-4] + ".mg.webp"
        return w if p["img"].endswith(".png") and os.path.exists(os.path.join(ROOT, w.lstrip("/"))) else p["img"]
    data = {"wa": WA_NUM, "prepaidPct": PREPAID_PCT, "coupons": COUPONS,
            "products": {p["slug"]: {"name": p["name"], "size": p["size"], "price": p["price"], "img": img(p), "u": f'/product/{p["slug"]}/'} for p in PRODUCTS}}
    robots = "noindex, nofollow"
    out = head("Checkout | Mirc Glow", "Your Mirc Glow cart: pay online with UPI or card, or choose Cash on Delivery. Free shipping across India.", "/checkout/", robots=robots)
    out += header("/shop/")
    out += f'''<main id="main" class="co"><div class="w">
<h1>Checkout</h1>
<div class="co-empty" data-co-empty hidden><p>Your cart is empty.</p><a class="yb yb-fill" style="width:auto;display:inline-flex" href="/shop/">Shop creams</a></div>
<form id="co-form" class="co-grid" data-co-main novalidate autocomplete="on">
<div>
<section class="co-card" aria-labelledby="h-cart"><h2 id="h-cart">Your cart</h2><div data-co-lines></div></section>
<section class="co-card" aria-labelledby="h-ship" style="margin-top:16px"><h2 id="h-ship">Delivery address</h2>
<div class="co-f">
<label>Full name<input name="name" autocomplete="name" required maxlength="80"></label>
<label>Mobile number <span class="hint">for delivery updates</span><input name="phone" type="tel" inputmode="numeric" autocomplete="tel-national" required maxlength="14" placeholder="10-digit mobile"></label>
<label>Pin code<input name="pin" inputmode="numeric" autocomplete="postal-code" required maxlength="6" placeholder="6 digits"><span class="hint" data-pin-note></span></label>
<label>House no., building, street, area<input name="address" autocomplete="street-address" required maxlength="220"></label>
<label>Landmark <span class="hint">optional</span><input name="landmark" maxlength="120"></label>
<div class="two"><label>City<input name="city" autocomplete="address-level2" required maxlength="60"></label><label>State<input name="state" autocomplete="address-level1" maxlength="60"></label></div>
<label>Email <span class="hint">optional, for the receipt</span><input name="email" type="email" autocomplete="email" maxlength="120"></label>
<label class="co-consent"><input type="checkbox" name="consent" value="1"><span>You may message me on WhatsApp about this order and related offers, even if I don't complete it.</span></label>
<label class="co-hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>
</div></section>
</div>
<div class="co-side">
<section class="co-card" aria-labelledby="h-pay"><h2 id="h-pay">Payment</h2>
<div class="co-pay">
<label class="co-opt" hidden><input type="radio" name="pay" value="online" disabled><span><b>Pay online</b><small data-pay-online-note></small></span></label>
<label class="co-opt" hidden><input type="radio" name="pay" value="cod" disabled><span><b>Cash on Delivery</b><small data-pay-cod-note></small></span></label>
<p class="co-msg" data-co-waonly hidden>Online checkout is being set up. Tap the button below to send this order on WhatsApp; we confirm it there.</p>
</div>
<div class="co-cp" style="margin-top:12px"><input id="co-cp" placeholder="Discount code" aria-label="Discount code" autocomplete="off"><button type="button" data-cp-apply>Apply</button></div>
<div class="co-sum" data-co-sum style="margin-top:14px"></div>
<button type="submit" class="yb yb-fill co-go" data-co-go>Place order</button>
<p class="co-msg" data-co-msg role="alert"></p>
<a class="yb yb-wa2" data-co-wa href="https://wa.me/{WA_NUM}" target="_blank" rel="noopener">{WA_SVG}<span>Or send this order on WhatsApp</span></a>
<p class="co-safe">🔒 Payments are processed by Razorpay; we never see your card or UPI PIN. Free shipping, usually 3–7 days. <a href="/returns-refunds/">7-day returns</a> on sealed jars. By ordering you agree to our <a href="/terms/">terms</a>.</p>
</section>
</div>
</form>
</div></main>
<script type="application/json" id="co-data">{json.dumps(data, ensure_ascii=False).replace("</", "<\\/")}</script>
<script src="/assets/checkout.{hj}.js" defer></script>'''
    out += footer(bar=False)
    write("/checkout/", out)

    out = head("Thank you for your order | Mirc Glow", "Your Mirc Glow order is placed. We pack it in Bhatkal, Karnataka, and deliver free across India, usually in 3 to 7 days, with tracking on WhatsApp.", "/order-success/", robots=robots)
    out += header("/shop/")
    out += f'''<main id="main" class="co"><div class="w co-done" id="done">
<div class="tick" aria-hidden="true">✓</div><h1>Thank you! Your order is placed.</h1>
<p>We pack orders from Bhatkal, Karnataka, usually within a day. Delivery is free and usually takes 3–7 days.</p>
<div data-done></div>
<p><a class="yb yb-fill" style="width:auto;display:inline-flex" href="/shop/">Continue shopping</a></p>
<p class="co-safe">Questions about your order? <a href="https://wa.me/{WA_NUM}" target="_blank" rel="noopener">WhatsApp us</a> with your order number. You can also <a href="/track-order/">track your order</a>.</p>
</div></main>
<script>(function(){{var o;try{{o=JSON.parse(sessionStorage.getItem("mg_last_order")||"null")}}catch(e){{}}if(!o)return;
var e=function(s){{return String(s).replace(/[&<>"]/g,function(c){{return{{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]}})}},r=function(n){{return"₹"+Math.round(n).toLocaleString("en-IN")}};
var h='<div class="co-card"><p><b>Order number:</b> '+e(o.ref)+'</p><p><b>Payment:</b> '+(o.pay==="online"?"Paid online"+(o.amount?" · "+r(o.amount):""):"Cash on Delivery · pay "+r(o.total)+" when it arrives")+'</p>'+
'<ul>'+o.items.map(function(i){{return"<li>"+i.q+" × "+e(i.n)+"</li>"}}).join("")+'</ul><p><b>Delivering to:</b> '+e(o.name)+', '+e(o.city)+' '+e(o.pin)+'</p>'+
(o.awb?'<p><b>Courier:</b> Delhivery · <a target="_blank" rel="noopener" data-track>track '+e(o.awb)+'</a></p>':'<p>We will WhatsApp you the tracking number once it is shipped.</p>')+'</div>';
document.querySelector("[data-done]").innerHTML=h;var t=document.querySelector("[data-track]");if(t&&/^https:\\/\\/www\\.delhivery\\.com\\//.test(o.trackUrl))t.setAttribute("href",o.trackUrl);}})();</script>'''
    out += footer(bar=False)
    write("/order-success/", out)

def build_404():
    out = head("Page not found | Mirc Glow", "This page could not be found. Browse Mirc Glow avocado night creams, glutathione cream and skincare guides instead.", "/404.html", robots="noindex, follow")
    out += header()
    out += f'''<main id="main" class="err"><div class="w" style="display:grid;gap:22px;justify-items:center;padding-block:80px"><span class="lab">404</span><h1 class="dsp" style="font-size:clamp(2.6rem,6vw,4.4rem)">This page has <em>moved</em>.</h1><p style="color:var(--muted);max-width:46ch">The link may be old. Try the shop, the journal, or ask us on WhatsApp and we will point you to the right cream.</p><div class="row" style="justify-content:center"><a class="btn dark" href="/shop/">Shop creams</a><a class="btn line" href="/blog/">Read the journal</a></div></div></main>'''
    out += footer()
    with open(os.path.join(DIST, "404.html"), "w", encoding="utf-8") as f: f.write(out)

# ---------------------------------------------------------------- machine-readable files
def indexable_urls():
    u = [("/", "1.0", TODAY), ("/shop/", "0.9", TODAY), ("/blog/", "0.7", TODAY)]
    u += [(cat_url(c), "0.8", TODAY) for c in CATS]
    u += [(f"/product/{p['slug']}/", "0.9", TODAY) for p in PRODUCTS]
    u += [(f"/{g['slug']}/", "0.6", TODAY) for g in PAGES]
    u += [(f"/{p['slug']}/", "0.7", TODAY) for p in LIVE_POSTS]
    u += [(f"/category/{c}/", "0.4", TODAY) for c,v in WPCATS.items() if len(v[2]) > 1]
    return u

def build_sitemaps():
    alt_map = {f"/{g['slug']}/": g for g in PAGES if g["alt"]}
    items = []
    for u, pr, lm in indexable_urls():
        x = f"<url><loc>{SITE}{u}</loc><lastmod>{lm}</lastmod><priority>{pr}</priority>"
        if u in alt_map:
            g = alt_map[u]; en, hi = (g["slug"], g["alt"]) if g["lang"] == "en" else (g["alt"], g["slug"])
            x += f'<xhtml:link rel="alternate" hreflang="en-IN" href="{SITE}/{en}/"/><xhtml:link rel="alternate" hreflang="hi-IN" href="{SITE}/{hi}/"/><xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/{en}/"/>'
        prod = next((p for p in PRODUCTS if u == f"/product/{p['slug']}/"), None)
        if prod: x += f"<image:image><image:loc>{SITE}{prod['img']}</image:loc></image:image>"
        if u in VIDEO_ON:
            V = VIDEO_BY_URL[u]; secs = int(re.sub(r"\D", "", V.get("dur", "PT30S")) or 30)
            x += (f"<video:video><video:thumbnail_loc>{SITE}{V['thumb']}</video:thumbnail_loc><video:title>{esc(V['name'])}</video:title>"
                  f"<video:description>{esc(V['description'])}</video:description><video:content_loc>{SITE}{V['src']}</video:content_loc>"
                  f"<video:duration>{secs}</video:duration><video:publication_date>{V['date']}</video:publication_date></video:video>")
        items.append(x + "</url>")
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n'
          + "\n".join(items) + "\n</urlset>\n")
    write("/sitemap.xml", sm)
    write("/sitemap_index.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>{SITE}/sitemap.xml</loc><lastmod>{TODAY}</lastmod></sitemap></sitemapindex>\n')

def build_robots():
    bots = ["GPTBot","OAI-SearchBot","ChatGPT-User","ClaudeBot","Claude-SearchBot","Claude-User","PerplexityBot","Perplexity-User","Google-Extended","Applebot","Applebot-Extended","Bingbot","CCBot","meta-externalagent","Amazonbot","DuckAssistBot"]
    txt = "# Mirc Glow — search engines and AI assistants are welcome.\nUser-agent: *\nAllow: /\n\n"
    txt += "\n".join(f"User-agent: {b}\nAllow: /\n" for b in bots)
    txt += f"\nSitemap: {SITE}/sitemap.xml\nSitemap: {SITE}/sitemap_index.xml\n"
    write("/robots.txt", txt)

DESK_IDS = {"avocado-korean-night-cream":"mg1","glutathione-cream":"mg2","avocado-night-cream":"mg3","avocado-face-cream":"mg4",
             "day-and-night-cream-combo":"mg5","night-cream-combo":"mg6","korean-glass-skin-kit":"mg7",
             "avocado-glow-cream-15g":"mg8","glass-glow-cream":"mg9","glass-glow-night-duo":"mg10"}
PREPAID_PCT = 5   # % off when paying online (shown at checkout; server uses api/_catalog.json)
COUPONS = {"GLOW10": 10}   # first-order code already promised on product pages (10% off)

def build_checkout_catalog():
    """Writes api/_catalog.json: the prices the payment server charges. Generated from PRODUCTS so it can never drift."""
    cat = {"prepaidPct": PREPAID_PCT, "coupons": COUPONS, "products": {}}
    for p in PRODUCTS:
        jars = len(p.get("parts") or []) or 1
        cat["products"][p["slug"]] = {"name": f'Mirc Glow {p["name"]}' + ("" if p["size"] in p["name"] else f' {p["size"]}'.replace(" g", "g").replace("g + ", "g + ")),
                                      "price": p["price"], "jars": jars, "desk": DESK_IDS.get(p["slug"], "")}
    txt = json.dumps(cat, ensure_ascii=False, indent=1)
    path = os.path.join(ROOT, "api", "_catalog.json")
    if not os.path.exists(path) or open(path, encoding="utf-8").read() != txt:
        open(path, "w", encoding="utf-8").write(txt)
    return cat

def build_merchant_feed():
    """Google Merchant Center product feed (free listings / Shopping): /google-merchant-feed.xml. Prices are the real selling prices only."""
    def x(t): return html.escape(re.sub(r"\s+", " ", strip_tags(str(t))).strip(), quote=False)
    items = []
    for p in PRODUCTS:
        url = f"{SITE}/product/{p['slug']}/"
        try: extra = re.findall(r'<img[^>]*src="(/wp-content/[^"]+)"', read(os.path.join(SRC, "products", p["slug"] + ".html")))
        except Exception: extra = []
        extra = [e for e in dict.fromkeys(extra) if e != p["img"]][:4]
        desc = f"{strip_tags(p['lead'])} Size: {p['size']}. Key ingredients: {', '.join(p['ing'])}. How to use: {strip_tags(p['use'])}. Patch test before first use."
        it = [f"<g:id>MG-{p['id']}</g:id>", f"<title>{x(p['h1']).replace('MircGlow', 'Mirc Glow')}</title>", f"<description>{x(desc)[:4900]}</description>",
              f"<link>{url}</link>", f"<g:image_link>{SITE}{p['img']}</g:image_link>"]
        it += [f"<g:additional_image_link>{SITE}{e}</g:additional_image_link>" for e in extra]
        it += ["<g:availability>in_stock</g:availability>", f"<g:price>{p['price']:.2f} INR</g:price>", f"<g:brand>{x(BRAND)}</g:brand>",
               "<g:condition>new</g:condition>", "<g:identifier_exists>no</g:identifier_exists>", f"<g:mpn>MG-{p['id']}</g:mpn>",
               "<g:google_product_category>Health &amp; Beauty &gt; Personal Care &gt; Cosmetics &gt; Skin Care &gt; Lotion &amp; Moisturizer</g:google_product_category>",
               f"<g:product_type>Skin care &gt; {'Sets and combos' if 'parts' in p else 'Face creams'}</g:product_type>",
               "<g:shipping><g:country>IN</g:country><g:price>0.00 INR</g:price><g:min_handling_time>0</g:min_handling_time><g:max_handling_time>2</g:max_handling_time><g:min_transit_time>3</g:min_transit_time><g:max_transit_time>7</g:max_transit_time></g:shipping>"]
        if "parts" in p: it.append("<g:is_bundle>yes</g:is_bundle>")
        else: it.append(f"<g:unit_pricing_measure>{p['grams']}g</g:unit_pricing_measure>")
        items.append("<item>" + "".join(it) + "</item>")
    feed = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0"><channel>'
            f"<title>{x(BRAND)} products</title><link>{SITE}/</link><description>{x(BRAND)} skincare products sold on mircglow.com</description>"
            + "".join(items) + "</channel></rss>\n")
    write("/google-merchant-feed.xml", feed)

def build_llms():
    L = [f"# {BRAND}", "",
         "> Korean-inspired skincare brand from Bhatkal, Karnataka, India. Six creams and four sets built around avocado, glutathione and kojic acid. The four original creams contain aloe vera, vitamin B3 and kojic acid; Avocado Glow Cream 15g is avocado and aloe vera only; Glass Glow Cream 30g has glutathione, niacinamide, hyaluronic acid, centella asiatica and alpha arbutin. Sold directly across India with free shipping, Cash on Delivery and 7-day returns on sealed jars. Orders are placed on WhatsApp (+91 99808 81230).", "",
         "Important: Mirc Glow creams are cosmetics. They help skin feel softer and look smoother and more even. They do not change natural skin tone and are not intended to treat skin conditions. They are Korean-inspired; manufacturing details are printed on each pack.", "",
         "## Products (prices in INR, October 2026)"]
    for p in PRODUCTS:
        L.append(f"- [{p['name']} ({p['size']})]({SITE}/product/{p['slug']}/): ₹{p['price']} (MRP ₹{p['mrp']}). {p['lead']} Best for: {p['best']}. Use: {p['use']}.")
    L += ["", "## Buying and policies",
          f"- [How to order]({SITE}/shop/): tap Order on a product, send the prefilled WhatsApp message with your address; pay by Cash on Delivery or an online link.",
          f"- [Shipping policy]({SITE}/shipping-policy/): free shipping across India, usually 3 to 7 days.",
          f"- [Returns and refunds]({SITE}/returns-refunds/): unopened sealed jars within 7 days of delivery; damaged, wrong or expired items replaced or refunded.",
          f"- [Track your order]({SITE}/track-order/)", f"- [Contact]({SITE}/contact/): WhatsApp or phone {PHONE}; Azad Nagar 4th Cross, Bhatkal, Karnataka 581320.",
          f"- [Bulk night cream in kg]({SITE}/bulk-night-cream/): wholesale supply for salons, resellers and brands.",
          f"- [Avocado cream in kg]({SITE}/avocado-cream-in-kg/): avocado cream and avocado night cream by the kilo (from 1 kg) for salons, parlours and resellers; price per kg on WhatsApp +91 99808 81230.",
          "", "## Buying guides and tools",
          f"- [Avocado cream guide]({SITE}/avocado-cream/) (Hindi: {SITE}/avocado-cream-hindi/)",
          f"- [Korean night cream guide]({SITE}/korean-night-cream/) (Hindi: {SITE}/korean-night-cream-hindi/)",
          f"- [Skin quiz]({SITE}/skin-quiz/)", f"- [Skincare routine builder]({SITE}/skincare-routine-builder/)", f"- [Skincare ingredient glossary]({SITE}/skincare-ingredient-glossary/)",
          f"- [Our ingredients]({SITE}/ingredients/)", f"- [FAQ]({SITE}/faq/)", f"- [About Mirc Glow]({SITE}/about/)",
          "", "## Skincare guides"]
    for p in LIVE_POSTS:
        q = GEO.QUICK.get(p["slug"])
        L.append(f"- [{p['title']}]({SITE}/{p['slug']}/): " + (q[0] if q else p['ex']))
    L += ["", "## Shop by category"] + [f"- [{d['name']}]({SITE}{cat_url(c)})" for c, d in CATS.items()] + [f"- [Gift sets]({SITE}/skincare-gift-sets/)"]
    L += ["", "## Hindi guides (हिंदी)"] + [f"- [{g['title']}]({SITE}/{g['slug']}/)" for g in PAGES if g["lang"] == "hi"]
    if any(g["lang"] in LANG_NAME for g in PAGES):
        L += ["", "## Tamil, Telugu, Marathi and Bengali guides"] + [f"- [{g['title']}]({SITE}/{g['slug']}/) ({LANG_NAME[g['lang']]})" for g in PAGES if g["lang"] in LANG_NAME]
    L += ["", "## Bulk and wholesale supply (cream by the kg)"] + [f"- [{g['title']}]({SITE}/{g['slug']}/)" + (f": {PAGE_QUICK[g['slug']][0]}" if g['slug'] in PAGE_QUICK else "") for g in PAGES if g["slug"] in CITY]
    L += ["", "## Guide categories"] + [f"- [{v[0]}]({SITE}/category/{c}/)" for c, v in WPCATS.items() if len(v[2]) > 1] + [f"- [All skincare guides]({SITE}/blog/)"]
    L += ["", "## Brand facts"] + [f"- {k}: {v}" for k, v in GEO.AT_A_GLANCE]
    L += ["", "## About the content", f"- [About the author]({SITE}/about-the-author/): guides are written by founder Mohammed Nihal.",
          f"- [Editorial policy]({SITE}/editorial-policy/): how guides are fact-checked and updated; no medical or skin-colour claims.", f"- [Privacy policy]({SITE}/privacy/)", f"- [Terms]({SITE}/terms/)", f"- [Full answers file: every page's short answer and FAQs]({SITE}/llms-full.txt)"]
    L += ["", "## Common questions"] + [f"- {q} {a}" for k in ("shipping-policy", "returns-refunds") for q, a in GEO.PAGE_ANSWERS[k]]
    write("/llms.txt", "\n".join(L) + "\n")

def build_feed():
    items = ""
    for p in sorted(LIVE_POSTS, key=lambda x: x["date"], reverse=True):
        y, m, d = map(int, p["date"].split("-"))
        dt = date(y, m, d).strftime("%a, %d %b %Y") + " 09:00:00 +0530"
        items += f"<item><title>{esc(p['title'])}</title><link>{SITE}/{p['slug']}/</link><guid>{SITE}/{p['slug']}/</guid><pubDate>{dt}</pubDate><description>{esc(p['ex'])}</description></item>"
    write("/feed.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{BRAND} Journal</title><link>{SITE}/blog/</link><description>Skincare guides from Mirc Glow</description><language>en-in</language>{items}</channel></rss>\n')

def build_vercel():
    R = lambda s, d: {"source": s, "destination": d, "permanent": True}
    redirects = [
        R("/product/mirc-glow-avocado-korean-night-cream-with-aloe-vera-vitamin-b3-kojic-acid-glutathione-inspired-brightening-night-cream-for-women-men-30-g/", "/product/avocado-korean-night-cream/"),
        R("/product/glutathione-kojic-acid-cream/", "/product/avocado-korean-night-cream/"),
        R("/product/luminous-barrier-cream/", "/product/glutathione-cream/"),
        R("/product/radiance-renewal-serum/", "/product/avocado-night-cream/"),
        R("/product/glow-clarifying-cleanser/", "/product/avocado-face-cream/"),
        R("/is-avocado-face-cream-good-for-glowing-skinis-avocado-cream-good-for-your-skin/", "/is-avocado-cream-good-for-your-skin/"),
        R("/cart(.*)", "/checkout/"), R("/my-account(.*)", "/track-order/"),
        R("/product-category/uncategorized/", "/shop/"), R("/category/uncategorized/", "/blog/"), R("/category/skincare-guides/", "/blog/"),
        R("/product-tag/(.*)", "/shop/"), R("/tag/(.*)", "/blog/"), R("/author/(.*)", "/about-the-author/"),
        R("/comments/feed(.*)", "/blog/"), R("/category/skincare-guides/(.*)", "/blog/"), R("/category/uncategorized/(.*)", "/blog/"), R("/category/:cat/page/(.*)", "/category/:cat/"), R("/product/:slug/feed(.*)", "/product/:slug/"), R("/:slug/feed(.*)", "/:slug/"), R("/home/", "/"), R("/sample-page/", "/"), R("/blog/page/(.*)", "/blog/"), R("/page/(.*)", "/blog/"), R("/shop/page/(.*)", "/shop/"),
        R("/post-sitemap.xml", "/sitemap.xml"), R("/page-sitemap.xml", "/sitemap.xml"), R("/product-sitemap.xml", "/sitemap.xml"),
        R("/product_cat-sitemap.xml", "/sitemap.xml"), R("/category-sitemap.xml", "/sitemap.xml"), R("/local-sitemap.xml", "/sitemap.xml"),
        R("/wp-sitemap.xml", "/sitemap.xml"),
        R("/feed/(.+)", "/feed/"), R("/comments/feed/", "/feed/"),
    ]
    sec = [{"key":"X-Content-Type-Options","value":"nosniff"},{"key":"Referrer-Policy","value":"strict-origin-when-cross-origin"},
           {"key":"X-Frame-Options","value":"SAMEORIGIN"},{"key":"Permissions-Policy","value":"camera=(), microphone=(), geolocation=()"},
           {"key":"Strict-Transport-Security","value":"max-age=63072000; includeSubDomains; preload"}]
    cfg = {"$schema":"https://openapi.vercel.sh/vercel.json","cleanUrls":False,"trailingSlash":True,"redirects":redirects,
           "rewrites":[{"source":"/feed/","destination":"/feed.xml"}],
           "headers":[{"source":"/(.*)","headers":sec},
                      {"source":"/assets/(.*)","headers":[{"key":"Cache-Control","value":"public, max-age=31536000, immutable"}]},
                      {"source":"/wp-content/uploads/(.*)","headers":[{"key":"Cache-Control","value":"public, max-age=2592000, stale-while-revalidate=86400"}]},
                      {"source":"/feed.xml","headers":[{"key":"Content-Type","value":"application/rss+xml; charset=utf-8"}]},
                      {"source":"/llms.txt","headers":[{"key":"Content-Type","value":"text/plain; charset=utf-8"}]},
                      {"source":"/llms-full.txt","headers":[{"key":"Content-Type","value":"text/plain; charset=utf-8"}]}]}
    with open(os.path.join(DIST, "vercel.json"), "w") as f: json.dump(cfg, f, indent=2)
    # project settings for Vercel (repo root). Vercel runs build.py itself on every deploy (falls back to the committed dist/ if it fails),
    # and Vercel Cron calls /api/publish every morning so scheduled pages go live on their date without any GitHub activity.
    root_cfg = {"$schema": cfg["$schema"], "framework": None,
                "installCommand": "python3 -m pip install --quiet --user pillow || echo 'pillow not installed; images keep working'",
                "buildCommand": "python3 build.py || echo 'build.py failed; using the committed dist folder'",
                "outputDirectory": "dist", "crons": [{"path": "/api/publish", "schedule": "35 0 * * *"}],
                **{k: v for k, v in cfg.items() if k != "$schema"}}
    with open(os.path.join(ROOT, "vercel.json"), "w") as f: json.dump(root_cfg, f, indent=2)

def build_assets():
    with open(os.path.join(DIST, "74d314fcd13a092ae512fe4c12566f9f.txt"), "w") as f: f.write("74d314fcd13a092ae512fe4c12566f9f")  # IndexNow key
    up = os.path.join(ROOT, "wp-content")
    if os.path.isdir(up): shutil.copytree(up, os.path.join(DIST, "wp-content"))
    global CSS_HREF, JS_HREF
    css = read(os.path.join(ROOT, "src", "site.css"))
    css += "\n.sr{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}\n"
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S); css = re.sub(r"\s*\n\s*", "\n", css).strip()
    h = hashlib.sha1(css.encode()).hexdigest()[:8]
    os.makedirs(os.path.join(DIST, "assets"), exist_ok=True)
    with open(os.path.join(DIST, "assets", f"site.{h}.css"), "w") as f: f.write(css)
    CSS_HREF = f"/assets/site.{h}.css"
    js = read(os.path.join(ROOT, "src", "site.js")); hj = hashlib.sha1(js.encode()).hexdigest()[:8]
    with open(os.path.join(DIST, "assets", f"site.{hj}.js"), "w") as f: f.write(js)
    JS_HREF = f"/assets/site.{hj}.js"
    icon = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#9C5468"/>'
            '<circle cx="32" cy="32" r="28.5" fill="none" stroke="#B87487" stroke-width="1"/>'
            '<text x="32" y="45.5" text-anchor="middle" font-family="Georgia,\'Times New Roman\',serif" font-weight="700" font-size="40" fill="#FFF7F8">M</text></svg>')
    with open(os.path.join(DIST, "assets", "icon.svg"), "w") as f: f.write(icon)
    # site icon for Google results and browsers: bold "M", served from the site root (favicon.ico + PNG sizes)
    for fn in os.listdir(os.path.join(ROOT, "src", "icons")):
        if fn.startswith(("favicon", "apple-touch-icon")): shutil.copy(os.path.join(ROOT, "src", "icons", fn), os.path.join(DIST, fn))
    src_logo = os.path.join(ROOT, "src", "logo.png")
    if os.path.exists(src_logo): shutil.copy(src_logo, os.path.join(DIST, "assets", "logo.png"))
    shutil.copy(os.path.join(ROOT, "DEPLOY.md"), os.path.join(DIST, "DEPLOY.md"))
    with open(os.path.join(DIST, ".vercelignore"), "w") as f: f.write("DEPLOY.md\n")

def main():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    build_assets()
    build_home(); build_shop(); build_blog(); build_wpcats()
    for p in PRODUCTS: build_product(p)
    for p in POSTS: build_post(p)
    for g in PAGES: build_page(g)
    build_404(); build_sitemaps(); build_robots(); build_llms(); build_feed(); build_vercel(); build_llms_full(); build_merchant_feed(); build_checkout_catalog(); build_checkout()
    n = sum(len(fs) for _, _, fs in os.walk(DIST))
    print(f"built {n} files into dist/")

if __name__ == "__main__":
    main()
