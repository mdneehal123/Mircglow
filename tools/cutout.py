"""Cuts product jars out of their plain photo background (flood fill from the edges)."""
from PIL import Image, ImageChops, ImageFilter, ImageDraw
def cutout(path, tol=22):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    # background colour = median of the border pixels
    border = [im.getpixel((x, 0)) for x in range(0, w, 7)] + [im.getpixel((x, h-1)) for x in range(0, w, 7)] + \
             [im.getpixel((0, y)) for y in range(0, h, 7)] + [im.getpixel((w-1, y)) for y in range(0, h, 7)]
    bg = tuple(sorted(c[i] for c in border)[len(border)//2] for i in range(3))
    diff = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L")
    near = diff.point(lambda v: 255 if v < tol else 0)          # 255 = looks like background
    mask = Image.new("L", im.size, 0)
    # flood-fill only the background that touches the edges, so white parts inside the jar stay
    fill = near.copy()
    for seed in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, 0), (w//2, h-1), (0, h//2), (w-1, h//2)]:
        if fill.getpixel(seed) == 255: ImageDraw.floodfill(fill, seed, 128)
    bgmask = fill.point(lambda v: 255 if v == 128 else 0)
    alpha = ImageChops.invert(bgmask).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGBA"); out.putalpha(alpha)
    return out.crop(out.getbbox())
