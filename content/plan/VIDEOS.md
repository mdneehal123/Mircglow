# Videos on mircglow.com

Each video is a 20–35 second vertical (720x1280) explainer made from slides, shown on one or more pages with VideoObject schema and a video sitemap entry.

1. Write a slide spec in content/video-specs/<out>.json (see example-how-to-apply-night-cream.json). Kinds: title, point, steps, end. 4–7 slides, 4–5 seconds each, short lines that read in 3 seconds, real product photos from wp-content/uploads only, real prices only, cosmetic wording only (no whitening/fairness, no "results in X days").
2. Make it: `npm i --no-save --prefix /tmp/mv playwright@1.48.2` once, then `PW_PREFIX=/tmp/mv node tools/make_video.mjs content/video-specs/<out>.json` (needs ffmpeg). It prints src, thumb and dur.
3. Add an entry to content/videos.json: {"name", "description" (1–2 honest sentences), "src", "thumb", "date" (ISO with +05:30), "dur", "pages": ["/<slug>/", ...]}. A page can have only one video; do not reuse a page already listed.
4. `python3 build.py && python3 check.py` (problems: 0). Keep each mp4 under ~1 MB.
