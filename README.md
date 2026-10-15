# Mirc Glow website (mircglow.com)

Static website for Mirc Glow, hosted on Vercel. Customers order on WhatsApp (+91 99808 81230).

- `content/` – page, article and product text (copied from the old WordPress site)
- `src/` – design (CSS, small script) and page templates
- `wp-content/uploads/` – product photos at the same addresses they had on WordPress
- `build.py` – builds the site into `dist/` (run `python3 build.py`), `check.py` checks links and SEO tags
- `dist/` – the finished website that Vercel serves (settings in `vercel.json`)

Every page keeps the address, title and description it had on WordPress, so Google rankings carry over.
