"""Pack « branding réseaux » NéoSoluce -> branding/
Usage : python3 tools/make_branding.py
"""
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_logo as ml  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "branding")
OFF = os.path.join(ROOT, "officiel")
os.makedirs(OUT, exist_ok=True)

BLACK = ml.find("InterDisplay-Black.otf")
BOLD = ml.find("InterDisplay-Bold.otf")

NIGHT = (15, 8, 38)
VIOLET = (26, 11, 61)
PINK = (255, 61, 154)
CYAN = (45, 226, 230)
SUN = (255, 209, 102)
WHITE = (255, 255, 255)
CREDIT = "Image officielle © Rockstar Games"


def F(path, size):
    return ImageFont.truetype(path, size)


def cover(img, w, h, cx=0.5, cy=0.5, zoom=1.0):
    """Resize+crop img to w x h, centred on relative point (cx, cy)."""
    s = max(w / img.width, h / img.height) * zoom
    im = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = min(max(0, round(im.width * cx - w / 2)), im.width - w)
    y = min(max(0, round(im.height * cy - h / 2)), im.height - h)
    return im.crop((x, y, x + w, y + h))


def vgrad(w, h, stops):
    """Vertical gradient; stops = [(t, (r,g,b,a)), ...]."""
    g = Image.new("RGBA", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                k = (t - t0) / max(1e-6, t1 - t0)
                g.putpixel((0, y), tuple(round(c0[i] + (c1[i] - c0[i]) * k) for i in range(4)))
                break
    return g.resize((w, h))


def hgrad(w, h, stops):
    return vgrad(h, w, stops).rotate(90, expand=True).transpose(Image.FLIP_TOP_BOTTOM)


def radial(w, h, center, radius, color, alpha=255):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse([center[0] - radius, center[1] - radius,
                               center[0] + radius, center[1] + radius], fill=alpha)
    m = m.filter(ImageFilter.GaussianBlur(radius * 0.45))
    lay = Image.new("RGBA", (w, h), color + (0,))
    lay.putalpha(m)
    return lay


def shadow_text(base, xy, text, font, fill, shadow=8, anchor="la", stroke=0):
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text(xy, text, font=font, fill=(0, 0, 0, 230), anchor=anchor, stroke_width=stroke + 2,
           stroke_fill=(0, 0, 0, 230))
    lay = lay.filter(ImageFilter.GaussianBlur(shadow))
    base.alpha_composite(lay)
    base.alpha_composite(lay)
    ImageDraw.Draw(base).text(xy, text, font=font, fill=fill + (255,) if len(fill) == 3 else fill,
                              anchor=anchor)


def neon_text(size, xy, text, font, color, anchor="mm"):
    lay = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).text(xy, text, font=font, fill=color + (255,), anchor=anchor)
    return ml.neon(lay, color)


def neon_bg(w, h):
    bg = Image.new("RGBA", (w, h), NIGHT + (255,))
    bg.alpha_composite(vgrad(w, h, [(0, VIOLET + (255,)), (0.55, NIGHT + (255,)), (1, (60, 10, 70, 255))]))
    return bg


def save(img, name):
    p = os.path.join(OUT, name)
    img.convert("RGB").save(p, quality=92, optimize=True)
    print("ok", name, img.size)


