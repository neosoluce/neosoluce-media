"""Visuels « épiques » NéoSoluce (illustrations IA / dessinées, jamais des images du jeu).

Usage :
  python3 tools/make_epic.py route    [fond.jpg] [--out visuels/2026-10-16-epic-route]
  python3 tools/make_epic.py montagne [fond.jpg] [--out visuels/2026-10-16-epic-montagne]
Sans fond.jpg, une illustration de secours est dessinée avec Pillow (sans texte ni logo).
Sortie : <out>.jpg (1080x1350, 4:5) et <out>-story.jpg (1080x1920).

Règles : aucun logo GTA/Rockstar, aucun personnage, police maison (Poppins/Inter),
noms en texte brut ajouté par nous, mention IA obligatoire en bas.
Le fond fourni (IA) doit être SANS texte ni logo ; le panneau vert reste vide.
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GF = "/usr/share/fonts/truetype/google-fonts/"
BOLD, MED = GF + "Poppins-Bold.ttf", GF + "Poppins-Medium.ttf"
NIGHT, PINK, CYAN, SUN = (15, 8, 38), (255, 61, 154), (45, 226, 230), (255, 209, 102)
MENTION = "Illustration NéoSoluce (IA) – pas une image du jeu"
LOGO = os.path.join(ROOT, "branding", "profil-logo.jpg")
F = lambda p, s: ImageFont.truetype(p, s)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(W, H, stops):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                d.line([(0, y), (W, y)], fill=lerp(c0, c1, (t - t0) / (t1 - t0))); break
    return im


def glow(im, layer_fn, blur=14, strength=1.0):
    g = Image.new("RGB", im.size, (0, 0, 0)); layer_fn(ImageDraw.Draw(g))
    g = g.filter(ImageFilter.GaussianBlur(blur))
    from PIL import ImageChops
    for _ in range(int(max(1, strength))):
        im.paste(ImageChops.screen(im, g))


def skyline(d, x0, x1, base, hmin, hmax, body, win, rnd, wc=None):
    x = x0
    while x < x1:
        w = rnd.randint(22, 52); h = rnd.randint(hmin, hmax)
        d.rectangle([x, base - h, x + w, base], fill=body)
        if win:
            for yy in range(base - h + 8, base - 6, 14):
                for xx in range(x + 5, x + w - 5, 10):
                    if rnd.random() < 0.55:
                        d.rectangle([xx, yy, xx + 3, yy + 5], fill=win if wc is None else rnd.choice(wc))
        x += w + rnd.randint(0, 6)


def palm(d, x, y, h, col):
    top = (x + h * 0.15, y - h)
    d.line([(x, y), top], fill=col, width=max(3, h // 14))
    for a in range(-60, 241, 38):
        r = h * 0.45
        ex = top[0] + r * math.cos(math.radians(a)); ey = top[1] + r * 0.6 * math.sin(math.radians(a)) + r * 0.25
        d.line([top, (ex, ey)], fill=col, width=max(3, h // 22))


def bg_route(W, H):
    rnd = random.Random(7)
    im = vgrad(W, H, [(0, (8, 6, 30)), (0.28, (40, 16, 80)), (0.36, (120, 30, 110)), (0.37, (18, 12, 40)), (1, (10, 8, 24))])
    d = ImageDraw.Draw(im); hz = int(H * 0.36); fx, fy = W // 2, int(H * 0.66)
    for _ in range(90):
        d.point((rnd.randint(0, W), rnd.randint(0, int(H * 0.25))), fill=(255, 255, 255))
    # villes
    skyline(d, 0, int(W * .46), hz, 30, 120, (24, 18, 40), (255, 170, 60), rnd)
    skyline(d, int(W * .54), W, hz, 50, 220, (30, 14, 60), CYAN, rnd, wc=[CYAN, PINK, (200, 120, 255)])
    for x in range(int(W * .58), W, 70):
        palm(d, x + rnd.randint(-10, 10), hz + 18, 46, (12, 6, 30))
    # mer + yachts à droite
    d.polygon([(int(W * .62), hz), (W, hz), (W, int(H * .75)), (int(W * .80), int(H * .60))], fill=(40, 20, 90))
    for i, (x, y) in enumerate([(0.80, 0.50), (0.88, 0.56), (0.74, 0.46), (0.92, 0.66)]):
        X, Y = int(W * x), int(H * y)
        d.polygon([(X - 24, Y), (X + 24, Y), (X + 16, Y + 8), (X - 18, Y + 8)], fill=(235, 235, 245))
        d.rectangle([X - 10, Y - 8, X + 8, Y], fill=(200, 200, 225))
    # routes
    road = (34, 32, 50)
    d.polygon([(int(W * .22), H), (int(W * .78), H), (int(W * .56), fy), (int(W * .44), fy)], fill=road)
    d.polygon([(int(W * .44), fy), (int(W * .50), fy), (int(W * .20), hz + 12), (int(W * .12), hz + 12)], fill=road)
    d.polygon([(int(W * .50), fy), (int(W * .56), fy), (int(W * .88), hz + 12), (int(W * .80), hz + 12)], fill=road)
    def trails(d):
        for k, c in enumerate([(255, 170, 60), (255, 70, 70), (255, 255, 255), CYAN, PINK]):
            o = (k - 2) * 0.055
            d.line([(int(W * (.5 + o * 3.2)), H), (fx + o * 90, fy)], fill=c, width=5)
            d.line([(fx + o * 90 - 25, fy), (int(W * .16 + o * 100), hz + 14)], fill=c, width=4)
            d.line([(fx + o * 90 + 25, fy), (int(W * .84 + o * 100), hz + 14)], fill=c, width=4)
    glow(im, trails, 9, 2); d = ImageDraw.Draw(im); trails(d)
    # portique vert VIDE
    sw, sh, sy = int(W * .74), int(H * .15), int(H * .40)
    sx = (W - sw) // 2
    d.rectangle([sx + 40, sy + sh, sx + 56, int(H * .62)], fill=(60, 60, 70))
    d.rectangle([sx + sw - 56, sy + sh, sx + sw - 40, int(H * .62)], fill=(60, 60, 70))
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], 14, fill=(8, 100, 56), outline=(235, 235, 235), width=6)
    return im, (sx, sy, sw, sh)


def bg_montagne(W, H):
    rnd = random.Random(3)
    im = vgrad(W, H, [(0, (60, 20, 110)), (0.22, (255, 61, 154)), (0.34, (255, 170, 90)), (0.6, (200, 160, 110)), (1, (110, 80, 60))])
    d = ImageDraw.Draw(im)
    tiers = [0.80, 0.62, 0.45, 0.27]
    # soleil
    d.ellipse([W * .42, H * .13, W * .62, H * .13 + W * .20], fill=SUN)
    # montagne
    mt = [(-40, H), (int(W * .30), int(H * .55)), (int(W * .46), int(H * .33)), (int(W * .52), int(H * .24)), (int(W * .60), int(H * .34)), (int(W * .78), int(H * .58)), (W + 40, H)]
    d.polygon(mt, fill=(70, 50, 62))
    d.polygon([(int(W * .52), int(H * .24)), (int(W * .60), int(H * .34)), (int(W * .78), int(H * .58)), (W + 40, H), (int(W * .6), H)], fill=(52, 36, 50))
    # sommet : ville néon + plage
    y4 = int(H * .27)
    d.rectangle([int(W * .36), y4 + 10, int(W * .70), y4 + 26], fill=(60, 30, 110))
    skyline(d, int(W * .40), int(W * .66), y4 + 10, 30, 90, (60, 20, 100), CYAN, rnd, wc=[CYAN, PINK])
    d.ellipse([int(W * .66), y4 + 8, int(W * .92), y4 + 42], fill=(255, 190, 140))  # plage
    d.arc([int(W * .70), y4 + 20, int(W * .96), y4 + 56], 0, 180, fill=(255, 255, 255), width=3)
    for x in (0.38, 0.69): palm(d, int(W * x), y4 + 12, 38, (30, 8, 60))
    # étage 3 : LA + colline
    y3 = int(H * .45)
    d.rectangle([int(W * .22), y3, int(W * .80), y3 + 16], fill=(120, 80, 70))
    skyline(d, int(W * .26), int(W * .62), y3, 20, 70, (140, 90, 70), (255, 209, 102), rnd)
    d.polygon([(int(W * .62), y3), (int(W * .72), y3 - 50), (int(W * .80), y3)], fill=(150, 105, 70))
    for x in (0.64, 0.70): palm(d, int(W * x), y3, 32, (60, 40, 30))
    # étage 2 : ville grise + pont
    y2 = int(H * .62)
    d.rectangle([int(W * .12), y2, int(W * .88), y2 + 16], fill=(90, 92, 100))
    skyline(d, int(W * .14), int(W * .52), y2, 40, 130, (96, 100, 112), (200, 200, 210), rnd)
    bx0, bx1 = int(W * .56), int(W * .90)
    for tx in (bx0 + 40, bx1 - 40):
        d.rectangle([tx - 6, y2 - 110, tx + 6, y2 + 10], fill=(70, 72, 82))
    d.line([(bx0, y2 - 6), (bx1, y2 - 6)], fill=(70, 72, 82), width=7)
    for tx in (bx0 + 40, bx1 - 40):
        for s in (-1, 1):
            d.line([(tx, y2 - 106), (tx + s * 110, y2 - 6)], fill=(70, 72, 82), width=2)
    # étage 1 : ville poussiéreuse années 90
    y1 = int(H * .80)
    d.rectangle([0, y1, W, y1 + 26], fill=(150, 112, 80))
    x = 20
    while x < W - 40:
        w, h = rnd.randint(40, 80), rnd.randint(24, 55)
        d.rectangle([x, y1 - h, x + w, y1], fill=rnd.choice([(170, 120, 85), (190, 150, 105), (140, 100, 78)]))
        d.polygon([(x - 4, y1 - h), (x + w + 4, y1 - h), (x + w // 2, y1 - h - 14)], fill=(120, 70, 55)); x += w + 18
    for x in range(60, W, 190): palm(d, x, y1, 60, (70, 55, 35))
    # route en lacets
    pts = [(int(W * .22), int(H * .90)), (int(W * .78), int(H * .88)), (int(W * .26), int(H * .74)), (int(W * .72), int(H * .64)),
           (int(W * .34), int(H * .53)), (int(W * .68), int(H * .45)), (int(W * .44), int(H * .35)), (int(W * .54), int(H * .30))]
    def road(d, col, w):
        d.line(pts, fill=col, width=w, joint="curve")
    road(d, (30, 24, 34), 22); road(d, (255, 220, 140), 3)
    return im, None


def cover(im, W, H):
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def text_c(d, cx, cy, s, font, fill, stroke=0):
    w = d.textlength(s, font=font)
    d.text((cx - w / 2, cy), s, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def arrow(d, x, y, w, h, left, col):
    t = h // 2
    if left:
        d.polygon([(x, y + t), (x + w * .4, y), (x + w * .4, y + h * .3), (x + w, y + h * .3), (x + w, y + h * .7), (x + w * .4, y + h * .7), (x + w * .4, y + h)], fill=col)
    else:
        d.polygon([(x + w, y + t), (x + w * .6, y), (x + w * .6, y + h * .3), (x, y + h * .3), (x, y + h * .7), (x + w * .6, y + h * .7), (x + w * .6, y + h)], fill=col)


def finish(im, W, H, top=None, bottom=None):
    d = ImageDraw.Draw(im, "RGBA")
    pad = int(H * 0.05)
    # voile haut/bas pour la lisibilité
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i in range(260):
        od.line([(0, i), (W, i)], fill=(15, 8, 38, int(200 * (1 - i / 260))))
        od.line([(0, H - 1 - i), (W, H - 1 - i)], fill=(15, 8, 38, int(220 * (1 - i / 260))))
    im.paste(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")); d = ImageDraw.Draw(im, "RGBA")
    if top:
        text_c(d, W / 2, int(H * .045), top[0], F(BOLD, 64), (255, 255, 255), 3)
        if len(top) > 1: text_c(d, W / 2, int(H * .045) + 80, top[1], F(MED, 34), SUN)
    if bottom:
        text_c(d, W / 2, H - pad - 175 + 20, bottom, F(BOLD, 46), (255, 255, 255), 3)
    # signature NéoSoluce + logo
    sig = F(BOLD, 30); x = 40
    if os.path.exists(LOGO):
        lg = Image.open(LOGO).convert("RGB").resize((64, 64), Image.LANCZOS)
        m = Image.new("L", (64, 64), 0); ImageDraw.Draw(m).ellipse([0, 0, 63, 63], fill=255)
        im.paste(lg, (40, H - 130), m); x = 116
    d.text((x, H - 120), "NÉOSOLUCE", font=sig, fill=(255, 255, 255))
    d.text((x, H - 84), "neosoluce.com", font=F(MED, 22), fill=(214, 203, 239))
    text_c(d, W / 2, H - 42, MENTION, F(MED, 22), (230, 224, 245, 235))


def make(scene, bgfile, out):
    for (W, H, suffix) in ((1080, 1350, ""), (1080, 1920, "-story")):
        if bgfile:
            im = cover(Image.open(bgfile).convert("RGB"), W, H)
            if scene == "route":  # panneau : zone approximative du panneau vide dans les fonds IA
                sign = (int(W * .13), int(H * .40), int(W * .74), int(H * .15))
            else: sign = None
        else:
            im, sign = (bg_route if scene == "route" else bg_montagne)(W, H)
        if scene == "route":
            sx, sy, sw, sh = sign; d = ImageDraw.Draw(im)
            f = F(BOLD, int(sh * .17)); cy = sy + sh * .2
            gap = int(sw * .04); half = sw // 2
            text_c(d, sx + half * .5, cy, "LOS SANTOS", f, (255, 255, 255))
            text_c(d, sx + half * 1.5, cy, "VICE CITY", f, (255, 255, 255))
            ah = int(sh * .26); aw = int(sw * .12)
            arrow(d, sx + gap + 6, sy + sh - ah - 14, aw, ah, True, (255, 255, 255))
            arrow(d, sx + sw - gap - aw - 6, sy + sh - ah - 14, aw, ah, False, (255, 255, 255))
            finish(im, W, H, top=("13 ANS PLUS TARD…", "Deux villes. Une seule route."), bottom="LA ROUTE MÈNE À LEONIDA")
        else:
            d = ImageDraw.Draw(im, "RGBA")
            labels = [("SAN ANDREAS · 2004", .80), ("GTA IV · 2008", .62), ("GTA V · 2013", .45), ("GTA VI · 19.11.2026", .27)]
            f = F(BOLD, 34)
            for i, (t, fy) in enumerate(labels):
                w = d.textlength(t, font=f) + 44; y = int(H * fy) - 120 - (0 if i < 3 else 0)
                y = int(H * fy) - 150 if i == 0 else int(H * fy) - 62
                x = 40 if i % 2 == 0 else W - 40 - w
                col = SUN if i == 3 else (255, 255, 255)
                d.rounded_rectangle([x, y, x + w, y + 56], 28, fill=(15, 8, 38, 215), outline=PINK if i == 3 else CYAN, width=3)
                d.text((x + 22, y + 6), t, font=f, fill=col)
            finish(im, W, H, top=("À TRAVERS LES ÉPOQUES", "Quelle ville t'a le plus marqué ?"), bottom="LE SOMMET : 19 NOVEMBRE 2026")
        p = os.path.join(ROOT, out + suffix + ".jpg"); os.makedirs(os.path.dirname(p), exist_ok=True)
        im.save(p, quality=92); print(p)


if __name__ == "__main__":
    a = sys.argv[1:]
    scene = a[0]; out = f"visuels/2026-10-16-epic-{'route' if scene == 'route' else 'montagne'}"
    bg = None
    i = 1
    while i < len(a):
        if a[i] == "--out": out = a[i + 1]; i += 2
        else: bg = a[i]; i += 1
    if bg is None:  # illustration de secours dessinée en code : pas d'IA
        MENTION = "Illustration NéoSoluce – pas une image du jeu"
    make(scene, bg, out)
