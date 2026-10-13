"""Couvertures d'articles NéoSoluce (1600x900) : style « média tech », 100 % original.

Usage :
    python3 tools/make_cover.py covers/<slug>.jpg "BADGE" "Titre ligne 1|Titre ligne 2" "Sous-titre" <motif> [accent]

motif : carte | gameplay | vehicules | missions | online | infos | actu | astuce
accent : rose (défaut) | cyan | soleil
Aucun élément Rockstar (pas de logo, personnage, capture ni police du jeu).
"""
import math, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_logo import find  # noqa: E402

W, H = 1600, 900
BLACK = find("InterDisplay-Black.otf")
BOLD = find("InterDisplay-Bold.otf")
MED = find("InterDisplay-Medium.otf")
PINK, CYAN, SUN, ORANGE = (255, 61, 154), (45, 226, 230), (255, 209, 102), (255, 122, 89)
NIGHT, VIOLET = (9, 4, 26), (26, 11, 61)
ACCENTS = {"rose": PINK, "cyan": CYAN, "soleil": SUN}


def blob(img, xy, r, color, alpha):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = xy
    d.ellipse([x - r, y - r, x + r, y + r], fill=color + (alpha,))
    return Image.alpha_composite(img, layer.filter(ImageFilter.GaussianBlur(r * 0.55)))


def background(accent):
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    base = np.zeros((H, W, 3))
    for i, (a, b) in enumerate(zip(NIGHT, VIOLET)):
        base[..., i] = a + (b - a) * (0.35 * y + 0.65 * x * y)
    img = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
    img = blob(img, (1250, 260), 360, accent, 120)
    img = blob(img, (1500, 820), 300, CYAN if accent != CYAN else PINK, 90)
    img = blob(img, (150, 900), 280, ORANGE, 55)
    return img


def grid(img, color):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    hz, vx = 610, 1180
    for i in range(1, 14):
        t = (i / 13) ** 2.1
        yy = hz + t * (H - hz + 80)
        d.line([(560, yy), (W, yy)], fill=color + (int(40 + 150 * t),), width=2)
    for k in range(-14, 15):
        x2 = vx + k * 150
        d.line([(vx + k * 8, hz), (x2, H + 60)], fill=color + (110,), width=2)
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    for yy in range(hz, H):
        md.line([(0, yy), (W, yy)], fill=int(255 * min(1, (yy - hz) / 160)))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    g = layer.filter(ImageFilter.GaussianBlur(3))
    return Image.alpha_composite(Image.alpha_composite(img, g), layer)


def sunset(img, cx, cy, r):
    s = Image.new("RGBA", img.size, (0, 0, 0, 0))
    arr = np.zeros((H, W, 4), dtype=np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    inside = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
    t = np.clip((yy - (cy - r)) / (2 * r), 0, 1)
    cols = np.stack([255 + 0 * t, 209 - 148 * t, 102 + 52 * t], -1)
    stripe = np.zeros_like(inside)
    for k in range(7):
        y0 = cy + r * (0.05 + k * 0.14)
        h = 3 + k * 3.2
        stripe |= (yy > y0) & (yy < y0 + h)
    alpha = np.where(inside & ~stripe & (yy < cy + r * 0.98), 235, 0)
    arr[..., :3] = cols.astype(np.uint8)
    arr[..., 3] = alpha.astype(np.uint8)
    s = Image.fromarray(arr, "RGBA")
    g = s.filter(ImageFilter.GaussianBlur(40))
    return Image.alpha_composite(Image.alpha_composite(img, g), s)


def neon_layer(draw_fn, color, width=4, blur=10):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d, color, width)
    glow = layer.filter(ImageFilter.GaussianBlur(blur))
    out = Image.alpha_composite(glow, glow)
    return Image.alpha_composite(out, layer)