# ---------------------------------------------------------------- 1. Facebook
def facebook():
    W, H = 1640, 624
    src = Image.open(os.path.join(OFF, "Jason_and_Lucia_09.jpg")).convert("RGB")
    # duo pushed to the right half of the safe zone
    img = cover(src, W, H, cx=0.46, cy=0.42, zoom=1.08).convert("RGBA")
    img.alpha_composite(hgrad(W, H, [(0, NIGHT + (250,)), (0.30, NIGHT + (225,)),
                                     (0.52, NIGHT + (120,)), (0.70, NIGHT + (0,)), (1, NIGHT + (40,))]))
    img.alpha_composite(vgrad(W, H, [(0, NIGHT + (60,)), (0.6, NIGHT + (0,)), (1, NIGHT + (150,))]))
    d = ImageDraw.Draw(img)
    x0 = 250  # inside central 1200x500 safe zone (x 220..1420, y 62..562)
    # brand tag
    tag = F(BOLD, 30)
    d.rounded_rectangle([x0, 112, x0 + 196, 158], radius=23, fill=PINK + (255,))
    d.text((x0 + 98, 135), "NÉOSOLUCE", font=tag, fill=WHITE, anchor="mm")
    # title (2 lines)
    ft = F(BLACK, 68)
    shadow_text(img, (x0, 185), "Toutes les infos", ft, WHITE)
    shadow_text(img, (x0, 262), "GTA 6 en français", ft, SUN)
    # pink underline
    ImageDraw.Draw(img).rectangle([x0, 352, x0 + 120, 358], fill=PINK + (255,))
    fs = F(BOLD, 34)
    shadow_text(img, (x0, 378), "Guides · Astuces · Actus · Chaque jour", fs, WHITE, shadow=6)
    fu = F(BLACK, 38)
    shadow_text(img, (x0, 440), "neosoluce.com", fu, CYAN, shadow=6)
    fc = F(BOLD, 20)
    shadow_text(img, (1405, 545), CREDIT, fc, (235, 235, 235), shadow=4, anchor="rs")
    save(img, "facebook-couverture.jpg")


# ---------------------------------------------------------------- 2. Profils
def circle_mask(size, inset=0):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse([inset, inset, size - 1 - inset, size - 1 - inset], fill=255)
    return m


