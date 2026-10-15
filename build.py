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
TODAY = "2026-10-14"
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
      lead="Our Korean-inspired avocado night cream in a 25 g jar, with aloe vera, vitamin B3 and kojic acid.",
      pts=["Leaves skin feeling hydrated and smooth by morning","The last step of a simple glass-skin night routine","A pea-sized amount is enough each night"]),
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
      lead="A glutathione night cream with vitamin C and kojic acid, plus aloe vera and vitamin B3, in a 30 g jar.",
      pts=["For skin that looks dull or uneven","Three glow-focused ingredients in one cream","Use at night, with sunscreen every morning"]),
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
      lead="A rich avocado night cream with aloe vera, vitamin B3 and kojic acid. Korean-inspired care for skin that feels soft and comfortable by morning.",
      pts=["Nourishes dry, tired-feeling skin while you sleep","Kojic acid and vitamin B3 for a more even-looking glow","A pea-sized amount is enough each night"]),
 dict(id=22, slug="avocado-face-cream", name="Avocado Glow Cream", size="10 g", grams=10,
      h1="Avocado Glow Nourishing Skin Cream – 10g",
      price=349, mrp=449, img=UP+"2DFA2551-B14E-43F6-8929-E39538EC9628-1.png", jars=["Avocado Day"],
      ko="글로우 크림", tag="Try me", topic="avocado", when="Day or night",
      meta="A light first step", best="First-time buyers, travel, and daytime under sunscreen",
      bg="linear-gradient(160deg,#F8FCFA,#DDECE4)", cats=["night-creams","avocado-night-creams"],
      ing=["Avocado","Aloe vera","Vitamin B3 (niacinamide)","Kojic acid"], lasts="About 2 to 3 weeks of daily use",
      skin="All skin types; very little for oily skin", use="Morning under sunscreen, or at night",
      rt="Avocado Face Cream 10g: Best Gentle Daily Moisturiser | Mirc Glow",
      rd="Buy Mirc Glow Avocado Face Cream 10g online in India. A nourishing avocado moisturiser for soft, smooth, radiant-looking skin. Cash on Delivery available.",
      lead="A light daily avocado cream with aloe vera, vitamin B3 and kojic acid, in a 10 g jar.",
      pts=["Soft, comfortable skin without a heavy feel","Small jar that is easy to carry","The easiest way to try Mirc Glow for the first time"]),
 dict(id=262, slug="day-and-night-cream-combo", name="Day & Night Combo", size="10 g + 30 g", grams=40,
      h1="Day and Night Cream Combo – Mirc Glow Avocado Glow 10g + Avocado Night Cream 30g",
      price=849, mrp=998, img=UP+"04BCBF62-EE16-4594-B65C-BDA805C264CB-1.png", jars=["Day","Night"],
      ko="데이 & 나이트", tag="Set", topic="avocado", when="Morning and night",
      meta="Avocado Glow 10 g and Avocado Night Cream 30 g", best="A complete, simple moisturising routine",
      bg="linear-gradient(150deg,#FFF6F1,#FBE3D8)", cats=["combos"],
      ing=["Avocado","Aloe vera","Vitamin B3 (niacinamide)","Kojic acid"], lasts="Day cream about 2 to 3 weeks; night cream about 4 to 6 weeks",
      skin="Dry, normal and combination skin", use="Day cream in the morning, night cream in the evening",
      rt="Day and Night Cream Combo: 2 Best Avocado Creams, 1 Routine | Mirc Glow",
      rd="Buy the Mirc Glow day and night cream combo online in India: Avocado Glow 10g for the day and Avocado Night Cream 30g for the night. Free shipping and COD.",
      lead="Two avocado creams: the light Avocado Glow Nourishing Skin Cream for the morning and the rich Avocado Night Cream with Kojic Acid for the evening.",
      pts=["Avocado Glow Nourishing Skin Cream, 10 g (day)","Avocado Night Cream with Kojic Acid, 30 g (night)","Costs less than buying the two jars separately"],
      parts=["avocado-face-cream","avocado-night-cream"]),
 dict(id=263, slug="night-cream-combo", name="Night Cream Combo", size="30 g + 30 g", grams=60,
      h1="Night Cream Combo – Mirc Glow Glutathione Cream 30g + Avocado Night Cream 30g",
      price=1799, mrp=2148, img=UP+"5D782746-D1F2-496B-8449-5B8149C43004-1.png", jars=["Glutathione","Avocado"],
      ko="나이트 듀오", tag="Set", topic="glutathione", when="Night (alternate or layer)",
      meta="Glutathione Cream and Avocado Night Cream", best="Radiance and deep nourishment in one evening routine",
      bg="linear-gradient(150deg,#FBF4FF,#EADFF3)", cats=["combos"],
      ing=["Glutathione","Vitamin C","Avocado","Kojic acid","Aloe vera","Vitamin B3 (niacinamide)"], lasts="About two months when you alternate the jars",
      skin="Dull, dry or uneven-looking skin", use="Alternate nights at first, then layer",
      rt="Night Cream Combo: 2 Best Creams for Glow and Soft Skin | Mirc Glow",
      rd="Buy the Mirc Glow night cream combo online in India: Glutathione Cream 30g plus Avocado Night Cream 30g for radiant-looking, nourished skin. Free shipping and COD.",
      lead="Our Glutathione Cream with vitamin C and kojic acid, paired with the rich Avocado Night Cream. Radiance-focused care and deep nourishment for your evenings.",
      pts=["Glutathione Cream with Vitamin C and Kojic Acid, 30 g","Avocado Night Cream with Kojic Acid, 30 g","Costs less than buying the two jars separately"],
      parts=["glutathione-cream","avocado-night-cream"]),
 dict(id=264, slug="korean-glass-skin-kit", name="Korean Glass Skin Kit", size="30 g + 25 g + 10 g", grams=65,
      h1="Korean Glass Skin Kit – 3 Mirc Glow Korean-Inspired Creams",
      price=1999, mrp=2497, img=UP+"4ED0DC3B-11FA-4903-87CC-21E1887C89E5.png", jars=["Glow","Night","Day"],
      ko="유리 피부 키트", tag="Full ritual", topic="routine", when="Morning and night",
      meta="Three creams for a complete routine", best="Beginners who want the full morning and night routine",
      bg="linear-gradient(150deg,#FFF5F7,#F3D3DB)", cats=["combos"],
      ing=["Glutathione","Vitamin C","Avocado","Kojic acid","Aloe vera","Vitamin B3 (niacinamide)"], lasts="Night creams about two months together; day cream about 2 to 3 weeks",
      skin="All skin types; thin layers for oily skin", use="Day cream in the morning; night creams in the evening",
      rt="Korean Glass Skin Kit: 3 Best Creams for a Dewy Glow | Mirc Glow",
      rd="Buy the Mirc Glow Korean glass skin kit online in India: 3 Korean-inspired creams for a complete morning and night routine. Free shipping and Cash on Delivery.",
      lead="Three Korean-inspired creams: the Glutathione Cream for radiance, the Avocado Korean Night Cream for nourishment, and the Avocado Glow cream for the day.",
      pts=["Glutathione Cream, 30 g","Avocado Korean Night Cream, 25 g","Avocado Glow Nourishing Skin Cream, 10 g","Costs less than buying the three jars separately"],
      parts=["glutathione-cream","avocado-korean-night-cream","avocado-face-cream"]),
]
PBY = {p["slug"]: p for p in PRODUCTS}
SINGLES = [p for p in PRODUCTS if "parts" not in p]
SETS = [p for p in PRODUCTS if "parts" in p]
CATS = {
 "night-creams": dict(name="Night Creams", h1="Night creams", ko="나이트 크림 · NIGHT CREAMS", parent=None,
     rt="Night Creams: Avocado and Glutathione Night Cream | Mirc Glow",
     rd="Shop Mirc Glow night creams in India: avocado night creams and glutathione cream with aloe vera, vitamin B3 and kojic acid, from ₹349. Free shipping and COD.",
     intro="Korean-inspired creams for the last step of your evening routine. Each one contains aloe vera, vitamin B3 and kojic acid, and each has its own job."),
 "avocado-night-creams": dict(name="Avocado Night Creams", h1="Avocado night creams", ko="아보카도 · AVOCADO CARE", parent="night-creams",
     rt="Avocado Night Creams: Compare 3 Avocado Creams | Mirc Glow",
     rd="Shop Mirc Glow avocado night creams and avocado face cream in India, from ₹349. Avocado, aloe vera, vitamin B3 and kojic acid. Free shipping and Cash on Delivery.",
     intro="Rich, cushioned avocado creams for skin that feels dry or tight after washing. Pick by jar size and the time of day you want to use it."),
 "combos": dict(name="Combos and Kits", h1="Combos and kits", ko="세트 · SETS", parent=None,
     rt="Skincare Combos and Kits: Save on Mirc Glow Sets | Mirc Glow",
     rd="Mirc Glow combos and kits: day and night combo, night cream combo and Korean glass skin kit, from ₹849. Each set costs less than buying the creams separately.",
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
 P("how-to-apply-night-cream","How to Apply Night Cream the Right Way","Most people use too much night cream and apply it at the wrong moment. Here is how to apply night cream properly, in about a minute.","How to Apply Night Cream: 6 Easy Steps Most People Skip | Mirc Glow","Most people use too much and apply it at the wrong time. Learn how to apply night cream in 6 easy steps, how much to use, and what order to follow.",D4,"night"),
 P("avocado-cream-for-dry-skin","Avocado Cream for Dry Skin: Why It Works and How to Use It","Dry, tight skin after washing? Here is why avocado cream for dry skin makes sense, how to apply it so it actually helps, and what to change in winter.","Avocado Cream for Dry Skin: 5 Simple Ways to Use It | Mirc Glow","Dry, tight skin after washing? See why avocado cream for dry skin makes sense, 5 simple ways to use it so it really helps, and what to change in winter.",D4,"avocado"),
 P("night-cream-for-men","Night Cream for Men: A Simple Guide to Getting Started","A no-fuss guide to night cream for men: why it helps, how to choose one, and a two-minute evening routine.","Night Cream for Men: 5 Easy Steps to Better-Looking Skin | Mirc Glow","A no-fuss guide to night cream for men in India: why it helps, how to choose one, and 5 easy steps for a two-minute evening routine.",D4,"night"),
 P("night-cream-for-oily-skin","Night Cream for Oily Skin: How to Choose and Use One","Yes, oily skin needs a night cream. Learn how to choose a night cream for oily skin, how much to use, and the mistakes that cause shine and breakouts.","Night Cream for Oily Skin: 6 Simple Rules That Work | Mirc Glow","Does oily skin need a night cream? Yes. Learn 6 simple rules for choosing and using a night cream for oily skin without shine, heaviness or breakouts.",D4,"night"),
 P("best-night-cream-for-glowing-skin","Best Night Cream for Glowing Skin in India: How to Choose","How to find the best night cream for glowing skin in India: the ingredients to look for, how to choose by skin type, and our three picks.","Best Night Cream for Glowing Skin in India: 7 Things to Check | Mirc Glow","Looking for the best night cream for glowing skin in India? Learn the 7 things to check, the ingredients that matter, and how to choose by skin type.",D3,"night"),
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
 P("is-avocado-night-cream-good","Is Avocado Night Cream Good?","Learn how avocado night cream can support a comfortable, moisturized-looking complexion and how to choose a formula for your evening routine.","Is Avocado Night Cream Good? | Mirc Glow","Is avocado night cream good for your skincare routine? Learn about its potential benefits, how to use it, and what to consider when choosing a formula.",D2,"avocado"),
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
}

# ---------------------------------------------------------------- pages
G = lambda slug, title, rt, rd, kind, crumb=None, img=None, lang="en", alt=None: dict(slug=slug, title=title, rt=rt, rd=rd, kind=kind, crumb=crumb or title, img=img, lang=lang, alt=alt)
PAGES = [
 G("avocado-cream","Avocado Cream","Avocado Cream: 3 Best Picks for Soft, Nourished Skin | Mirc Glow","Shop avocado cream by Mirc Glow in India. Compare 3 avocado creams with aloe vera, vitamin B3 and kojic acid, from ₹349, and find the right one for your skin.","legacy",img=UP+"04BCBF62-EE16-4594-B65C-BDA805C264CB.png",alt="avocado-cream-hindi"),
 G("korean-night-cream","Korean Night Cream","Korean Night Cream: 3 Best Picks for a Glass Skin Glow | Mirc Glow","Shop Korean night cream by Mirc Glow in India. Compare 3 Korean-inspired night creams with avocado, vitamin B3 and kojic acid, from ₹649, and learn how to use them.","legacy",img=UP+"4ED0DC3B-11FA-4903-87CC-21E1887C89E5.png",alt="korean-night-cream-hindi"),
 G("avocado-cream-hindi","एवोकाडो क्रीम (Avocado Cream in Hindi)","एवोकाडो क्रीम के फायदे और इस्तेमाल का तरीका | Mirc Glow","एवोकाडो क्रीम क्या है, चेहरे के लिए इसके फायदे क्या हैं और इसे कैसे लगाएं? आसान हिंदी में जानकारी, साथ में Mirc Glow की 3 एवोकाडो क्रीम की तुलना।","plain",crumb="एवोकाडो क्रीम",lang="hi",alt="avocado-cream",img=UP+"04BCBF62-EE16-4594-B65C-BDA805C264CB.png"),
 G("korean-night-cream-hindi","कोरियन नाइट क्रीम (Korean Night Cream in Hindi)","कोरियन नाइट क्रीम क्या है? फायदे और लगाने का सही तरीका | Mirc Glow","कोरियन नाइट क्रीम क्या होती है, इसके फायदे क्या हैं और इसे कैसे लगाएं? आसान हिंदी में पूरी जानकारी, साथ में Mirc Glow की 3 नाइट क्रीम की तुलना।","plain",crumb="कोरियन नाइट क्रीम",lang="hi",alt="korean-night-cream",img=UP+"4ED0DC3B-11FA-4903-87CC-21E1887C89E5.png"),
 G("skin-quiz","Skin Quiz","Skin Quiz: Find Your Best Cream in 4 Easy Questions | Mirc Glow","Take the Mirc Glow skin quiz. Answer 4 easy questions about your skin and get a cream recommendation with tips on how to use it.","legacy"),
 G("skincare-routine-builder","Skincare Routine Builder","Skincare Routine Builder: 5 Easy Korean-Style Routines | Mirc Glow","Use our skincare routine builder to get a simple morning and night routine for dry, oily, combination, normal or sensitive skin, Korean style.","legacy"),
 G("skincare-ingredient-glossary","Skincare Ingredient Glossary","Skincare Ingredient Glossary: 15 Essential K-Beauty Actives | Mirc Glow","A plain-English skincare ingredient glossary. Learn what PDRN, exosomes, tranexamic acid, niacinamide, kojic acid, glutathione and 9 more actually do.","legacy"),
 G("skincare-gift-sets","Diwali Skincare Gift Sets","Diwali Skincare Gift Sets: 3 Best Glow Kits from ₹849 | Mirc Glow","Looking for a Diwali skincare gift? Choose from 3 Mirc Glow gift sets from ₹849, with avocado night creams and glutathione cream. Free shipping and Cash on Delivery.","legacy",crumb="Gift sets",img=UP+"2DFA2551-B14E-43F6-8929-E39538EC9628-1.png"),
 G("bulk-night-cream","Bulk Night Cream in Kg","Night Cream in Kg: Bulk Avocado Night Cream Wholesale Supply | Mirc Glow","Buy night cream in kg from Mirc Glow. Avocado night cream in kg and glutathione cream wholesale for salons, resellers and brands in India. Get a quote on WhatsApp.","legacy",crumb="Bulk orders",img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"),
 G("night-cream-in-kg-mumbai","Night Cream in Kg in Mumbai","Night Cream in Kg in Mumbai: Wholesale Bulk Supply | Mirc Glow","Night cream in kg in Mumbai for salons, parlours and resellers. Avocado night cream wholesale by the kilo or in jars. Get the price per kg on WhatsApp.","legacy",crumb="Mumbai",img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"),
 G("night-cream-in-kg-delhi","Night Cream in Kg in Delhi","Night Cream in Kg in Delhi: Wholesale Bulk Supply | Mirc Glow","Night cream in kg in Delhi NCR for salons, parlours and resellers. Avocado night cream wholesale by the kilo or in jars. Ask for the price per kg.","legacy",crumb="Delhi",img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"),
 G("night-cream-in-kg-bangalore","Night Cream in Kg in Bangalore","Night Cream in Kg in Bangalore: Wholesale Bulk Supply | Mirc Glow","Night cream in kg in Bangalore from a Karnataka brand. Avocado night cream wholesale for salons, resellers and new brands. Ask for the price per kg.","legacy",crumb="Bangalore",img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"),
 G("night-cream-in-kg-hyderabad","Night Cream in Kg in Hyderabad","Night Cream in Kg in Hyderabad: Wholesale Bulk Supply | Mirc Glow","Night cream in kg in Hyderabad for salons, bridal studios and resellers. Avocado night cream wholesale by the kilo or in jars. Get the price per kg.","legacy",crumb="Hyderabad",img="/wp-content/uploads/2026/10/mirc-glow-bulk-night-cream-in-kg.webp"),
 G("about","About","About Mirc Glow | Korean-Inspired Skincare from Karnataka","Mirc Glow is a skincare brand from Bhatkal, Karnataka, making avocado and glutathione creams with aloe vera, vitamin B3 and kojic acid. Meet the brand.","legacy",crumb="About us"),
 G("ingredients","Ingredients","Our Ingredients: Glutathione, Kojic Acid and Avocado | Mirc Glow","The ingredients in Mirc Glow creams, glutathione, kojic acid, vitamin C, vitamin B3, avocado and aloe vera, and what each one does for how skin looks and feels.","legacy"),
 G("faq","FAQ","FAQ: Orders, Delivery, Returns and Using Our Creams | Mirc Glow","Answers to common questions about Mirc Glow: Cash on Delivery, free shipping, 7-day returns, which cream to choose and how to use it safely.","legacy"),
 G("contact","Contact","Contact Mirc Glow | WhatsApp +91 99808 81230","Contact Mirc Glow for order help, product advice or bulk orders. WhatsApp or call +91 99808 81230. Azad Nagar, Bhatkal, Karnataka.","legacy"),
 G("about-the-author","About the Author","About the Author: Mohammed Nihal, Founder | Mirc Glow","Mohammed Nihal runs Mirc Glow from Bhatkal, Karnataka, and writes our guides on night creams, avocado skincare, glutathione and kojic acid. How the guides are written.","plain",crumb="About the author"),
 G("editorial-policy","Editorial Policy","Editorial Policy: How We Write Our Skincare Guides | Mirc Glow","How Mirc Glow writes, fact-checks and updates its skincare guides, who writes them, and the claims we will never make about our creams.","plain"),
 G("track-order","Track Your Order","Track Your Order | Mirc Glow","Track your Mirc Glow order. Find your tracking number, check your delivery status, and get help on WhatsApp if your parcel is delayed.","plain"),
 G("shipping-policy","Shipping Policy","Shipping Policy | Mirc Glow","Mirc Glow offers free shipping across India with delivery in 3 to 7 days. Cash on Delivery and secure online payment are available.","plain"),
 G("returns-refunds","Returns and Refunds","Returns and Refunds Policy | Mirc Glow","Mirc Glow accepts returns of unopened, sealed jars within 7 days of delivery, and of damaged, wrong or expired items. Refunds are made in 5 to 7 working days.","plain"),
 G("privacy","Privacy Policy","Privacy Policy | Mirc Glow","How Mirc Glow collects, uses and protects your personal information when you visit mircglow.com or place an order.","plain"),
 G("terms","Terms and Conditions","Terms and Conditions | Mirc Glow","The terms that apply when you use mircglow.com or order from Mirc Glow, including pricing, payment, delivery and returns.","plain"),
]
CITY = {"night-cream-in-kg-mumbai","night-cream-in-kg-delhi","night-cream-in-kg-bangalore","night-cream-in-kg-hyderabad"}

# ---------------------------------------------------------------- helpers
def read(path):
    with open(path, encoding="utf-8") as f: return f.read()

def write(urlpath, content):
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
        return tag
    return re.sub(r"<img [^>]*>", rep, body)

def faqs_from(body):
    """Pull Q&A pairs from <details>, FAQ-style h3 lists, and 'Short answers' blocks."""
    out = []
    for q, a in re.findall(r"<details[^>]*>\s*<summary>(.*?)</summary>(.*?)</details>", body, flags=re.S):
        out.append((strip_tags(q), strip_tags(a)))
    for sec in re.finditer(r"<h2[^>]*>([^<]*(?:FAQ|[Qq]uestions|Short answers)[^<]*)</h2>(.*?)(?=<h2|\Z)", body, flags=re.S):
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

# ---------------------------------------------------------------- schema
ORG_ID = SITE + "/#organization"
RETURN_POLICY = {"@type":"MerchantReturnPolicy","applicableCountry":"IN","returnPolicyCategory":"https://schema.org/MerchantReturnFiniteReturnWindow","merchantReturnDays":7,"returnMethod":"https://schema.org/ReturnByMail","returnFees":"https://schema.org/FreeReturn","merchantReturnLink":SITE+"/returns-refunds/"}
SHIPPING = {"@type":"OfferShippingDetails","shippingRate":{"@type":"MonetaryAmount","value":0,"currency":"INR"},"shippingDestination":{"@type":"DefinedRegion","addressCountry":"IN"},
            "deliveryTime":{"@type":"ShippingDeliveryTime","handlingTime":{"@type":"QuantitativeValue","minValue":0,"maxValue":2,"unitCode":"DAY"},"transitTime":{"@type":"QuantitativeValue","minValue":3,"maxValue":7,"unitCode":"DAY"}}}
ORG = {"@type":"OnlineStore","@id":ORG_ID,"name":BRAND,"url":SITE+"/","logo":SITE+"/assets/logo.png",
       "description":"Korean-inspired skincare brand from Bhatkal, Karnataka, making avocado night creams and glutathione cream with aloe vera, vitamin B3 and kojic acid.",
       "telephone":PHONE.replace(" ",""),"address":{"@type":"PostalAddress","streetAddress":"Azad Nagar 4th Cross","addressLocality":"Bhatkal","addressRegion":"Karnataka","postalCode":"581320","addressCountry":"IN"},
       "areaServed":{"@type":"Country","name":"India"},"currenciesAccepted":"INR","paymentAccepted":"Cash on Delivery, UPI, card",
       "contactPoint":{"@type":"ContactPoint","telephone":PHONE.replace(" ",""),"contactType":"customer service","areaServed":"IN","availableLanguage":["English","Hindi"]},
       "hasMerchantReturnPolicy":RETURN_POLICY}
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
    return d

def ld(*nodes):
    return '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@graph":list(nodes)}, ensure_ascii=False, separators=(",",":")).replace("</","<\\/") + "</script>"

# ---------------------------------------------------------------- layout
CSS_HREF = None
JS_HREF = None
def head(title, desc, url, *, lang="en", og_type="website", image=None, canonical=None, alts=None, extra="", robots="index, follow, max-image-preview:large, max-snippet:-1"):
    canonical = canonical or SITE + url
    image = SITE + (image or PBY["avocado-korean-night-cream"]["img"])
    hl = ""
    if alts:
        for code, u in alts: hl += f'<link rel="alternate" hreflang="{code}" href="{SITE+u}">'
    return f'''<!doctype html>
<html lang="{'hi-IN' if lang=='hi' else 'en-IN'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="{robots}">
{hl}
<meta property="og:locale" content="{'hi_IN' if lang=='hi' else 'en_IN'}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/logo.png">
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
        url, extra=f'<link rel="preload" as="image" href="{hero[0]["img"][:-4]}.mg.webp" type="image/webp" fetchpriority="high">' + ld(ORG, WEBSITE, itemlist, faq_ld(faqs)))
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

def compare_table(items):
    rows = "".join(f'<tr><td><a href="/product/{p["slug"]}/">{esc(p["name"])}</a></td><td>{p["size"]}</td><td>{inr(p["price"])} <s style="color:var(--muted)">{inr(p["mrp"])}</s></td>'
                   f'<td>about {inr(round(p["price"]/p["grams"]))}</td><td>{esc(p["when"])}</td><td>{esc(p["best"])}</td></tr>' for p in items)
    return f'<div class="tbl"><table><caption class="sr">Mirc Glow creams compared</caption><thead><tr><th scope="col">Cream</th><th scope="col">Size</th><th scope="col">Price</th><th scope="col">Per gram</th><th scope="col">When</th><th scope="col">Best for</th></tr></thead><tbody>{rows}</tbody></table></div>'

def listing(url, title, desc, h1, ko, intro, items, crumbs, active_chip, extra_html=""):
    chips = [("All","/shop/"),("Night creams","/product-category/night-creams/"),("Avocado","/product-category/night-creams/avocado-night-creams/"),("Combos and kits","/product-category/combos/")]
    chip_html = "".join(f'<a href="{u}"{" aria-current=\"page\"" if u==active_chip else ""}>{n}</a>' for n,u in chips)
    il = {"@type":"ItemList","name":h1,"numberOfItems":len(items),"itemListElement":[{"@type":"ListItem","position":i+1,"url":SITE+f"/product/{p['slug']}/","name":p["name"]} for i,p in enumerate(items)]}
    cp = {"@type":"CollectionPage","@id":SITE+url,"url":SITE+url,"name":h1,"description":desc,"isPartOf":{"@id":SITE+"/#website"}}
    body = head(title, desc, url, extra=ld(ORG, cp, il, crumbs_ld(crumbs)))
    body += header("/shop/")
    body += f'<main id="main">{crumbs_html(crumbs)}<div class="w ptop"><span class="lab">{ko}</span><h1 class="dsp">{esc(h1)}</h1><p>{esc(intro)}</p><nav class="chips" aria-label="Categories">{chip_html}</nav></div>'
    body += f'<section class="w" style="padding-bottom:clamp(48px,6vw,90px)"><div class="grid4">{"".join(card_html(p, "h2") for p in items)}</div></section>'
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

def build_shop():
    help_html = f'''<section class="w" style="padding-bottom:clamp(56px,8vw,110px)"><div class="brief"><div><span class="lab">How ordering works</span><h2 class="dsp" style="margin-top:14px">Order in <em>one message</em>.</h2></div>
<div class="say"><p>Tap <b>Order</b> on any cream. WhatsApp opens with your order already written. Add your name, address and pincode, choose Cash on Delivery or online payment, and send. We confirm the order and share the tracking number when it ships.</p>
<p>Not sure which cream to choose? Take the <a class="link" href="/skin-quiz/">skin quiz</a> or <a class="link" href="{WA_ASK}" target="_blank" rel="noopener">ask us on WhatsApp</a>.</p></div></div></section>'''
    listing("/shop/","Shop Avocado Night Cream and Glutathione Cream | Mirc Glow",
            "Shop all Mirc Glow creams and combos from ₹349: avocado night creams, glutathione cream and glass skin kits. Free shipping and Cash on Delivery across India.",
            "Shop all creams", '<span lang="ko">컬렉션</span> · THE COLLECTION',
            "Four Korean-inspired creams and three sets. Free shipping across India, Cash on Delivery, and 7-day returns on sealed jars.",
            PRODUCTS, [("Home","/"),("Shop","/shop/")], "/shop/", help_html)
    for c, d in CATS.items():
        items = [p for p in PRODUCTS if c in p["cats"]]
        cr = [("Home","/"),("Shop","/shop/")]
        if d["parent"]: cr.append((CATS[d["parent"]]["name"], cat_url(d["parent"])))
        cr.append((d["name"], cat_url(c)))
        listing(cat_url(c), d["rt"], d["rd"], d["h1"], d["ko"], d["intro"], items, cr, cat_url(c))

def related_posts(p, n=3):
    same = [q for q in LIVE_POSTS if q["topic"] == p["topic"] and q["slug"] != p["slug"]]
    other = [q for q in LIVE_POSTS if q["topic"] != p["topic"] and q["slug"] != p["slug"]]
    return (same + other)[:n]

def guide_note():
    return f'''<aside class="note"><b>About this guide</b><p>Written by <a href="/about-the-author/">Mohammed Nihal</a>, founder of Mirc Glow, in Bhatkal, Karnataka, and reviewed on {fmt_date(TODAY)}. This is general skincare information, not medical advice. If you have a skin condition, are pregnant, or get a reaction that does not settle, please see a dermatologist.</p><p>Questions about our creams? WhatsApp <a href="{WA_ASK}" target="_blank" rel="noopener">{PHONE}</a>. Free shipping · Cash on Delivery · <a href="/returns-refunds/">7-day returns</a> on sealed jars.</p></aside>'''

def product_cta(p):
    return (f'<aside class="pcta" aria-label="Featured cream">{photo(p, "", alt=p["name"])}<div><span class="lab">From this guide</span><h2>{esc(p["name"])} · {p["size"]}</h2><p>{esc(p["lead"])}</p>'
            f'<div class="row"><span class="price">{inr(p["price"])} <s>{inr(p["mrp"])}</s></span><a class="order" href="{wa(order_msg(p))}" target="_blank" rel="noopener">Order on WhatsApp</a><a class="link" href="/product/{p["slug"]}/">Details</a></div></div></aside>')

def build_post(p):
    url = f"/{p['slug']}/"
    raw = read(os.path.join(SRC, "posts", p["slug"] + ".html"))
    body_html, toc = add_h2_ids(lazy_imgs(raw))
    faqs = faqs_from(raw)
    mins = max(2, round(words(raw) / 200))
    hub = HUB.get(p["slug"])
    canonical = SITE + f"/{hub}/" if hub else None
    topic_name, prod_slug = TOPICS[p["topic"]]
    prod = PBY[prod_slug]
    crumbs = [("Home","/"),("Journal","/blog/"),(p["title"], url)]
    art = {"@type":"BlogPosting","@id":SITE+url+"#article","headline":p["title"],"description":p["rd"],"datePublished":p["date"]+"T09:00:00+05:30","dateModified":TODAY+"T09:00:00+05:30",
           "author":{"@type":"Person","name":"Mohammed Nihal","url":SITE+"/about-the-author/","jobTitle":"Founder, Mirc Glow"},"publisher":{"@id":ORG_ID},"mainEntityOfPage":SITE+url,
           "image":SITE+prod["img"],"inLanguage":"en-IN","articleSection":topic_name,"wordCount":words(raw),"isPartOf":{"@id":SITE+"/#website"},
           "about":[{"@type":"Thing","name":topic_name}]}
    nodes = [ORG, art, crumbs_ld(crumbs)]
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
<div class="short"><p>{esc(p["ex"])}</p></div>
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
        ("/category/skincare-guides/","Skincare Guides | Mirc Glow","Mirc Glow skincare guides: how to choose and use night creams, glutathione and kojic acid creams, and simple glass skin routines for Indian skin.","Skincare guides",[("Home","/"),("Journal","/blog/"),("Skincare guides","/category/skincare-guides/")]),
    ]:
        il = {"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":SITE+f"/{p['slug']}/"} for i,p in enumerate(LIVE_POSTS)]}
        cp = {"@type":"CollectionPage","@id":SITE+url,"url":SITE+url,"name":h1,"description":desc}
        out = head(title, desc, url, extra=ld(ORG, cp, il, crumbs_ld(crumbs)))
        out += header("/blog/")
        out += f'''<main id="main">{crumbs_html(crumbs)}<div class="w ptop"><span class="lab"><span lang="ko">가이드</span> · Skincare guides</span><h1 class="dsp">{esc(h1)}</h1><p>Honest, plain-English guides to night creams, glutathione, kojic acid and glass skin routines for Indian weather. Written by the Mirc Glow team; general information, not medical advice.</p><nav class="chips" aria-label="Topics">{chips}</nav></div>
<section class="w" style="padding-bottom:clamp(48px,6vw,80px)"><h2 class="lab" style="margin-bottom:22px">Start here</h2><div class="journal">{"".join(post_card(p) for p in hubs)}</div></section>
{secs}{tools}</main>'''
        out += footer()
        write(url, out)

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
               extra=f'<meta property="product:price:amount" content="{p["price"]}"><meta property="product:price:currency" content="INR"><meta property="product:availability" content="in stock"><link rel="preload" as="image" href="{p["img"][:-4]}.mg.webp" type="image/webp" fetchpriority="high">' + ld(*nodes))
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

def build_page(g):
    url = f"/{g['slug']}/"
    raw = read(os.path.join(SRC, "pages", g["slug"] + ".html"))
    raw = lazy_imgs(raw)
    faqs = faqs_from(raw)
    if g["slug"] in CITY: cr = [("Home","/"),("Bulk orders","/bulk-night-cream/"),(g["crumb"], url)]
    else: cr = [("Home","/"),(g["crumb"], url)]
    alts = None
    if g["alt"]:
        en, hi = (g["slug"], g["alt"]) if g["lang"] == "en" else (g["alt"], g["slug"])
        alts = [("en-IN", f"/{en}/"), ("hi-IN", f"/{hi}/"), ("x-default", f"/{en}/")]
    ptype = {"about":"AboutPage","contact":"ContactPage","faq":"FAQPage"}.get(g["slug"], "WebPage")
    wp = {"@type":ptype if ptype != "FAQPage" else "WebPage","@id":SITE+url,"url":SITE+url,"name":g["title"],"description":g["rd"],"inLanguage":"hi-IN" if g["lang"]=="hi" else "en-IN","isPartOf":{"@id":SITE+"/#website"},"dateModified":TODAY}
    nodes = [ORG, wp, crumbs_ld(cr)]
    if faqs: nodes.append(faq_ld(faqs))
    out = head(g["rt"], g["rd"], url, lang=g["lang"], image=g["img"], alts=alts, extra=ld(*nodes))
    out += header()
    if g["kind"] == "legacy":
        out += f'<main id="main" class="lg">{crumbs_html(cr)}{raw}</main>'
    else:
        out += f'<main id="main" class="plain">{crumbs_html(cr)}<div class="w"><article class="prose">{raw}<p style="margin-top:3em;font-size:.85rem;color:var(--muted)">{"अंतिम अपडेट" if g["lang"]=="hi" else "Last reviewed"}: {fmt_date(TODAY)}</p></article></div></main>'
    out += footer()
    write(url, out)


WPCATS = {  # WordPress post categories (same URLs as on WordPress)
 "night-cream-guides": ("Night Creams","How to choose and use a night cream in India: by skin type, for men, for oily and dry skin, and step-by-step night routines.",
   ["how-to-apply-night-cream","night-cream-for-men","night-cream-for-oily-skin","best-night-cream-for-glowing-skin","which-is-the-no-1-night-cream-in-india","how-to-build-a-simple-night-skincare-routine"]),
 "avocado-skincare": ("Avocado Skincare","Honest guides to avocado cream and avocado night cream: what avocado does for skin, who it suits, side effects, and how to use it.",
   ["avocado-cream-for-dry-skin","avocado-night-cream-side-effects","is-avocado-cream-good-for-your-skin","is-avocado-night-cream-good","how-to-make-avocado-night-cream-at-home","can-i-use-avocado-night-cream-every-night"]),
 "glutathione-kojic-acid": ("Glutathione and Kojic Acid","Plain-English guides to glutathione cream and kojic acid cream: benefits, how long they take, side effects, how to use them and how they compare.",
   ["kojic-acid-cream-for-dark-spots","kojic-acid-vs-glutathione","how-to-use-glutathione-cream","how-long-does-glutathione-cream-take-to-work","glutathione-cream-side-effects","glutathione-cream-benefits"]),
 "korean-skincare-glass-skin": ("Korean Skincare and Glass Skin","Korean skincare made simple for Indian skin: glass skin routines adapted for heat, humidity and strong sun.",
   ["glass-skin-routine-for-indian-skin"]),
}

def build_wpcats():
    for slug,(name,desc,posts) in WPCATS.items():
        url=f"/category/{slug}/"; items=[POST_BY[x] for x in posts]
        crumbs=[("Home","/"),("Skincare guides","/blog/"),(name,url)]
        cp={"@type":"CollectionPage","@id":SITE+url,"url":SITE+url,"name":name,"description":desc,"isPartOf":{"@id":SITE+"/#website"}}
        robots = "index, follow, max-image-preview:large, max-snippet:-1" if len(items) > 1 else "noindex, follow"
        out=head(f"{name} %s Skincare Guides | Mirc Glow" % "-", desc, url, robots=robots, extra=ld(ORG,cp,crumbs_ld(crumbs)))
        out+=header("/blog/")
        out+=f'<main id="main">{crumbs_html(crumbs)}<div class="w ptop"><span class="eyebrow">Skincare guides</span><h1 class="dsp">{esc(name)}</h1><p>{esc(desc)}</p></div><section class="w" style="padding-bottom:40px"><div class="posts">{"".join(post_card(p) for p in items)}</div></section></main>'
        out+=footer()
        write(url,out)

def build_404():
    out = head("Page not found | Mirc Glow", "This page could not be found. Browse Mirc Glow avocado night creams, glutathione cream and skincare guides instead.", "/404.html", robots="noindex, follow")
    out += header()
    out += f'''<main id="main" class="err"><div class="w" style="display:grid;gap:22px;justify-items:center;padding-block:80px"><span class="lab">404</span><h1 class="dsp" style="font-size:clamp(2.6rem,6vw,4.4rem)">This page has <em>moved</em>.</h1><p style="color:var(--muted);max-width:46ch">The link may be old. Try the shop, the journal, or ask us on WhatsApp and we will point you to the right cream.</p><div class="row" style="justify-content:center"><a class="btn dark" href="/shop/">Shop creams</a><a class="btn line" href="/blog/">Read the journal</a></div></div></main>'''
    out += footer()
    with open(os.path.join(DIST, "404.html"), "w", encoding="utf-8") as f: f.write(out)

# ---------------------------------------------------------------- machine-readable files
def indexable_urls():
    u = [("/", "1.0", TODAY), ("/shop/", "0.9", TODAY), ("/blog/", "0.7", TODAY), ("/category/skincare-guides/", "0.4", TODAY)]
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
        items.append(x + "</url>")
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
          + "\n".join(items) + "\n</urlset>\n")
    write("/sitemap.xml", sm)
    write("/sitemap_index.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>{SITE}/sitemap.xml</loc><lastmod>{TODAY}</lastmod></sitemap></sitemapindex>\n')

def build_robots():
    bots = ["GPTBot","OAI-SearchBot","ChatGPT-User","ClaudeBot","Claude-SearchBot","Claude-User","PerplexityBot","Perplexity-User","Google-Extended","Applebot","Applebot-Extended","Bingbot","CCBot","meta-externalagent","Amazonbot","DuckAssistBot"]
    txt = "# Mirc Glow — search engines and AI assistants are welcome.\nUser-agent: *\nAllow: /\n\n"
    txt += "\n".join(f"User-agent: {b}\nAllow: /\n" for b in bots)
    txt += f"\nSitemap: {SITE}/sitemap.xml\nSitemap: {SITE}/sitemap_index.xml\n"
    write("/robots.txt", txt)

def build_llms():
    L = [f"# {BRAND}", "",
         "> Korean-inspired skincare brand from Bhatkal, Karnataka, India. Four creams and three sets built around avocado, glutathione and kojic acid; every cream also contains aloe vera and vitamin B3. Sold directly across India with free shipping, Cash on Delivery and 7-day returns on sealed jars. Orders are placed on WhatsApp (+91 99808 81230).", "",
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
          "", "## Buying guides and tools",
          f"- [Avocado cream guide]({SITE}/avocado-cream/) (Hindi: {SITE}/avocado-cream-hindi/)",
          f"- [Korean night cream guide]({SITE}/korean-night-cream/) (Hindi: {SITE}/korean-night-cream-hindi/)",
          f"- [Skin quiz]({SITE}/skin-quiz/)", f"- [Skincare routine builder]({SITE}/skincare-routine-builder/)", f"- [Skincare ingredient glossary]({SITE}/skincare-ingredient-glossary/)",
          f"- [Our ingredients]({SITE}/ingredients/)", f"- [FAQ]({SITE}/faq/)", f"- [About Mirc Glow]({SITE}/about/)",
          "", "## Skincare guides"]
    for p in LIVE_POSTS: L.append(f"- [{p['title']}]({SITE}/{p['slug']}/): {p['ex']}")
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
        R("/cart/:path*", "/shop/"), R("/checkout/:path*", "/shop/"), R("/my-account/:path*", "/shop/"),
        R("/product-category/uncategorized/", "/shop/"), R("/category/uncategorized/", "/blog/"),
        R("/product-tag/:slug*", "/shop/"), R("/tag/:slug*", "/blog/"), R("/author/:slug*", "/about/"),
        R("/home/", "/"), R("/sample-page/", "/"),
        R("/post-sitemap.xml", "/sitemap.xml"), R("/page-sitemap.xml", "/sitemap.xml"), R("/product-sitemap.xml", "/sitemap.xml"),
        R("/product_cat-sitemap.xml", "/sitemap.xml"), R("/category-sitemap.xml", "/sitemap.xml"), R("/local-sitemap.xml", "/sitemap.xml"),
        R("/wp-sitemap.xml", "/sitemap.xml"),
        R("/feed/:path+", "/feed/"), R("/comments/feed/", "/feed/"),
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
                      {"source":"/llms.txt","headers":[{"key":"Content-Type","value":"text/plain; charset=utf-8"}]}]}
    with open(os.path.join(DIST, "vercel.json"), "w") as f: json.dump(cfg, f, indent=2)

def build_assets():
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
    icon = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><radialGradient id="g" cx=".38" cy=".3"><stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#F7E6E8"/><stop offset="1" stop-color="#E3B4BF"/></radialGradient></defs>'
            '<circle cx="32" cy="32" r="30" fill="url(#g)"/><text x="32" y="41" text-anchor="middle" font-family="Georgia,serif" font-size="26" fill="#9C5468">M</text></svg>')
    with open(os.path.join(DIST, "assets", "icon.svg"), "w") as f: f.write(icon)
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
    build_404(); build_sitemaps(); build_robots(); build_llms(); build_feed(); build_vercel()
    n = sum(len(fs) for _, _, fs in os.walk(DIST))
    print(f"built {n} files into dist/")

if __name__ == "__main__":
    main()
