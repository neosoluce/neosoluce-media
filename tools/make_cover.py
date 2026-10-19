"""Couvertures d'articles NéoSoluce (1600x900) : style « média tech », 100 % original.

Usage :
    python3 tools/make_cover.py covers/<slug>.jpg "BADGE" "Titre ligne 1|Titre ligne 2" "Sous-titre" <motif> [accent]

motif : carte | gameplay | vehicules | missions | online | infos | actu | astuce (ancien décor soleil)
  ou une scène thématique : voiture | arme | peninsule | manette | disque | ecran | globe | play | calendrier | editions | coffre | palmiers | boussole | etoiles
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


# ---------- Scènes thématiques (remplacent le soleil couchant) ----------
def _rr(d, box, r, **kw):
    d.rounded_rectangle(box, r, **kw)


def scene(img, kind, accent):
    """Illustration néon originale et générique, propre au sujet de l'article."""
    cx, cy = 1170, 450
    A, B = accent, (CYAN if accent != CYAN else PINK)
    def draw(f, color=None, width=5, blur=10, fit=(940, 1540, 450)):
        """fit=(x0, x1, cy) : recadre la scène dans la zone de droite (le texte reste à gauche)."""
        nonlocal img
        layer = neon_layer(f, color or A, width, blur)
        if fit:
            x0, x1, cyy = fit
            bb = layer.getbbox()
            if bb:
                crop = layer.crop(bb)
                k = min((x1 - x0) / crop.width, 520 / crop.height, 1.0)
                crop = crop.resize((int(crop.width * k), int(crop.height * k)), Image.LANCZOS)
                layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
                layer.paste(crop, (int(x0 + ((x1 - x0) - crop.width) / 2), int(cyy - crop.height / 2)))
        img = Image.alpha_composite(img, layer)
    if kind == "voiture":
        def f(d, c, w):
            body = [(700, 560), (730, 500), (860, 470), (960, 400), (1180, 385), (1300, 470), (1500, 500), (1540, 560)]
            d.line(body + [(700, 560)], fill=c + (255,), width=w + 1, joint="curve")
            d.line([(985, 470), (1030, 415), (1170, 410), (1240, 470), (985, 470)], fill=B + (230,), width=w - 1)
            for x in (870, 1380):
                d.ellipse([x - 62, 500, x + 62, 624], outline=c + (255,), width=w + 1)
                d.ellipse([x - 24, 538, x + 24, 586], outline=B + (230,), width=w - 1)
            for i in range(7):
                y = 410 + i * 28
                d.line([(520 - i * 12, y), (660 - i * 6, y)], fill=B + (150,), width=3)
        draw(f)
    elif kind == "arme":
        def f(d, c, w):
            for R in (190, 130, 70):
                d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=c + (230,), width=w)
            d.line([(cx - 250, cy), (cx - 40, cy)], fill=c + (255,), width=w)
            d.line([(cx + 40, cy), (cx + 250, cy)], fill=c + (255,), width=w)
            d.line([(cx, cy - 250), (cx, cy - 40)], fill=c + (255,), width=w)
            d.line([(cx, cy + 40), (cx, cy + 250)], fill=c + (255,), width=w)
            d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=B + (255,))
            for i in range(4):
                x = 760 + i * 46
                _rr(d, [x, 640, x + 26, 730], 6, outline=B + (230,), width=3)
                d.polygon([(x, 640), (x + 26, 640), (x + 13, 606)], outline=B + (230,), width=3)
        draw(f)
    elif kind == "peninsule":
        pts = [(1090, 190), (1210, 190), (1250, 250), (1235, 330), (1270, 410), (1300, 500), (1340, 590), (1330, 680), (1275, 700),
               (1235, 640), (1195, 560), (1160, 480), (1120, 420), (1070, 380), (950, 360), (880, 330), (950, 290), (1060, 270)]
        def f(d, c, w):
            d.polygon(pts, outline=c + (255,), width=w)
            for k, sc in enumerate((0.8, 0.6, 0.4)):
                q = [(1190 + (x - 1190) * sc, 440 + (y - 440) * sc) for x, y in pts]
                d.polygon(q, outline=(B if k % 2 == 0 else c) + (150,), width=2)
            d.ellipse([1210 - 16, 560 - 16, 1210 + 16, 560 + 16], outline=SUN + (255,), width=5)
            d.line([(1210, 560 - 18), (1210, 500)], fill=SUN + (255,), width=4)
            d.ellipse([1210 - 7, 492 - 7, 1210 + 7, 492 + 7], fill=SUN + (255,))
        draw(f)
    elif kind == "manette":
        def f(d, c, w):
            body = [(780, 410), (880, 350), (1160, 350), (1260, 350), (1540, 350), (1640 - 40, 410), (1610 - 40, 600), (1500, 640), (1400, 560), (1010, 560), (910, 640), (810, 600)]
            body = [(x - 150, y) for x, y in body]
            d.line(body + [body[0]], fill=c + (255,), width=w + 1, joint="curve")
            d.ellipse([740 + 40 - 150 + 150, 440, 740 + 100 - 150 + 150, 500], outline=B + (230,), width=w)
            # croix
            for dx, dy in ((0, -34), (0, 34), (-34, 0), (34, 0)):
                _rr(d, [800 + dx - 15, 470 + dy - 15, 800 + dx + 15, 470 + dy + 15], 5, outline=B + (230,), width=3)
            for dx, dy, col in ((0, -42, B), (0, 42, B), (-42, 0, B), (42, 0, B)):
                d.ellipse([1250 + dx - 17, 465 + dy - 17, 1250 + dx + 17, 465 + dy + 17], outline=col + (230,), width=3)
            d.ellipse([930 - 36, 540 - 36, 930 + 36, 540 + 36], outline=c + (230,), width=w)
            d.ellipse([1130 - 36, 540 - 36, 1130 + 36, 540 + 36], outline=c + (230,), width=w)
        draw(f)
    elif kind == "disque":
        def f(d, c, w):
            _rr(d, [820, 330, 1500, 600], 28, outline=c + (255,), width=w + 1)
            _rr(d, [860, 370, 1460, 560], 14, outline=B + (150,), width=2)
            for i in range(12):
                x = 880 + i * 48
                if i < 8:
                    _rr(d, [x, 440, x + 34, 520], 6, fill=(c if i % 3 else B) + (235,))
                else:
                    _rr(d, [x, 440, x + 34, 520], 6, outline=c + (160,), width=3)
            d.line([(880, 400), (1100, 400)], fill=B + (230,), width=w)
            d.ellipse([1440 - 8, 350 - 8, 1440 + 8, 350 + 8], fill=SUN + (255,))
            for i in range(6):
                d.line([(1500, 400 + i * 28), (1556, 400 + i * 28)], fill=c + (230,), width=4)
        draw(f)
    elif kind == "ecran":
        def f(d, c, w):
            _rr(d, [830, 250, 1510, 590], 22, outline=c + (255,), width=w + 1)
            _rr(d, [860, 280, 1480, 560], 10, outline=B + (140,), width=2)
            d.line([(1170, 590), (1170, 650)], fill=c + (255,), width=w)
            d.line([(1060, 655), (1280, 655)], fill=c + (255,), width=w + 1)
            for i in range(4):
                d.line([(900, 330 + i * 40), (900 + 300 - i * 50, 330 + i * 40)], fill=B + (220,), width=4)
            d.polygon([(1280, 380), (1280, 480), (1370, 430)], outline=SUN + (255,), width=4)
            _rr(d, [900, 690, 1440, 740], 10, outline=B + (200,), width=3)
        draw(f)
    elif kind == "globe":
        def f(d, c, w):
            R = 200
            d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=c + (255,), width=w)
            for k in (60, 130):
                d.ellipse([cx - k, cy - R, cx + k, cy + R], outline=B + (180,), width=2)
            for y in (-110, 0, 110):
                half = math.sqrt(R * R - y * y)
                d.line([(cx - half, cy + y), (cx + half, cy + y)], fill=B + (180,), width=2)
            for (a, b_) in ((-80, -90), (90, 40), (-30, 110), (20, -140)):
                x, y = cx + a, cy + b_
                d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=SUN + (255,))
                d.line([(x, y), (cx, cy)], fill=SUN + (110,), width=2)
        draw(f)
    elif kind == "play":
        def f(d, c, w):
            _rr(d, [800, 290, 1540, 650], 30, outline=c + (255,), width=w + 1)
            for i in range(10):
                x = 835 + i * 71
                _rr(d, [x, 305, x + 28, 325], 4, outline=B + (200,), width=2)
                _rr(d, [x, 615, x + 28, 635], 4, outline=B + (200,), width=2)
            d.polygon([(1100, 400), (1100, 540), (1230, 470)], fill=SUN + (245,))
            d.line([(840, 580), (1500, 580)], fill=B + (170,), width=3)
            d.line([(840, 580), (1180, 580)], fill=c + (255,), width=6)
        draw(f)
    elif kind == "calendrier":
        def f(d, c, w):
            _rr(d, [860, 260, 1380, 640], 26, outline=c + (255,), width=w + 1)
            d.line([(860, 350), (1380, 350)], fill=c + (255,), width=w)
            for x in (960, 1280):
                d.line([(x, 225), (x, 290)], fill=B + (255,), width=w + 2)
            for r in range(3):
                for k in range(5):
                    x, y = 905 + k * 90, 395 + r * 80
                    if (r, k) == (1, 3):
                        d.ellipse([x - 8, y - 8, x + 62, y + 62], outline=SUN + (255,), width=5)
                    else:
                        _rr(d, [x, y, x + 46, y + 46], 8, outline=B + (140,), width=2)
            cx2, cy2 = 1400, 590
            d.ellipse([cx2 - 100, cy2 - 100, cx2 + 100, cy2 + 100], outline=B + (255,), width=w)
            d.line([(cx2, cy2), (cx2, cy2 - 62)], fill=SUN + (255,), width=6)
            d.line([(cx2, cy2), (cx2 + 44, cy2 + 20)], fill=SUN + (255,), width=6)
        draw(f)
    elif kind == "editions":
        def f(d, c, w):
            for i, col in enumerate((B, c, SUN)):
                x, y = 880 + i * 130, 560 - i * 110
                _rr(d, [x, y - 230, x + 330, y + 90], 22, outline=col + (255,), width=w + 1)
                d.line([(x + 30, y - 160), (x + 200, y - 160)], fill=col + (200,), width=4)
                d.line([(x + 30, y - 120), (x + 150, y - 120)], fill=col + (140,), width=3)
            pts = [(1500 + (62 if k % 2 == 0 else 26) * math.cos(math.radians(-90 + k * 36)),
                    320 + (62 if k % 2 == 0 else 26) * math.sin(math.radians(-90 + k * 36))) for k in range(10)]
            d.polygon(pts, fill=SUN + (245,))
        draw(f)
    elif kind == "coffre":
        def f(d, c, w):
            for R, wd in ((240, w + 2), (190, w), (60, w)):
                d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=c + (255,), width=wd)
            for a in range(0, 360, 45):
                x2, y2 = cx + 170 * math.cos(math.radians(a)), cy + 170 * math.sin(math.radians(a))
                d.line([(cx, cy), (x2, y2)], fill=B + (230,), width=w - 1)
                d.ellipse([x2 - 10, y2 - 10, x2 + 10, y2 + 10], fill=B + (255,))
            for a in range(22, 360, 45):
                d.ellipse([cx + 215 * math.cos(math.radians(a)) - 7, cy + 215 * math.sin(math.radians(a)) - 7,
                           cx + 215 * math.cos(math.radians(a)) + 7, cy + 215 * math.sin(math.radians(a)) + 7], fill=SUN + (255,))
            d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=SUN + (255,))
        draw(f)
    elif kind == "palmiers":
        def f(d, c, w):
            def palm(x, y, h, lean):
                top = (x + lean, y - h)
                d.line([(x, y), (x + lean * 0.4, y - h * 0.55), top], fill=c + (255,), width=w + 1, joint="curve")
                for a in (-160, -125, -90, -55, -20, 15, 195):
                    L = 120 + (a % 40)
                    ex = top[0] + L * math.cos(math.radians(a))
                    ey = top[1] + L * math.sin(math.radians(a)) * 0.6 + 55
                    mx, my = (top[0] + ex) / 2, min(top[1], ey) - 38
                    d.line([top, (mx, my), (ex, ey)], fill=B + (240,), width=w - 1, joint="curve")
            palm(1130, 640, 330, -50)
            palm(1330, 640, 250, 60)
            palm(960, 640, 190, -30)
            for i in range(4):
                y = 665 + i * 22
                pts = [(700 + k * 20, y + 7 * math.sin(k * 0.7 + i)) for k in range(46)]
                d.line(pts, fill=(B if i % 2 else c) + (200 - i * 30,), width=3)
            # flamant stylisé
            fx, fy = 1470, 590
            d.line([(fx, fy), (fx, fy + 70)], fill=SUN + (255,), width=3)
            d.ellipse([fx - 40, fy - 24, fx + 30, fy + 16], outline=SUN + (255,), width=4)
            d.arc([fx + 6, fy - 100, fx + 56, fy - 10], start=270, end=90, fill=SUN + (255,), width=4)
            d.ellipse([fx + 40, fy - 104, fx + 56, fy - 90], outline=SUN + (255,), width=3)
        draw(f)
    elif kind == "boussole":
        def f(d, c, w):
            R = 210
            d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=c + (255,), width=w)
            d.ellipse([cx - R + 28, cy - R + 28, cx + R - 28, cy + R - 28], outline=B + (150,), width=2)
            for a in range(0, 360, 15):
                r1 = R - (34 if a % 90 == 0 else 20)
                d.line([(cx + r1 * math.cos(math.radians(a)), cy + r1 * math.sin(math.radians(a))),
                        (cx + (R - 6) * math.cos(math.radians(a)), cy + (R - 6) * math.sin(math.radians(a)))], fill=B + (220,), width=3)
            d.polygon([(cx, cy - 170), (cx + 34, cy), (cx, cy + 170), (cx - 34, cy)], outline=c + (255,), width=w)
            d.polygon([(cx, cy - 170), (cx + 34, cy), (cx - 34, cy)], fill=SUN + (235,))
            d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=B + (255,))
        draw(f)
    elif kind == "radio":
        def f(d, c, w):
            _rr(d, [820, 330, 1500, 620], 34, outline=c + (255,), width=w + 1)
            d.ellipse([870, 380, 1060, 570], outline=B + (255,), width=w)
            d.ellipse([920, 430, 1010, 520], outline=B + (160,), width=3)
            d.ellipse([958, 468, 972, 482], fill=SUN + (255,))
            for i in range(9):
                h = 40 + (i * 37) % 120
                x = 1110 + i * 42
                _rr(d, [x, 560 - h, x + 24, 560], 5, fill=(c if i % 2 else B) + (235,))
            d.line([(1120, 380), (1480, 380)], fill=c + (200,), width=3)
            d.arc([760, 270, 900, 410], start=200, end=290, fill=SUN + (255,), width=4)
            d.arc([720, 230, 940, 450], start=205, end=285, fill=SUN + (180,), width=3)
        draw(f)
    elif kind == "cartes":
        def f(d, c, w):
            for i, col in enumerate((B, c)):
                x = 900 + i * 330
                _rr(d, [x, 300, x + 290, 600], 24, outline=col + (255,), width=w + 1)
                d.ellipse([x + 85, 340, x + 205, 460], outline=col + (255,), width=w)
                d.ellipse([x + 120, 365, x + 170, 415], outline=col + (200,), width=3)
                d.arc([x + 105, 415, x + 185, 475], start=200, end=340, fill=col + (200,), width=3)
                for k in range(3):
                    d.line([(x + 40, 510 + k * 28), (x + 250 - k * 50, 510 + k * 28)], fill=col + (200,), width=4)
            pts = [(1500 + (44 if k % 2 == 0 else 18) * math.cos(math.radians(-90 + k * 36)),
                    270 + (44 if k % 2 == 0 else 18) * math.sin(math.radians(-90 + k * 36))) for k in range(10)]
            d.polygon(pts, fill=SUN + (245,))
        draw(f)
    elif kind == "etoiles":
        def f(d, c, w):
            for i in range(6):
                x0, y0, R = 850 + i * 112, 450, 48
                pts = [(x0 + (R if k % 2 == 0 else R * 0.42) * math.cos(math.radians(-90 + k * 36)),
                        y0 + (R if k % 2 == 0 else R * 0.42) * math.sin(math.radians(-90 + k * 36))) for k in range(10)]
                if i < 4:
                    d.polygon(pts, fill=c + (240,))
                else:
                    d.line(pts + [pts[0]], fill=c + (230,), width=w)
            d.line([(820, 560), (1530, 560)], fill=B + (200,), width=4)
            for i in range(9):
                x = 830 + i * 80
                d.line([(x, 590), (x + 36, 590)], fill=(B if i % 2 else c) + (220,), width=7)
        draw(f)
    return img


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


SCENES = {"voiture", "arme", "peninsule", "manette", "disque", "ecran", "globe", "play", "calendrier", "editions", "coffre", "palmiers", "boussole", "etoiles", "radio", "cartes"}


def make(out, badge, title, subtitle, kind, accent_name="rose"):
    accent = ACCENTS.get(accent_name, PINK)
    img = background(accent)
    if kind in SCENES:
        img = scene(img, kind, accent)
    else:
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
