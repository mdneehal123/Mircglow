# Mirc Glow: going live on Vercel

This repository is the whole website. Every page keeps the same address it had on WordPress, and the product photos are already included at their old addresses.

## 1. Connect to Vercel

1. On vercel.com, choose **Add New → Project**, then import the GitHub repository **mircglow**.
2. Framework Preset: **Other**. Leave Build Command and Install Command empty. Output Directory: `dist` (already set in `vercel.json`). The `api/` folder holds the checkout functions; Vercel deploys them automatically, no setting needed.
3. Deploy, then open the `*.vercel.app` link and check the home page, a product page, the blog and the skin quiz.

## 1b. Switch on the website checkout

Add the environment variables listed in `README.md` (Razorpay, Delhivery, Order Desk), then redeploy. Place one small test order of each kind (online and Cash on Delivery) and check that it appears in the Order Desk and, for COD, in the Delhivery panel.

## 2. Switch the domain

1. In Vercel, open the project → **Settings → Domains** and add `mircglow.com` and `www.mircglow.com`.
2. At your domain provider, change the DNS records to the values Vercel shows (usually an **A** record `76.76.21.21` for `@` and a **CNAME** `cname.vercel-dns.com` for `www`).
3. Wait until mircglow.com shows the new site, then stop WordPress. Download your WooCommerce orders and customers first if you want to keep them.

## 3. Search Console, on the day you switch

1. Sitemaps: submit `https://mircglow.com/sitemap.xml` (the old `sitemap_index.xml` points to it).
2. URL Inspection: request indexing for the home page, `/shop/` and the 7 product pages.
3. A small dip for a few days is normal.

## 4. About 4 weeks after launch

Eight older articles point Google to their newer, fuller guides with canonical tags. After about 4 weeks, convert them to permanent redirects (list in `MIGRATION_NOTES.md`).

## Making changes

Edit the files in `content/` or `src/`, run `python3 build.py`, check with `python3 check.py`, then commit and push. Vercel publishes the new version automatically.
