"""Reel animé NéoSoluce (compte à rebours) : 1080x1920, 8 s, 30 i/s, musique synthwave originale.
Usage : python3 make_reel.py <jours restants, 0 = jour de sortie> sortie.mp4 [graine musique]
"""
import sys, os, math, wave, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_logo import sun, glow, neon, wordmark, find, NIGHT, PINK, CYAN, YELLOW, ORANGE

W, H, FPS, DUR = 1080, 1920, 30, 8.0
N = int(FPS * DUR)
HOR = 1180  # ligne d'horizon
BPM = 120
BEAT = 60 / BPM

BLACK_IT = find("InterDisplay-BlackItalic.otf")
BLACK = find("InterDisplay-Black.otf")
BOLD = find("InterDisplay-Bold.otf")
WHITE = (244, 238, 254)


def ease_out(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3


def back_out(x, s=1.9):
    x = min(max(x, 0), 1) - 1
    return x * x * ((s + 1) * x + s) + 1


def prog(t, a, b):
    return min(max((t - a) / (b - a), 0), 1)


# ---------- couches statiques ----------
def make_bg():
    a = np.zeros((H, W, 3), np.float32)
    top, mid, hz = np.array((10, 5, 28)), np.array((26, 11, 61)), np.array((92, 22, 90))
    for y in range(HOR):
        k = y / HOR
        c = top + (mid - top) * min(k * 1.6, 1) if k < 0.62 else mid + (hz - mid) * ((k - 0.62) / 0.38) ** 1.4
        a[y] = c
    a[HOR:] = (14, 6, 34)
    img = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(7)
    for _ in range(140):
        x, y = rng.integers(0, W), rng.integers(0, HOR - 300)
        r = rng.choice([1, 1, 1, 2])
        v = int(rng.integers(120, 255))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(v, v, 255, 255))
    return img


