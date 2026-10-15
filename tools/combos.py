"""Builds the combo and kit photos by placing the real jar photos together on white (multiply blend)."""
import os
from PIL import Image, ImageChops, ImageFilter
U = "wp-content/uploads/2026/09/"
SRC = {"korean": U+"4ED0DC3B-11FA-4903-87CC-21E1887C89E5.png", "gluta": U+"5D782746-D1F2-496B-8449-5B8149C43004-1.png",
       "night": U+"04BCBF62-EE16-4594-B65C-BDA805C264CB-1.png", "glow": U+"2DFA2551-B14E-43F6-8929-E39538EC9628-1.png",
       "glass": "wp-content/uploads/2026/10/mirc-glow-glass-glow-cream-glutathione-30g.png", "glow15": "wp-content/uploads/2026/10/mirc-glow-avocado-glow-cream-15g-jars.png"}

def whiten(path, soft=(18, 46)):
    """Turns the photo's plain background white, keeping the jar untouched."""
    im = Image.open(path).convert("RGB"); w, h = im.size
    edge = [im.getpixel((x, y)) for x in range(0, w, 9) for y in (0, h-1)] + [im.getpixel((x, y)) for y in range(0, h, 9) for x in (0, w-1)]
    bg = tuple(sorted(c[i] for c in edge)[len(edge)//2] for i in range(3))
    d = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L")
    lo, hi = soft
    keep = d.point(lambda v: 0 if v <= lo else 255 if v >= hi else int((v-lo)*255/(hi-lo))).filter(ImageFilter.GaussianBlur(1))
    out = Image.composite(im, Image.new("RGB", im.size, "white"), keep)
    box = ImageChops.invert(out.convert("L")).point(lambda v: 255 if v > 12 else 0).getbbox()
    return out.crop(box)

def compose(parts, size=1200, margin=50, gap=10, base=.80):
    """Places the jars side by side (no overlap) on a white square. parts = [(key, relative size)]"""
    jars = []
    for key, rel in parts:
        j = whiten(SRC[key]); jars.append((j, rel))
    # height of each jar ~ rel; scale everything so the row fits the width
    hs = [rel for _, rel in jars]; ws = [j.width / j.height * rel for j, rel in jars]
    k = min((size - 2*margin - gap*(len(jars)-1)) / sum(ws), .74*size / max(hs))
    canvas = Image.new("RGB", (size, size), "white")
    total = sum(w*k for w in ws) + gap*(len(jars)-1); x = (size - total) / 2
    bottom = (size + max(hs)*k) / 2 + size*.02
    for (j, rel), w in zip(jars, ws):
        jj = j.resize((max(1, round(w*k)), max(1, round(rel*k))), Image.LANCZOS)
        layer = Image.new("RGB", canvas.size, "white"); layer.paste(jj, (round(x), round(bottom - jj.height)))
        canvas = ImageChops.multiply(canvas, layer); x += jj.width + gap
    return canvas

COMBOS = {
 "mirc-glow-day-and-night-cream-combo": [("night", 1.0), ("glow", .55)],
 "mirc-glow-night-cream-combo": [("gluta", .85), ("night", 1.0)],
 "mirc-glow-korean-glass-skin-kit": [("gluta", .8), ("korean", 1.0), ("glow", .55)],
 "mirc-glow-glass-glow-night-duo": [("glass", 1.25), ("night", .8)],
}
if __name__ == "__main__":
    os.makedirs("wp-content/uploads/2026/10", exist_ok=True)
    for name, parts in COMBOS.items():
        im = compose(parts)
        im.save(f"wp-content/uploads/2026/10/{name}.png", optimize=True)
        im.resize((900, 900), Image.LANCZOS).save(f"wp-content/uploads/2026/10/{name}.mg.webp", "WEBP", quality=82, method=6)
        print(name)
