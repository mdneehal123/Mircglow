// Makes a short vertical (720x1280) explainer video from a slide spec, plus a thumbnail.
// Usage (from the repo root):
//   npm i --no-save --prefix /tmp/mv playwright@1.48.2
//   PW_PREFIX=/tmp/mv node tools/make_video.mjs content/video-specs/<name>.json
// Needs ffmpeg. Output: wp-content/uploads/<yyyy>/<mm>/<out>.mp4 and <out>-thumb.jpg (paths printed).
// Spec: {"out": "mirc-glow-...", "brand": "MIRC GLOW", "color": "#157A36", "bg": "#F6F4EE", "seconds": 5,
//        "slides": [{"kind":"title"|"point"|"steps"|"end", "eyebrow":"", "title":"", "text":"", "steps":["..."], "img":"/wp-content/uploads/..."}]}
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import fs from "node:fs"; import path from "node:path"; import os from "node:os";

const { chromium } = createRequire(path.join(process.env.PW_PREFIX || "/tmp/mv", "x.js"))("playwright");
const spec = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const root = process.cwd(), tmp = fs.mkdtempSync(path.join(os.tmpdir(), "mv-"));
const C = spec.color || "#157A36", BG = spec.bg || "#F6F4EE", SEC = spec.seconds || 5;
const esc = s => String(s || "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const img = p => p ? `<img src="file://${path.join(root, p)}" alt="">` : "";
function slide(s, i) {
  const end = s.kind === "end";
  const body = s.kind === "steps"
    ? `<ol>${(s.steps || []).map((t, n) => `<li><b>${n + 1}</b><span>${esc(t)}</span></li>`).join("")}</ol>${s.text ? `<p class="note">${esc(s.text)}</p>` : ""}`
    : `${s.text ? `<p>${esc(s.text)}</p>` : ""}${img(s.img)}`;
  return `<!doctype html><meta charset="utf-8"><style>
  *{box-sizing:border-box;margin:0}html,body{width:720px;height:1280px}
  body{font-family:"Poppins","DejaVu Sans","Liberation Sans",Arial,sans-serif;background:${end ? C : (i % 2 ? "#EEF5E8" : BG)};color:${end ? "#fff" : "#1B1B1B"};
    display:flex;flex-direction:column;align-items:center;padding:56px 56px 72px;text-align:center}
  .brand{align-self:flex-start;font-weight:800;letter-spacing:.06em;font-size:26px;color:${end ? "#fff" : C}}
  .eyebrow{margin-top:70px;font-size:30px;color:${end ? "#FFE58A" : C};font-weight:600}
  h1{margin-top:${s.eyebrow ? 14 : 110}px;font-size:${(s.title || "").length > 34 ? 54 : 64}px;line-height:1.12;font-weight:800}
  p{margin-top:26px;font-size:34px;line-height:1.35;color:${end ? "#fff" : "#3A3A3A"};max-width:600px}
  img{margin-top:auto;max-width:560px;max-height:560px;border-radius:24px;background:#fff;object-fit:contain}
  ol{list-style:none;margin-top:60px;display:grid;gap:34px;text-align:left;width:100%}
  li{display:flex;gap:22px;align-items:flex-start;font-size:34px;line-height:1.3}
  li b{flex:0 0 56px;height:56px;border-radius:50%;background:${C};color:#fff;display:grid;place-items:center;font-size:28px}
  .note{margin-top:auto;font-size:28px;color:#555}
  .cta{margin-top:auto;font-size:40px;font-weight:800}
  </style><div class="brand">${esc(spec.brand || "")}</div>${s.eyebrow ? `<div class="eyebrow">${esc(s.eyebrow)}</div>` : ""}<h1>${esc(s.title)}</h1>${body}${end && s.cta ? `<div class="cta">${esc(s.cta)}</div>` : ""}`;
}
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 720, height: 1280 } });
const clips = [];
for (const [i, s] of spec.slides.entries()) {
  const html = path.join(tmp, `s${i}.html`), png = path.join(tmp, `s${i}.png`), mp4 = path.join(tmp, `c${i}.mp4`);
  fs.writeFileSync(html, slide(s, i)); await page.goto("file://" + html); await page.waitForTimeout(150);
  await page.screenshot({ path: png });
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-loop", "1", "-t", String(SEC), "-i", png,
    "-vf", `fade=t=in:st=0:d=0.3,fade=t=out:st=${SEC - 0.3}:d=0.3,format=yuv420p`, "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", mp4]);
  clips.push(mp4);
}
await browser.close();
const now = new Date(), dir = path.join("wp-content", "uploads", String(now.getFullYear()), String(now.getMonth() + 1).padStart(2, "0"));
fs.mkdirSync(dir, { recursive: true });
const list = path.join(tmp, "list.txt"); fs.writeFileSync(list, clips.map(c => `file '${c}'`).join("\n"));
const out = path.join(dir, spec.out + ".mp4"), thumb = path.join(dir, spec.out + "-thumb.jpg");
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", list, "-c", "copy", "-movflags", "+faststart", out]);
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", path.join(tmp, "s0.png"), "-q:v", "4", thumb]);
console.log(JSON.stringify({ src: "/" + out, thumb: "/" + thumb, dur: `PT${SEC * spec.slides.length}S`, bytes: fs.statSync(out).size }));