def motif(img, kind, accent):
    cx, cy = 1210, 430
    rnd = random.Random(kind)
    if kind == "carte":
        def f(d, c, w):
            for i in range(9):
                pts = []
                for a in range(0, 361, 6):
                    rr = 70 + i * 30 + 18 * math.sin(math.radians(a * 3 + i * 40)) + 10 * math.cos(math.radians(a * 5))
                    pts.append((cx + rr * math.cos(math.radians(a)) * 1.25, cy + rr * math.sin(math.radians(a)) * 0.8))
                d.line(pts, fill=c + (150 if i % 2 else 230,), width=w if i % 3 == 0 else 2)
            d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=SUN + (255,), width=5)
            d.line([(cx, cy - 40), (cx, cy - 16)], fill=SUN + (255,), width=4)
        return Image.alpha_composite(img, neon_layer(f, accent, 3))
    if kind == "gameplay":
        def f(d, c, w):
            for i in range(6):
                x0, y0, R = 880 + i * 112, 420, 46
                pts = [(x0 + (R if k % 2 == 0 else R * 0.42) * math.cos(math.radians(-90 + k * 36)),
                        y0 + (R if k % 2 == 0 else R * 0.42) * math.sin(math.radians(-90 + k * 36))) for k in range(10)]
                if i < 4:
                    d.polygon(pts, fill=c + (235,))
                else:
                    d.line(pts + [pts[0]], fill=c + (230,), width=w)
        return Image.alpha_composite(img, neon_layer(f, accent, 5))
    if kind == "vehicules":
        def f(d, c, w):
            for i in range(16):
                y = 260 + i * 24 + rnd.randint(-6, 6)
                x1 = 760 + rnd.randint(0, 240)
                d.line([(x1, y), (x1 + rnd.randint(200, 640), y)], fill=(c if i % 3 else CYAN) + (rnd.randint(120, 240),), width=rnd.choice([2, 3, 5]))
        return Image.alpha_composite(img, neon_layer(f, accent, 4))
    if kind == "missions":
        def f(d, c, w):
            for i, R in enumerate([210, 165, 120]):
                d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=c + (230 - i * 40,), width=w + 2 - i)
            for a in range(0, 360, 10):
                r1, r2 = 210, 225 if a % 30 else 245
                d.line([(cx + r1 * math.cos(math.radians(a)), cy + r1 * math.sin(math.radians(a))),
                        (cx + r2 * math.cos(math.radians(a)), cy + r2 * math.sin(math.radians(a)))], fill=c + (220,), width=3)
            d.line([(cx, cy), (cx + 100 * math.cos(math.radians(-60)), cy + 100 * math.sin(math.radians(-60)))], fill=SUN + (255,), width=7)
            d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=SUN + (255,))
        return Image.alpha_composite(img, neon_layer(f, accent, 5))
    if kind == "online":
        def f(d, c, w):
            nodes = [(cx + 230 * math.cos(math.radians(a)) * rnd.uniform(.5, 1.1), cy + 170 * math.sin(math.radians(a)) * rnd.uniform(.5, 1.1)) for a in range(0, 360, 30)]
            nodes.append((cx, cy))
            for i, p in enumerate(nodes):
                for q in nodes[i + 1:]:
                    if math.dist(p, q) < 200:
                        d.line([p, q], fill=c + (140,), width=2)
            for p in nodes:
                d.ellipse([p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9], fill=CYAN + (255,))
        return Image.alpha_composite(img, neon_layer(f, accent, 3))
    # infos / actu / astuce : anneaux concentriques
    def f(d, c, w):
        for i in range(6):
            R = 60 + i * 42
            d.arc([cx - R, cy - R, cx + R, cy + R], start=200 + i * 25, end=200 + i * 25 + 220, fill=(c if i % 2 else CYAN) + (230,), width=w)
    return Image.alpha_composite(img, neon_layer(f, accent, 5))


def grain(img, amount=10):
    n = np.random.default_rng(7).normal(0, amount, (H, W, 1))
    arr = np.asarray(img.convert("RGB")).astype(np.float32) + n
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")


def text(img, badge, title_lines, subtitle, accent):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = 90
    fb = ImageFont.truetype(BOLD, 30)
    bw = d.textlength(badge, font=fb)
    d.rounded_rectangle([x, 120, x + bw + 44, 172], 26, fill=accent + (255,))
    d.text((x + 22, 128), badge, font=fb, fill=NIGHT + (255,))
    size = 118 if max(len(l) for l in title_lines) <= 13 else 96
    ft = ImageFont.truetype(BLACK, size)
    y = 210
    for line in title_lines:
        d.text((x, y), line, font=ft, fill=(255, 255, 255, 255))
        y += int(size * 1.02)
    fs = ImageFont.truetype(MED, 36)
    words, lines, cur = subtitle.split(), [], ""
    for w_ in words:
        if d.textlength((cur + " " + w_).strip(), font=fs) > 640:
            lines.append(cur); cur = w_
        else:
            cur = (cur + " " + w_).strip()
    lines.append(cur)
    y += 26
    for l in lines[:3]:
        d.text((x, y), l, font=fs, fill=(214, 203, 239, 255))
        y += 48
    fw = ImageFont.truetype(BLACK, 34)
    d.text((x, H - 92), "NÉOSOLUCE", font=fw, fill=(255, 255, 255, 255))
    wx = x + d.textlength("NÉOSOLUCE", font=fw) + 18
    d.line([(wx, H - 72), (wx + 60, H - 72)], fill=accent + (255,), width=4)
    d.text((wx + 76, H - 86), "GTA VI · GUIDE", font=ImageFont.truetype(BOLD, 24), fill=(214, 203, 239, 230))
    shadow = layer.filter(ImageFilter.GaussianBlur(18))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(shadow.getchannel("A").point(lambda v: int(v * .6)))
    return Image.alpha_composite(Image.alpha_composite(img, sh), layer)


def make(out, badge, title, subtitle, kind, accent_name="rose"):
    accent = ACCENTS.get(accent_name, PINK)
    img = background(accent)
    img = sunset(img, 1230, 560, 230)
    img = grid(img, PINK)
    img = motif(img, kind, accent if kind != "carte" else CYAN)
    # voile sombre à gauche pour la lisibilité du texte
    v = np.zeros((H, W, 4), dtype=np.uint8)
    v[..., :3] = NIGHT
    v[..., 3] = (np.clip(1 - np.linspace(0, 1, W) / 0.62, 0, 1) ** 1.4 * 200).astype(np.uint8)[None, :]
    img = Image.alpha_composite(img, Image.fromarray(v, "RGBA"))
    img = text(img, badge, title.split("|"), subtitle, accent)
    img = grain(img, 7)
    img.convert("RGB").save(out, quality=90, optimize=True, progressive=True)


if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else "rose")
    print("ok", sys.argv[1])