def text_img(txt, font, color, track=0):
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = sum(tmp.textlength(c, font=font) + track for c in txt) - track
    bb = font.getbbox(txt)
    pad = 80
    img = Image.new("RGBA", (int(w) + 2 * pad, bb[3] + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad
    for c in txt:
        d.text((x, pad), c, font=font, fill=color + (255,))
        x += d.textlength(c, font=font) + track
    return img


def neon_text(txt, font, color, track=0):
    return neon(text_img(txt, font, color, track), color)


def shadowed(txt, font, color):
    base = text_img(txt, font, color, track=6)
    sh = Image.new("RGBA", base.size, (8, 2, 22, 0))
    sh.putalpha(base.getchannel("A").filter(ImageFilter.GaussianBlur(22)).point(lambda v: min(255, int(v * 2.2))))
    return Image.alpha_composite(sh, neon(base, color))


def soft_glow(img, r=14):
    g = glow(img, r, 1)
    return Image.alpha_composite(g, img)


def with_alpha(img, a):
    if a >= 0.999:
        return img
    im = img.copy()
    al = im.getchannel("A").point(lambda v: int(v * a))
    im.putalpha(al)
    return im


def paste_center(canvas, img, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.01:
        return
    if abs(scale - 1) > 0.005:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    img = with_alpha(img, alpha)
    canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def palm(h, flip=False):
    """Silhouette de palmier stylisée (originale)."""
    S = Image.new("RGBA", (h, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(S)
    col = (8, 3, 22, 255)
    bx, by = int(h * 0.55), h
    tx, ty = int(h * 0.42), int(h * 0.22)
    pts = []
    for i in range(21):
        k = i / 20
        x = bx + (tx - bx) * k + math.sin(k * math.pi) * h * 0.06
        y = by + (ty - by) * k
        wdt = h * (0.035 - 0.018 * k)
        pts.append((x, y, wdt))
    left = [(x - w, y) for x, y, w in pts]
    right = [(x + w, y) for x, y, w in reversed(pts)]
    d.polygon(left + right, fill=col)
    for ang, ln in [(-160, 0.42), (-130, 0.38), (-95, 0.3), (-55, 0.4), (-20, 0.45), (15, 0.36), (170, 0.4)]:
        a = math.radians(ang)
        pts2 = []
        for i in range(13):
            k = i / 12
            x = tx + math.cos(a) * h * ln * k
            y = ty + math.sin(a) * h * ln * k + (h * 0.22 * k * k)
            pts2.append((x, y))
        for i in range(len(pts2) - 1):
            wdt = int(h * 0.03 * (1 - i / 12)) + 2
            d.line([pts2[i], pts2[i + 1]], fill=col, width=wdt)
    if flip:
        S = S.transpose(Image.FLIP_LEFT_RIGHT)
    return S


print("couches…")
BG = make_bg()
SUN_S = 760
SUN = sun(SUN_S)
SUN_L = Image.new("RGBA", (SUN_S + 200, SUN_S + 200), (0, 0, 0, 0))
SUN_L.alpha_composite(SUN, (100, 100))
SUN_L = Image.alpha_composite(glow(SUN_L, 40, 2), SUN_L)

PALM_L = palm(900)
PALM_R = palm(760, flip=True)

f_kick = ImageFont.truetype(BOLD, 46)
KICK = neon_text("COMPTE À REBOURS", f_kick, CYAN, track=10)
NUM = None  # rempli dans main
f_sub = ImageFont.truetype(BLACK, 88)
SUB = None
f_date = ImageFont.truetype(BOLD, 54)
DATE = None
LOGO = wordmark(0.55)
f_cta = ImageFont.truetype(BOLD, 46)
CTA = soft_glow(text_img("Tous les guides : lien en bio", f_cta, WHITE), 8)


def grid_layer(t):
    L = Image.new("RGBA", (W, H - HOR), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    vx = W / 2
    hh = H - HOR
    # lignes de fuite
    for i in range(-14, 15):
        x_bottom = vx + i * 150
        d.line([(vx + i * 6, 0), (x_bottom, hh)], fill=PINK + (200,), width=3)
    # lignes horizontales qui avancent
    speed = 0.55
    ph = (t * speed) % 1
    for j in range(14):
        y = hh * ((j + ph) / 13) ** 2.2
        if 0 <= y <= hh:
            a = int(90 + 165 * (y / hh))
            d.line([(0, y), (W, y)], fill=CYAN + (a,), width=2 + int(3 * y / hh))
    g = L.filter(ImageFilter.GaussianBlur(7))
    out = Image.alpha_composite(g, g)
    out = Image.alpha_composite(out, L)
    return out


def frame(i, num_img):
    t = i / FPS
    c = BG.copy()
    # soleil qui se lève
    rise = ease_out(prog(t, 0, 1.6))
    sy = HOR - SUN_S * 0.42 + (1 - rise) * 420
    # léger battement sur la musique après le drop
    pulse = 0
    if t > 1.0:
        bp = ((t - 1.0) % BEAT) / BEAT
        pulse = math.exp(-bp * 6)
    sun_l = SUN_L
    c.alpha_composite(sun_l, (int(W / 2 - sun_l.width / 2), int(sy - sun_l.height / 2)))
    # sol + grille (masque le bas du soleil)
    floor = Image.new("RGBA", (W, H - HOR), (14, 6, 34, 255))
    c.alpha_composite(floor, (0, HOR))
    c.alpha_composite(grid_layer(t), (0, HOR))
    # halo d'horizon
    hz = Image.new("RGBA", (W, 60), PINK + (0,))
    ImageDraw.Draw(hz).rectangle([0, 26, W, 34], fill=PINK + (255,))
    c.alpha_composite(glow(hz, 12, 2), (0, HOR - 30))
    # palmiers
    pin = ease_out(prog(t, 0.2, 1.4))
    c.alpha_composite(PALM_L, (int(-330 - (1 - pin) * 300), HOR - PALM_L.height + 60))
    c.alpha_composite(PALM_R, (int(W - PALM_R.width + 300 + (1 - pin) * 300), HOR - PALM_R.height + 60))
    # surtitre
    paste_center(c, KICK, W / 2, 300, alpha=ease_out(prog(t, 0.3, 0.8)))
    # chiffre : pop au drop (1.0 s) puis pulsation au tempo
    if t >= 0.95:
        k = prog(t, 0.95, 1.35)
        sc = 0.35 + 0.65 * back_out(k) + 0.035 * pulse
        al = 1.0
        if 1.35 < t < 1.75:  # scintillement néon
            al = 0.35 if int(t * 22) % 3 == 0 else 1.0
        paste_center(c, num_img, W / 2, 720, alpha=min(1, k * 3) * al, scale=sc)
    # sous-titre
    k = ease_out(prog(t, 1.8, 2.4))
    paste_center(c, SUB, W / 2, 985 + (1 - k) * 70, alpha=k)
    k = ease_out(prog(t, 2.4, 3.0))
    paste_center(c, DATE, W / 2, 1085 + (1 - k) * 50, alpha=k)
    # marque + appel à l'action
    k = ease_out(prog(t, 3.2, 3.8))
    paste_center(c, LOGO, W / 2, 1395, alpha=k, scale=0.95 + 0.05 * k)
    k = ease_out(prog(t, 4.2, 4.8))
    paste_center(c, CTA, W / 2, 1520 + (1 - k) * 30, alpha=k)
    # fondu de fin
    fo = prog(t, DUR - 0.4, DUR)
    if fo > 0:
        c.alpha_composite(Image.new("RGBA", (W, H), (5, 2, 15, int(255 * fo))))
    # fondu d'ouverture
    fi = 1 - prog(t, 0, 0.35)
    if fi > 0:
        c.alpha_composite(Image.new("RGBA", (W, H), (5, 2, 15, int(255 * fi))))
    return c.convert("RGB")


# ---------- musique synthwave originale ----------
SR = 44100


def note(n):  # n = demi-tons depuis La 440
    return 440 * 2 ** (n / 12)


def saw(f, t):
    return 2 * ((f * t) % 1) - 1


def lowpass(x, cutoff):
    a = 1 - math.exp(-2 * math.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def music():
    n = int(SR * DUR)
    out = np.zeros(n, np.float32)
    bar = 4 * BEAT
    # Am - F - C - G (demi-tons relatifs à La 440)
    chords = [(-12, -9, -5), (-16, -12, -9), (-21, -17, -14), (-14, -10, -7)]
    roots = [-36, -40, -33, -38]
    # nappe
    for b, ch in enumerate(chords):
        s, e = int(b * bar * SR), int((b + 1) * bar * SR)
        tt = np.arange(e - s) / SR
        env = np.minimum(tt / 0.25, 1) * np.minimum((bar - tt) / 0.15, 1)
        sig = np.zeros(e - s)
        for nn in ch:
            for det in (-0.08, 0.08):
                sig += saw(note(nn + det), tt)
        out[s:e] += 0.06 * sig * env
    out = lowpass(out, 1600).astype(np.float32)
    # riser avant le drop
    tt = np.arange(int(SR * 1.0)) / SR
    noise = np.random.default_rng(1).standard_normal(len(tt))
    out[: len(tt)] += 0.08 * noise * (tt / 1.0) ** 2
    # basse en croches à partir du drop
    bass = np.zeros(n, np.float32)
    step = BEAT / 2
    for k in range(int(DUR / step)):
        st = k * step
        if st < 1.0:
            continue
        b = int(st // bar) % 4
        f = note(roots[b] + (12 if k % 2 else 0))
        s = int(st * SR)
        L = int(step * SR * 0.9)
        tt = np.arange(L) / SR
        env = np.exp(-tt * 6)
        bass[s:s + L] += 0.35 * saw(f, tt) * env
    out += lowpass(bass, 700).astype(np.float32)
    # arpège en doubles croches à partir de la mesure 2
    arp = np.zeros(n, np.float32)
    step = BEAT / 4
    for k in range(int(DUR / step)):
        st = k * step
        if st < bar:
            continue
        b = int(st // bar) % 4
        ch = chords[b]
        nn = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24][k % 4]
        s = int(st * SR)
        L = int(step * SR)
        tt = np.arange(L) / SR
        sq = np.sign(np.sin(2 * np.pi * note(nn) * tt))
        arp[s:s + L] += 0.07 * sq * np.exp(-tt * 18)
    arp = lowpass(arp, 3000)
    d = int(SR * BEAT * 0.75)
    arp[d:] += 0.35 * arp[:-d]
    out += arp.astype(np.float32)
    # batterie
    rng = np.random.default_rng(3)
    for k in range(int(DUR / BEAT)):
        st = k * BEAT
        if st < 1.0:
            continue
        s = int(st * SR)
        L = int(0.35 * SR)
        tt = np.arange(L) / SR
        f = 45 + 120 * np.exp(-tt * 30)
        ph = 2 * np.pi * np.cumsum(f) / SR
        e = min(n, s + L)
        out[s:e] += (0.55 * np.sin(ph) * np.exp(-tt * 9))[: e - s]
        if k % 2 == 1:  # caisse claire
            L2 = int(0.25 * SR)
            tt2 = np.arange(L2) / SR
            sn = rng.standard_normal(L2) * np.exp(-tt2 * 14) * 0.22 + 0.12 * np.sin(2 * np.pi * 190 * tt2) * np.exp(-tt2 * 20)
            e = min(n, s + L2)
            out[s:e] += sn[: e - s]
        # charleston sur les contretemps
        s3 = int((st + BEAT / 2) * SR)
        L3 = int(0.05 * SR)
        if s3 + L3 <= n:
            hn = rng.standard_normal(L3)
            hn = hn - lowpass(hn, 6000)
            out[s3:s3 + L3] += 0.12 * hn * np.exp(-np.arange(L3) / SR * 60)
    # fondu final + normalisation
    fo = int(0.6 * SR)
    out[-fo:] *= np.linspace(1, 0, fo)
    out = np.tanh(out * 1.2)
    out /= np.max(np.abs(out)) / 0.89
    return out


def main():
    global SUB, DATE
    num = sys.argv[1] if len(sys.argv) > 1 else "38"
    sub, date = "JOURS AVANT GTA 6", "Sortie le 19 novembre 2026"
    if num == "1":
        sub, date = "JOUR AVANT GTA 6", "Sortie demain, 19 novembre"
    elif num == "0":
        num, sub, date = "J-0", "GTA 6 EST SORTI !", "Tous nos guides sur neosoluce.com"
    SUB = soft_glow(text_img(sub, f_sub, WHITE), 16)
    DATE = soft_glow(text_img(date, f_date, YELLOW), 10)
    dst = sys.argv[2] if len(sys.argv) > 2 else "reel.mp4"
    work = os.path.join(os.path.dirname(os.path.abspath(dst)), "_frames")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    f_num = ImageFont.truetype(BLACK_IT, 470 if len(num) <= 2 else 330)
    num_img = shadowed(num, f_num, PINK)
    print("musique…")
    # musique différente à chaque Reel : la graine dépend du jour (style, tempo, tonalité, grille)
    from music import make_music
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else (int(num) if num.isdigit() else 0)
    a, info = make_music(seed=seed, duration=DUR)
    print("musique :", info)
    wav = os.path.join(work, "music.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())
    print("images…")
    for i in range(N):
        frame(i, num_img).save(os.path.join(work, f"f{i:04d}.jpg"), quality=92)
        if i % 40 == 0:
            print(i, flush=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(work, "f%04d.jpg"),
                    "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dst], check=True)
    frame(int(2.6 * FPS), num_img).save(os.path.splitext(dst)[0] + "-apercu.jpg", quality=88)
    print("ok", dst)


if __name__ == "__main__":
    main()