def profil_leona():
    S = 1080
    bg = Image.new("RGBA", (S, S))
    bg.alpha_composite(vgrad(S, S, [(0, (255, 61, 154, 255)), (0.5, (110, 20, 140, 255)), (1, VIOLET + (255,))]))
    bg.alpha_composite(radial(S, S, (S // 2, S // 2), 520, (255, 140, 200), 200))
    # portrait disc
    leona = Image.open(os.path.join(ROOT, "mascotte/references/leona-police.png")).convert("RGB")
    # head + shoulders : x 130..1230, y 170..1270 in the 1296x2304 original
    crop = leona.crop((120, 170, 1230, 1280)).resize((800, 800), Image.LANCZOS).convert("RGBA")
    crop.putalpha(circle_mask(800))
    ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([140 - 6, 140 - 6, 940 + 6, 940 + 6], outline=PINK + (255,), width=14)
    bg.alpha_composite(ml.glow(ring, 26, 3))
    bg.alpha_composite(crop, (140, 140))
    bg.alpha_composite(ml.neon(ring, PINK))
    ring2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(ring2).ellipse([108, 108, 972, 972], outline=CYAN + (255,), width=5)
    bg.alpha_composite(ml.neon(ring2, CYAN))
    save(bg, "profil-leona.jpg")


def profil_logo():
    S = 1080
    bg = neon_bg(S, S)
    bg.alpha_composite(radial(S, S, (S // 2, 470), 430, (120, 30, 150), 220))
    sun = ml.sun(300)
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    lay.alpha_composite(sun, ((S - 300) // 2, 200))
    bg.alpha_composite(ml.glow(lay, 22, 1))
    bg.alpha_composite(lay)
    bg.alpha_composite(neon_text((S, S), (S // 2, 650), "NÉO", F(BLACK, 170), PINK))
    bg.alpha_composite(neon_text((S, S), (S // 2, 800), "SOLUCE", F(BLACK, 130), CYAN))
    save(bg, "profil-logo.jpg")


# ---------------------------------------------------------------- 3. Highlights
def stroke_layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def icon_infos(d, c, col, w):
    cx, cy = c
    d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], outline=col, width=w)
    d.ellipse([cx - 17, cy - 78, cx + 17, cy - 44], fill=col)
    d.rounded_rectangle([cx - 15, cy - 22, cx + 15, cy + 80], radius=8, fill=col)


def icon_carte(d, c, col, w):
    cx, cy = c
    pts = [(cx - 140, cy - 80), (cx - 50, cy - 110), (cx + 50, cy - 80), (cx + 140, cy - 110),
           (cx + 140, cy + 90), (cx + 50, cy + 120), (cx - 50, cy + 90), (cx - 140, cy + 120)]
    d.line(pts + [pts[0]], fill=col, width=w, joint="curve")
    d.line([(cx - 50, cy - 110), (cx - 50, cy + 90)], fill=col, width=w - 4)
    d.line([(cx + 50, cy - 80), (cx + 50, cy + 120)], fill=col, width=w - 4)


def icon_pin(d, c, col, w):
    cx, cy = c
    r = 46
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    d.polygon([(cx - r * 0.86, cy + r * 0.5), (cx + r * 0.86, cy + r * 0.5), (cx, cy + r * 2.0)], fill=col)
    d.ellipse([cx - 17, cy - 17, cx + 17, cy + 17], fill=NIGHT + (255,))


def icon_persos(d, c, col, w):
    cx, cy = c
    for dx in (-80, 80):
        x = cx + dx
        d.ellipse([x - 38, cy - 128, x + 38, cy - 52], outline=col, width=w)
        d.arc([x - 62, cy - 30, x + 62, cy + 94], 180, 360, fill=col, width=w)
        d.line([(x - 62, cy + 32), (x + 62, cy + 32)], fill=col, width=w)


def icon_guides(d, c, col, w):
    cx, cy = c
    d.line([(cx, cy - 80), (cx - 40, cy - 100), (cx - 140, cy - 100), (cx - 140, cy + 90),
            (cx - 40, cy + 90), (cx, cy + 110)], fill=col, width=w, joint="curve")
    d.line([(cx, cy - 80), (cx + 40, cy - 100), (cx + 140, cy - 100), (cx + 140, cy + 90),
            (cx + 40, cy + 90), (cx, cy + 110)], fill=col, width=w, joint="curve")
    d.line([(cx, cy - 80), (cx, cy + 110)], fill=col, width=w - 4)
    for i in range(3):
        y = cy - 50 + i * 45
        d.line([(cx - 110, y), (cx - 35, y)], fill=col, width=8)
        d.line([(cx + 35, y), (cx + 110, y)], fill=col, width=8)


def icon_leona(d, c, col, w):
    """Stylised crocodile head in profile (snout to the left)."""
    cx, cy = c
    top = [(cx - 150, cy - 10), (cx - 140, cy - 40), (cx - 20, cy - 52), (cx + 20, cy - 95),
           (cx + 85, cy - 105), (cx + 135, cy - 70), (cx + 145, cy + 10)]
    d.line(top, fill=col, width=w, joint="curve")
    d.line([(cx + 145, cy + 10), (cx + 120, cy + 70), (cx - 150, cy + 30), (cx - 150, cy - 10)],
           fill=col, width=w, joint="curve")
    # mouth line + teeth
    d.line([(cx - 145, cy + 10), (cx + 90, cy + 25)], fill=col, width=8)
    for i in range(6):
        x = cx - 120 + i * 36
        y = cy + 10 + (x - (cx - 145)) * (15 / 235)
        d.polygon([(x - 9, y + 2), (x + 9, y + 2), (x, y + 24)], fill=col)
    # nostril, eye, lashes
    d.ellipse([cx - 135, cy - 40, cx - 115, cy - 24], fill=col)
    d.ellipse([cx + 45, cy - 82, cx + 95, cy - 38], outline=col, width=8)
    d.ellipse([cx + 63, cy - 70, cx + 81, cy - 50], fill=col)
    for k in range(3):
        a = math.radians(-150 + k * 35)
        d.line([(cx + 70 + 27 * math.cos(a), cy - 60 + 27 * math.sin(a)),
                (cx + 70 + 48 * math.cos(a), cy - 60 + 48 * math.sin(a))], fill=col, width=6)


def icon_quiz(d, c, col, w):
    cx, cy = c
    d.arc([cx - 75, cy - 130, cx + 75, cy + 20], 180, 405, fill=col, width=w + 4)
    a = math.radians(45)
    sx, sy = cx + 75 * math.cos(a), cy - 55 + 75 * math.sin(a)
    d.line([(sx, sy), (cx, cy + 25), (cx, cy + 55)], fill=col, width=w + 4, joint="curve")
    d.ellipse([cx - 20, cy + 85, cx + 20, cy + 125], fill=col)


HIGHLIGHTS = [
    ("infos", "INFOS", icon_infos, CYAN),
    ("carte", "CARTE", None, CYAN),
    ("persos", "PERSOS", icon_persos, PINK),
    ("guides", "GUIDES", icon_guides, SUN),
    ("leona", "LÉONA", icon_leona, PINK),
    ("quiz", "QUIZ", icon_quiz, SUN),
]


def highlight(slug, word, fn, col):
    W, H = 1080, 1920
    C = (540, 960)
    bg = neon_bg(W, H)
    bg.alpha_composite(radial(W, H, C, 420, (90, 20, 120), 255))
    disc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    dd.ellipse([C[0] - 290, C[1] - 290, C[0] + 290, C[1] + 290], fill=NIGHT + (200,))
    bg.alpha_composite(disc)
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([C[0] - 280, C[1] - 280, C[0] + 280, C[1] + 280], outline=col + (255,), width=8)
    bg.alpha_composite(ml.neon(ring, col))
    ic = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ic)
    icc = (C[0], C[1] - 55)
    if slug == "carte":
        icon_carte(d, (icc[0], icc[1] + 10), col + (255,), 14)
    else:
        fn(d, icc, col + (255,), 14)
    bg.alpha_composite(ml.neon(ic, col))
    if slug == "carte":
        pin = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        pc = (icc[0] + 40, icc[1] - 60)
        icon_pin(ImageDraw.Draw(pin), pc, PINK + (255,), 14)
        bg.alpha_composite(ml.glow(pin, 14, 2))
        bg.alpha_composite(pin)
        ImageDraw.Draw(bg).ellipse([pc[0] - 17, pc[1] - 17, pc[0] + 17, pc[1] + 17], fill=NIGHT + (255,))
    bg.alpha_composite(neon_text((W, H), (C[0], C[1] + 155), word, F(BLACK, 80), WHITE if col != SUN else SUN))
    save(bg, f"highlight-{slug}.jpg")


# ---------------------------------------------------------------- 4. Fonds d'écran
WALLS = [
    ("Jason_and_Lucia_13.jpg", 0.43, 0.5),
    ("Vice_City_08.jpg", 0.40, 0.5),
    ("Jason_and_Lucia_10.jpg", 0.40, 0.5),
]


def wallpaper(i, name, cx, cy):
    W, H = 1080, 1920
    src = Image.open(os.path.join(OFF, name)).convert("RGB")
    img = cover(src, W, H, cx=cx, cy=cy).convert("RGBA")
    img.alpha_composite(vgrad(W, H, [(0, NIGHT + (0,)), (0.70, NIGHT + (0,)), (0.80, NIGHT + (170,)),
                                     (1, NIGHT + (235,))]))
    # band: y 1500..1660 (above the story reply bar)
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rounded_rectangle([70, 1490, 1010, 1660], radius=36, fill=NIGHT + (215,), outline=PINK + (255,), width=4)
    img.alpha_composite(band)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 1540), "Fond d'écran GTA VI · enregistre-le", font=F(BOLD, 44), fill=WHITE, anchor="mm")
    img.alpha_composite(neon_text((W, H), (W // 2, 1612), "NÉOSOLUCE", F(BLACK, 62), PINK))
    shadow_text(img, (W // 2, 1705), CREDIT, F(BOLD, 28), (235, 235, 235), shadow=5, anchor="mm")
    save(img, f"banniere-story-fond-ecran-{i}.jpg")


if __name__ == "__main__":
    facebook()
    profil_leona()
    profil_logo()
    for h in HIGHLIGHTS:
        highlight(*h)
    for i, (n, cx, cy) in enumerate(WALLS, 1):
        wallpaper(i, n, cx, cy)
