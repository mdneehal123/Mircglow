# Mirc Glow: going live on GitHub and Vercel

This folder is the whole website. Every page keeps the same address it had on WordPress.

## 1. Add your product photos (required)

The pages use your existing images at the same paths, `/wp-content/uploads/...`.

1. In your WordPress hosting, open File Manager or FTP and go to `public_html/wp-content/uploads/`.
2. Download the folders `2026/09` and `2026/10`.
3. Put them inside this folder so the paths look like this:
   `wp-content/uploads/2026/09/4ED0DC3B-11FA-4903-87CC-21E1887C89E5.png`

You can skip the resized copies that end in `-300x300` or `-768x768`. Only the original files are used.

Until the photos are added, each product shows a pink jar illustration in place of its photo.

## 2. Upload to GitHub

1. Create a new repository on github.com, for example `mircglow-site`.
2. Choose "uploading an existing file" and drag in everything in this folder, including `wp-content`.
3. Commit.

## 3. Deploy on Vercel

1. On vercel.com, choose Add New → Project → Import the GitHub repository.
2. For Framework Preset, choose **Other**. Leave Build Command empty. Leave Output Directory empty, or set it to `.`.
3. Deploy, then open the `*.vercel.app` link and check:
   - The home page, a product page, the blog and the skin quiz load.
   - Product photos appear.
   - Opening `/cart/` takes you to `/shop/`.
   - Tapping **Order** opens WhatsApp with the order already written.

## 4. Switch the domain

1. In Vercel, open Project → Settings → Domains and add `mircglow.com` and `www.mircglow.com`.
2. At your domain registrar, change the DNS records to the values Vercel shows. These are usually an A record `76.76.21.21` for `@` and a CNAME `cname.vercel-dns.com` for `www`.
3. Keep the WordPress hosting running for 2 weeks in case you need anything from it.

## 5. Search Console, on the day you switch

1. Sitemaps: submit `https://mircglow.com/sitemap.xml`. You can keep the old `sitemap_index.xml`, because it now points to the new sitemap.
2. URL Inspection: request indexing for the home page, `/shop/` and the 7 product pages.
3. Check the Pages report a week later. A temporary dip for a few days is normal.

## 6. About 4 weeks after launch

Eight older articles currently point Google to their newer, fuller guides using canonical tags. After about 4 weeks, convert them to permanent redirects. Ask Claude to "convert the consolidated posts to 301", or follow the list in `MIGRATION_NOTES.md`.

## 7. Payment links (optional)

When you create Razorpay payment links, add them to `PAYLINKS` in `build.py`, then run `python3 build.py`. A "Pay online now" button will then appear on each product page.

## What changed from WordPress

- Customers order on WhatsApp instead of using a cart and checkout. `/cart/`, `/checkout/` and `/my-account/` redirect to `/shop/`.
- WooCommerce, Razorpay checkout and the Shiprocket plugin are no longer used. You can still create Shiprocket shipments from its own dashboard.
- Pages load from Vercel's global network with no plugins or database, so they are much faster.
