# Writing brief: Mirc Glow skincare guides (mircglow.com)

Mirc Glow is a small Korean-inspired skincare brand from Bhatkal, Karnataka, India, founded by Mohammed Nihal. It sells 4 creams and 3 sets (see LINKS.md for products, prices, ingredients). Every cream contains aloe vera, vitamin B3 (niacinamide) and kojic acid. Free shipping across India (3–7 days), Cash on Delivery or online payment link, 7-day returns on sealed jars, orders on WhatsApp +91 99808 81230. Bulk night cream by the kg for salons/resellers.

## Audience and voice
Indian readers, mostly women 18–40, many on phones, Indian weather (heat, humidity, monsoon, AC, hard water, pollution). Warm, plain, confident English (or simple Hindi for Hindi pages). Short sentences. Practical. Write as the Mirc Glow team / founder; never claim to be a doctor.

## Hard rules (Google Merchant / honesty)
- Cosmetic wording only: "helps skin feel moisturised", "brighter-looking", "more even-looking", "reduce the look of".
- NEVER: cure, treat, heal, remove, whitening, fairness, fair skin, lighten skin colour, bleach, permanent, guaranteed, "results in X days", "clinically proven", "dermatologist recommended", "No. 1".
- No invented statistics, studies, percentages of users, quotes, reviews, customers, doctors or experts. Ingredient facts must be general and well known (e.g. kojic acid typically ~1–2% in creams; skin renews roughly every 4–6 weeks; 8–12 weeks for a more even look).
- Always: patch test advice, sunscreen in the morning (especially with kojic acid), "see a dermatologist if…" for conditions (acne that is painful/cystic, melasma, rashes, pregnancy).
- Do not name or attack competitor brands.
- Mention Mirc Glow products naturally 1–3 times where they truly fit, with links. Not salesy.

## Structure of each English guide (HTML fragment, NO <h1>, NO <html>/<body>, NO inline styles, NO <img>)
1. Opening 1–2 short <p> paragraphs that directly answer the title question in the first 2 sentences.
2. 5–9 <h2> sections with real substance (steps as <ol>, comparisons as a simple <table> with <thead>/<tbody>, tips as <ul>). Use <h3> only inside sections where helpful.
3. At least 4 internal links to existing pages from LINKS.md (exact paths, relative like /avocado-cream/), plus 1–2 product links.
4. A final section exactly: <h2>Short answers</h2> followed by 4–6 lines in the form <p><strong>Question ending with ?</strong> Answer in 1–2 sentences.</p>
5. Last line: <p><em>This is general skincare information, not medical advice. Patch test any new product, and see a dermatologist if you have a skin condition.</em></p>
Length: 900–1,300 words. Use the target keyword naturally in the first paragraph, one <h2>, and 2–4 times overall. Include related phrases Indians search (e.g. "for oily skin", "in summer", "kaise lagaye" only on Hindi pages).

## Hindi pages (HTML fragment WITH one <h1> in Hindi that includes the Hinglish keyword in brackets)
Same rules, in simple Hindi (Devanagari) with common English skincare words where natural (क्रीम, स्किन, सनस्क्रीन). 800–1,200 words. Open with <p><strong>छोटा जवाब:</strong> …</p>. Include a simple table. End with <h2>अक्सर पूछे जाने वाले सवाल (FAQ)</h2> then 4–5 pairs of <h3>सवाल?</h3><p>जवाब</p>, then the disclaimer in Hindi (<p><em>…</em></p>). Link to at least 3 existing pages (Hindi pages /avocado-cream-hindi/, /korean-night-cream-hindi/, /avocado-night-cream-benefits-hindi/ where relevant, plus English guides/products).

## City bulk pages
Follow the exact HTML structure and CSS classes of content/pages/night-cream-in-kg-mumbai.html (read it first), changing the city. Use honest, general local context only (climate, typical salon/bridal demand, being shipped by courier from Bhatkal, Karnataka). Never invent addresses, clients, delivery times beyond "usually 3–7 days" or prices.

## For EVERY file you write, also write a metadata file
content/plan/<slug>.json :
{"slug": "...", "kind": "post" | "hindi" | "city", "title": "on-page title (H1 for posts)", "ex": "1–2 sentence excerpt (≤200 chars)",
 "rt": "SEO title ≤ 62 chars ending with ' | Mirc Glow'", "rd": "meta description 140–158 chars, includes keyword, no claims",
 "topic": "avocado|glutathione|kojic|routine|night", "keyword": "main target search",
 "quick": "2–3 sentence direct answer (40–60 words)", "facts": ["3–4 short key facts"]}
(For city pages: topic "night", quick/facts may be empty strings/lists.)

Files go to: English guides → content/posts/<slug>.html ; Hindi → content/pages/<slug>.html ; City → content/pages/<slug>.html.
Do not edit any other file. When finished, reply with just the list of slugs written.
