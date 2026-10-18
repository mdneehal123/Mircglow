# Mirc Glow migration notes (14 Oct 2026)

## Redirects to add in vercel.json (permanent 301)
Old product slugs (WordPress redirected these automatically):
- /product/mirc-glow-avocado-korean-night-cream-with-aloe-vera-vitamin-b3-kojic-acid-glutathione-inspired-brightening-night-cream-for-women-men-30-g/ -> /product/avocado-korean-night-cream/
- /product/glutathione-kojic-acid-cream/ -> /product/avocado-korean-night-cream/
- /product/luminous-barrier-cream/ -> /product/glutathione-cream/
- /product/radiance-renewal-serum/ -> /product/avocado-night-cream/
- /product/glow-clarifying-cleanser/ -> /product/avocado-face-cream/
- /is-avocado-face-cream-good-for-glowing-skinis-avocado-cream-good-for-your-skin/ -> /is-avocado-cream-good-for-your-skin/

Shop flows (website checkout added Oct 2026):
- /cart/ and /checkout/ are real pages again (noindex); old subpaths such as /checkout/order-received/... -> /checkout/, /cart/... -> /cart/
- /my-account/ (and subpaths) -> /shop/
- ?add-to-cart= links -> rewrite to WhatsApp order links in HTML

## Consolidated posts (canonical set on WordPress 14 Oct; convert to 301 ~4 weeks after launch)
- 149 /is-avocado-cream-good-for-the-face/ -> /is-avocado-cream-good-for-your-skin/
- 145 /is-avocado-good-for-skin-brightening/ -> /is-avocado-cream-good-for-your-skin/
- 139 /is-avocado-face-cream-good-for-glowing-skin/ -> /is-avocado-cream-good-for-your-skin/
- 32 /a-brighter-looking-skincare-routine-made-simple/ -> /is-avocado-night-cream-good/
- 98 /glass-skin-routine-steps-for-a-smooth-hydrated-looking-glow/ -> /glass-skin-routine-for-indian-skin/
- 93 /korean-skincare-glass-skin-building-a-simple-glow-focused-routine/ -> /glass-skin-routine-for-indian-skin/
- 94 /kojic-acid-in-skincare-a-guide-to-brightening-focused-care/ -> /kojic-acid-cream-for-dark-spots/
- 95 /glutathione-in-skincare-what-it-is-and-how-it-fits-into-a-routine/ -> /glutathione-cream-benefits/

## Schema to add in static build
- Organization/LocalBusiness: Mirc Glow, Azad Nagar 4th Cross, Bhatkal, Karnataka 581320, IN, +91 99808 81230
- Product + Offer (INR, InStock), OfferShippingDetails (free, IN, 3-7 days), MerchantReturnPolicy (7 days, sealed)
- BreadcrumbList, Article (datePublished/dateModified)
- hreflang: /avocado-cream/ <-> /avocado-cream-hindi/ ; /korean-night-cream/ <-> /korean-night-cream-hindi/

## Prices (Oct 2026)
- 22 Avocado Glow 10g: 349 (449)
- 23 Avocado Night Cream 30g: 649 (949)
- 66 Avocado Korean Night Cream 25g: 649 (899)
- 24 Glutathione Cream 30g: 1499 (1999)
- 262 Day and Night Combo: 849 (998)
- 263 Night Cream Combo: 1799 (2148)
- 264 Korean Glass Skin Kit: 1999 (2497)
