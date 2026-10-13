"""Reels DYNAMIQUES NéoSoluce (style comptes d'actu jeux vidéo) à partir des images et vidéos OFFICIELLES
de GTA VI publiées par Rockstar Games (dossier officiel/ du dépôt). Remplace le mode « reel » de make_official.py.

Usage :
    python3 tools/make_dynamic_reel.py cartes.json reels/AAAA-MM-JJ-<sujet>.mp4 [graine]

    - graine (entier, 11 par défaut) : choisit la musique originale (tools/music.py : style, tempo, tonalité)
      et l'ordre des effets. Change-la à chaque Reel.
    - Sortie : MP4 1080x1920, 30 i/s, H.264 yuv420p + AAC, faststart, 15 à 25 s.
    - Écrit aussi <sortie>-apercu.jpg : planche de 6 images réparties dans le temps. Regarde-la avec Read
      (texte non coupé, crédit lisible, visages dans le cadre), puis supprime-la (ne la commite pas).

Format de cartes.json : liste de 4 à 8 « plans », dans l'ordre du montage.
    Plan image :
        {"image": "officiel/<fichier>.jpg", "badge": "INFO", "titre": "...", "texte": "...",
         "x": 0.5, "y": 0.42, "cle": "mot clé"}
    Plan vidéo (clip officiel de officiel/videos/) :
        {"video": "officiel/videos/<fichier>.mp4", "x": 0.5, "debut": 0, "cadre": "remplir"|"entier",
         "largeur": 1, "badge": "...", "titre": "...", "texte": "..."}
    Écran de fin (facultatif, uniquement en DERNIER) :
        {"fin": true, "titre": "Tous les guides GTA 6", "texte": "neosoluce.com · Abonne-toi"}

    - Le PREMIER plan est l'accroche : son titre s'affiche en très gros, mot par mot.
    - "titre" : 40 caractères au maximum ; "texte" : 90 caractères au maximum ; "badge" : facultatif (court, ex. « OFFICIEL »).
    - "cle" (facultatif) : mot ou groupe de mots du titre à surligner (rose ou jaune). Par défaut : le premier
      mot qui contient un chiffre (avec « GTA » devant s'il y est), sinon le mot le plus long.
    - "x" / "y" (0 à 1) : centre du cadrage dans l'image source (0 = gauche/haut, 1 = droite/bas).
      Les images officielles sont en paysage : règle "x" pour garder les visages dans le cadre et vérifie l'aperçu.
    - Vidéo : "debut" = seconde de départ (clips longs) ; les clips très courts (portraits animés de 1,5 s) sont
      joués en aller-retour. "cadre": "entier" = vidéo entière sur fond flou (ex. jaquette : "largeur": 0.45,
      "debut": 16.5, jamais la fin avec « Pre-order now »).

Ce que fait le script :
    - Musique originale de tools/music.py (graine), fondu d'entrée et de sortie ; la durée de chaque plan est un
      nombre pair de temps (60/bpm) : toutes les coupes tombent sur les temps forts.
    - Mouvements de caméra variés (punch-in, panoramique, zoom arrière, poussée lente sur les vidéos), petite
      pulsation de zoom sur chaque temps, transitions alternées : flash blanc + secousse, « whip » (flou de
      mouvement horizontal), glitch RVB.
    - Titre qui apparaît mot par mot (pop avec rebond), mot clé surligné, texte secondaire qui glisse, encart
      néon en bas (au-dessus des 200 px réservés à l'interface TikTok), barre de progression, pastille NÉOSOLUCE.

Règles (voir agents/COMMUN.md, section Images officielles, et REELS.md) :
    - Uniquement des fichiers de officiel/ (jamais d'image trouvée ailleurs, jamais de trailer).
    - Crédit OBLIGATOIRE, ajouté automatiquement et visible en permanence sur chaque plan officiel :
      « Image officielle © Rockstar Games » ou « Vidéo officielle © Rockstar Games » (absent sur l'écran de fin).
    - Son d'origine des vidéos officielles TOUJOURS coupé : seule la musique originale est dans le Reel.
    - Usage de fan non commercial : jamais sponsorisé, boosté, en partenariat ni avec un lien d'achat.
    - Chaque fait écrit doit être vérifié et correspondre à ce qu'on voit ; aucun spoiler.
"""
import json, math, os, random, subprocess, sys, tempfile, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from make_logo import find, sun  # noqa: E402
from music import make_music, write_wav  # noqa: E402

W, H, FPS = 1080, 1920, 30
BLACK, BOLD = find("InterDisplay-Black.otf"), find("InterDisplay-Bold.otf")
PINK, CYAN, YEL, WHITE = (255, 61, 154), (45, 226, 230), (255, 209, 102), (255, 255, 255)
NIGHT, VIOLET = (15, 8, 38), (26, 11, 61)
SAFE_TOP, SAFE_BOTTOM = 150, 200          # zones réservées à l'interface TikTok/Instagram
PANEL_X0, PANEL_X1 = 40, 968              # encart : laisse libre la colonne de boutons à droite
TXT_X, TXT_MAXW = 78, 850
ZOOM_IMG, ZOOM_VID = 1.3, 1.2             # marge de préchargement (zoom max sans perte)
HZ = 1330                                 # horizon de l'écran de fin
CREDITS = {"image": "Image officielle © Rockstar Games", "video": "Vidéo officielle © Rockstar Games"}


def font(path, size, _c={}):
    k = (path, size)
    if k not in _c:
        _c[k] = ImageFont.truetype(path, size)
    return _c[k]


def path_of(p):
    return p if os.path.exists(p) else os.path.join(ROOT, p)


def ease_out(t, p=3):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** p


def ease_back(t, s=2.2):
    t = min(max(t, 0.0), 1.0) - 1
    return 1 + (s + 1) * t ** 3 + s * t ** 2


def paste(frame, rgba, xy, alpha=1.0):
    if alpha <= 0.01:
        return
    m = rgba.getchannel("A")
    if alpha < 0.99:
        m = m.point(lambda v: int(v * alpha))
    frame.paste(rgba, (int(xy[0]), int(xy[1])), m)


# ---------------------------------------------------------------- sources (préchargées une seule fois)

class Source:
    """Image ou vidéo préchargée à ~1,3x (1,2x pour les vidéos) la taille utile, recadrée par une caméra virtuelle."""

    def __init__(self, card, nframes):
        self.card = card
        self.kind = "video" if "video" in card else "image"
        self.cx, self.cy = float(card.get("x", 0.5)), float(card.get("y", 0.42))
        if self.kind == "image":
            im = Image.open(path_of(card["image"])).convert("RGB")
            s = max(W / im.width, H / im.height) * ZOOM_IMG
            self.frames = [im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)]
            self.zmax = ZOOM_IMG
        else:
            self.frames = self._video(card, nframes)
            self.cx = self.cy = 0.5               # recadrage horizontal déjà fait par ffmpeg
            self.zmax = ZOOM_VID
        self.pw, self.ph = self.frames[0].size
        self.sc = max(W / self.pw, H / self.ph)

    def _video(self, c, need):
        src = path_of(c["video"])
        vw, vh = round(W * ZOOM_VID), round(H * ZOOM_VID)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                                   capture_output=True, text=True, check=True).stdout.strip())
        debut = float(c.get("debut", 0))
        if debut >= dur - 0.2:
            debut = 0.0
        if c.get("cadre") == "entier":
            z = float(c.get("largeur", 1))
            fw = round(W * 0.84 * ZOOM_VID) // 2 * 2
            vf = (f"fps={FPS},crop=iw*{z}:ih,split[s1][s2];[s1]scale={vw}:{vh}:force_original_aspect_ratio=increase,"
                  f"crop={vw}:{vh},boxblur=30:2,eq=brightness=-0.25[bg];[s2]scale={fw}:-2[fg];"
                  f"[bg][fg]overlay=(W-w)/2:(H-h)/2-{round(150 * ZOOM_VID)}")
        else:
            x = min(max(float(c.get("x", 0.5)), 0), 1)
            vf = f"fps={FPS},scale={vw}:{vh}:force_original_aspect_ratio=increase,crop={vw}:{vh}:x=(iw-{vw})*{x}:y=(ih-{vh})/2"
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(debut), "-i", src, "-an", "-filter_complex", vf,
                            "-frames:v", str(need), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           capture_output=True, check=True)
        n = len(p.stdout) // (vw * vh * 3)
        if n == 0:
            raise RuntimeError(f"aucune image lue dans {src}")
        return [Image.frombuffer("RGB", (vw, vh), p.stdout[i * vw * vh * 3:(i + 1) * vw * vh * 3]) for i in range(n)]

    def frame(self, i):
        n = len(self.frames)
        if n == 1:
            return self.frames[0]
        cyc = 2 * n - 2                           # aller-retour si le clip est plus court que le plan
        j = i % cyc
        return self.frames[j if j < n else cyc - j]

    def view(self, i, z, dx, dy, shake=(0, 0)):
        """Vue 1080x1920 : zoom z (1 = plein cadre), décalage du centre dx/dy (fraction de la source)."""
        z = min(max(z, 1.0), self.zmax * 0.999)
        k = 1 / (self.sc * z)
        vw, vh = W * k, H * k
        x0 = (self.cx + dx) * self.pw - vw / 2 + shake[0] * k
        y0 = (self.cy + dy) * self.ph - vh / 2 + shake[1] * k
        x0 = min(max(x0, 0), self.pw - vw)
        y0 = min(max(y0, 0), self.ph - vh)
        return self.frame(i).transform((W, H), Image.AFFINE, (k, 0, x0, 0, k, y0), Image.BILINEAR)

    def pan_room(self, z):
        """Marge de panoramique horizontal disponible (fraction de la largeur source) autour du centre."""
        vw = W / (self.sc * z)
        left = self.cx * self.pw - vw / 2
        right = self.pw - (self.cx * self.pw + vw / 2)
        return max(left, 0) / self.pw, max(right, 0) / self.pw, vw / self.pw


def camera(move, src, u, sec, pulse):
    """Renvoie (zoom, dx) pour la position u (0..1) dans le plan, sec = secondes écoulées."""
    if move == "punch":                          # zoom avant rapide puis lent
        z = 1.0 + 0.17 * (1 - math.exp(-sec / 0.18)) + 0.08 * u
        dx = 0
    elif move == "zoomout":
        z = 1.27 - 0.24 * ease_out(u, 2)
        dx = 0
    elif move in ("pan_l", "pan_r"):
        z = 1.16
        left, right, vw = src.pan_room(z)
        span = min(0.16 * vw, left, right)
        d = 1 if move == "pan_r" else -1
        dx = d * (-span + 2 * span * (0.15 + 0.85 * u))
        z += 0.03 * u
    else:                                        # push : poussée lente (vidéos)
        z = 1.02 + 0.13 * ease_out(u, 2)
        dx = 0
    return z * (1 + 0.022 * pulse), dx


# ---------------------------------------------------------------- texte

def word_img(w, size, color, key=None):
    f = font(BLACK, size)
    asc, desc = f.getmetrics()
    tw = f.getlength(w)
    pad = max(10, size // 6)
    st = max(3, size // 22)
    im = Image.new("RGBA", (int(tw + 2 * pad + 2 * st), asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if key:                                      # mot clé : surligné
        d.rounded_rectangle([pad - size * 0.08, pad + asc * 0.14, pad + tw + size * 0.06 + 2 * st, pad + asc + desc * 0.3],
                            int(size * 0.14), fill=key + (255,))
        d.text((pad + st, pad), w, font=f, fill=NIGHT + (255,) if key == YEL else WHITE + (255,))
        return im
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((pad + st, pad + size // 18), w, font=f, fill=(0, 0, 0, 200), stroke_width=st, stroke_fill=(0, 0, 0, 200))
    sh = sh.filter(ImageFilter.GaussianBlur(size / 18))
    im.alpha_composite(sh)
    ImageDraw.Draw(im).text((pad + st, pad), w, font=f, fill=color + (255,), stroke_width=st, stroke_fill=NIGHT + (255,))
    return im


def wrap(words, size, maxw):
    f = font(BLACK, size)
    sp = f.getlength(" ")
    lines, cur, cw = [], [], 0
    for w in words:
        lw = f.getlength(w)
        if cur and cw + sp + lw > maxw:
            lines.append(cur); cur, cw = [], 0
        cw += (sp if cur else 0) + lw
        cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def keyword_idx(words, cle):
    if cle:
        ks = [k.lower() for k in cle.split()]
        for i in range(len(words)):
            if [w.lower().strip(",.!?:") for w in words[i:i + len(ks)]] == ks:
                return set(range(i, i + len(ks)))
    for i, w in enumerate(words):
        if any(ch.isdigit() for ch in w):
            s = {i}
            if i > 0 and words[i - 1].isupper() and len(words[i - 1]) > 1:
                s.add(i - 1)
            return s
    if not words:
        return set()
    return {max(range(len(words)), key=lambda i: len(words[i]))}


class Title:
    """Titre animé mot par mot (pop avec rebond). Positions relatives au coin haut-gauche du bloc."""

    def __init__(self, text, size, maxw, keycol, center=False, color=WHITE, cle=None):
        words = text.split()
        kidx = keyword_idx(words, cle)
        f = font(BLACK, size)
        sp = f.getlength(" ")
        self.items, self.lh = [], int(size * 1.13)
        i = 0
        lines = wrap(words, size, maxw)
        for li, line in enumerate(lines):
            lw = sum(f.getlength(w) for w in line) + sp * (len(line) - 1)
            x = (maxw - lw) / 2 if center else 0
            for w in line:
                im = word_img(w, size, color, keycol if i in kidx else None)
                pad = max(10, size // 6)
                self.items.append((im, x - pad, li * self.lh - pad))
                x += f.getlength(w) + sp
                i += 1
        self.h = self.lh * len(lines)

    def draw(self, frame, ox, oy, t, step):
        """t = images écoulées depuis le début de l'animation ; un mot toutes les `step` images."""
        for n, (im, x, y) in enumerate(self.items):
            k = t - n * step
            if k < 0:
                break
            s = 0.35 + 0.65 * ease_back(k / 7)
            a = min(1.0, k / 3 + 0.34)
            if abs(s - 1) > 0.01:
                sw, shh = max(1, int(im.width * s)), max(1, int(im.height * s))
                cx, cy = ox + x + im.width / 2, oy + y + im.height / 2
                paste(frame, im.resize((sw, shh), Image.BILINEAR), (cx - sw / 2, cy - shh / 2), a)
            else:
                paste(frame, im, (ox + x, oy + y), a)

    def duration(self, step):
        return (len(self.items) - 1) * step + 8


def text_block(text, size, color, maxw, center=False):
    f = font(BOLD, size)
    lines = wrap(text.split(), size, maxw) if text else []
    lh = int(size * 1.28)
    im = Image.new("RGBA", (maxw + 20, max(1, lh * len(lines) + 16)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = (maxw - f.getlength(" ".join(l))) / 2 if center else 0
        d.text((4 + x, 4 + i * lh), " ".join(l), font=f, fill=color + (255,), stroke_width=2, stroke_fill=NIGHT + (255,))
    return im


def pill(text, size, fg, bg, fnt=BLACK, padx=24, pady=10, outline=None):
    f = font(fnt, size)
    asc, desc = f.getmetrics()
    tw = f.getlength(text)
    im = Image.new("RGBA", (int(tw + 2 * padx) + 4, asc + desc + 2 * pady), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], im.height // 2, fill=bg, outline=outline, width=3 if outline else 0)
    d.text((padx + 2, pady), text, font=f, fill=fg)
    return im


# ---------------------------------------------------------------- calques fixes

def shade_layer():
    """Assombrit le haut (pastille, crédit) et le bas (encart) pour la lisibilité."""
    a = np.zeros(H, np.float32)
    y = np.arange(H)
    a += 150 * np.clip(1 - y / 380, 0, 1) ** 1.6
    a += 215 * np.clip((y - 880) / (H - 880), 0, 1) ** 1.25
    im = Image.new("RGBA", (W, H), NIGHT + (0,))
    im.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)[:, None].repeat(W, 1)))
    return im


def end_background():
    y = np.linspace(0, 1, H)[:, None]
    top, bot = np.array(NIGHT, np.float32), np.array(VIOLET, np.float32)
    g = top + (bot - top) * np.clip(y * 1.6, 0, 1)[..., None]
    g = np.repeat(g, W, 1)
    hz = HZ                                      # lueur de l'horizon
    glow = np.exp(-((np.arange(H) - hz) / 90.0) ** 2)[:, None, None] * np.array(PINK, np.float32) * 0.35
    return Image.fromarray(np.clip(g + glow, 0, 255).astype(np.uint8))


class Plan:
    def __init__(self, card, idx, n, keycol):
        self.card, self.idx = card, idx
        self.fin = bool(card.get("fin"))
        self.hook = idx == 0 and not self.fin
        self.keycol = keycol
        titre, texte = card.get("titre", ""), card.get("texte", "")
        cle = card.get("cle")
        if self.fin:
            self.title = Title(titre, 104, 900, keycol, center=True, cle=cle)
            self.sub = text_block(texte, 50, CYAN, 900, center=True)
            return
        badge = card.get("badge", "")
        self.badge = pill(badge.upper(), 36, NIGHT + (255,), CYAN + (255,), BOLD, 20, 8) if badge else None
        tsize = 0 if self.hook else 74
        self.sub = text_block(texte, 42 if not self.hook else 46, YEL if not self.hook else WHITE, TXT_MAXW)
        # encart : badge + (titre) + texte
        hb = (self.badge.height + 22) if self.badge else 0
        self.title = None if self.hook else Title(titre, tsize, TXT_MAXW, keycol, cle=cle)
        ht = (self.title.h + 14) if self.title else 0
        hs = self.sub.height if texte else 0
        ph = 34 + hb + ht + hs + 30
        self.panel_h = ph
        self.panel_y = H - SAFE_BOTTOM - ph
        self.offs = (34, 34 + hb, 34 + hb + ht)
        pw = PANEL_X1 - PANEL_X0
        bg = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(bg)
        d.rounded_rectangle([20, 20, pw + 19, ph + 19], 30, outline=PINK + (255,), width=10)
        bg = bg.filter(ImageFilter.GaussianBlur(9))  # halo néon
        d = ImageDraw.Draw(bg)
        d.rounded_rectangle([20, 20, pw + 19, ph + 19], 30, fill=NIGHT + (212,), outline=PINK + (255,), width=4)
        self.panel = bg
        if self.hook:                             # accroche : titre géant au-dessus de l'encart
            self.big = Title(titre, 128, 940, keycol, center=True, cle=cle)
            self.big_y = self.panel_y - 50 - self.big.h

    def draw_text(self, fr, t, step):
        """t = images depuis le début du plan."""
        if self.fin:
            ty = 640 - self.title.h // 2
            self.title.draw(fr, (W - 900) / 2, ty, t - 2, max(3, step))
            ts = t - 2 - self.title.duration(max(3, step))
            if ts >= 0:
                e = ease_out(ts / 9)
                paste(fr, self.sub, ((W - self.sub.width) / 2 + 3, ty + self.title.h + 36 + 60 * (1 - e)), e)
            return
        e = ease_out(t / 7)
        py = self.panel_y + 90 * (1 - e)
        paste(fr, self.panel, (PANEL_X0 - 20, py - 20), min(1, t / 4 + 0.15))
        if self.badge and t >= 2:
            s = 0.4 + 0.6 * ease_back((t - 2) / 6)
            b = self.badge if abs(s - 1) < 0.01 else self.badge.resize((max(1, int(self.badge.width * s)), max(1, int(self.badge.height * s))))
            paste(fr, b, (TXT_X - 4, py + self.offs[0] + (self.badge.height - b.height) / 2))
        if self.hook:
            self.big.draw(fr, (W - 940) / 2, self.big_y, t + 3, 3)
            ts = t - 3
        else:
            self.title.draw(fr, TXT_X, py + self.offs[1], t - 4, step)
            ts = t - 4 - self.title.duration(step) + 4
        if ts >= 0:
            e2 = ease_out(ts / 8)
            paste(fr, self.sub, (TXT_X - 120 * (1 - e2), py + self.offs[2]), e2)


# ---------------------------------------------------------------- effets de transition (sur l'image de fond)

def hblur(im, strength):
    if strength <= 0.02:
        return im
    f = 1 + 30 * strength
    small = im.resize((max(8, int(W / f)), H), Image.BOX)
    return Image.blend(im, small.resize((W, H), Image.BILINEAR), min(1, 0.4 + strength))


def whip(im, s, direction):
    """s de 0 à 1 : intensité ; décalage horizontal + flou de mouvement."""
    a = np.asarray(hblur(im, s))
    d = int(direction * s * 520)
    if d == 0:
        return Image.fromarray(a)
    out = np.empty_like(a)
    if d > 0:                                    # décalage avec bord étiré (pas de raccord visible)
        out[:, d:] = a[:, :-d]; out[:, :d] = a[:, :1]
    else:
        out[:, :d] = a[:, -d:]; out[:, d:] = a[:, -1:]
    return Image.fromarray(out)


def glitch(im, s, rng):
    a = np.asarray(im)
    out = a.copy()
    d = int(10 + 38 * s)
    out[:, :, 0] = np.roll(a[:, :, 0], d, 1)
    out[:, :, 2] = np.roll(a[:, :, 2], -d, 1)
    for _ in range(int(3 + 6 * s)):
        y = rng.randrange(0, H - 140)
        h = rng.randrange(14, 140)
        out[y:y + h] = np.roll(out[y:y + h], rng.choice([-1, 1]) * rng.randrange(30, 40 + int(160 * s)), 1)
    return Image.fromarray(out)


def flash(im, a):
    return Image.blend(im, Image.new("RGB", (W, H), WHITE), a) if a > 0 else im


# ---------------------------------------------------------------- montage

def plan_beats(cards, beat):
    """Durée de chaque plan en nombre PAIR de temps, total entre 15 et 25 s."""
    beats = []
    for i, c in enumerate(cards):
        target = 2.6 if c.get("fin") else (3.3 if i == 0 else 3.0)
        beats.append(max(2, int(round(target / beat / 2)) * 2))
    order = [i for i in range(len(cards)) if not cards[i].get("fin")]
    k = 0
    while sum(beats) * beat < 15.5:
        beats[order[k % len(order)]] += 2; k += 1
    while sum(beats) * beat > 24.5:
        i = max(order, key=lambda j: beats[j])
        if beats[i] <= 2:
            break
        beats[i] -= 2
    return beats


def render(cards_path, out, seed):
    t_start = time.time()
    cards = json.load(open(cards_path, encoding="utf-8"))
    assert 4 <= len(cards) <= 8, "cartes.json : 4 à 8 plans"
    for i, c in enumerate(cards):
        assert not c.get("fin") or i == len(cards) - 1, "l'écran de fin doit être le dernier plan"
        assert c.get("fin") or "image" in c or "video" in c, f"plan {i + 1} : « image », « video » ou « fin » requis"
        assert len(c.get("titre", "")) <= 40, f"plan {i + 1} : titre > 40 caractères"
        assert len(c.get("texte", "")) <= 90, f"plan {i + 1} : texte > 90 caractères"
        for k in ("image", "video"):
            if k in c:
                assert os.path.normpath(c[k]).startswith("officiel"), f"plan {i + 1} : uniquement des fichiers de officiel/"
                assert os.path.exists(path_of(c[k])), f"fichier introuvable : {c[k]}"
    rng = random.Random(seed)
    _, info = make_music(seed=seed, duration=1.0)
    bpm = info["bpm"]
    beat = 60 / bpm
    beats = plan_beats(cards, beat)
    cuts = [0]
    acc = 0
    for b in beats:
        acc += b
        cuts.append(int(round(acc * beat * FPS)))
    total = cuts[-1]
    dur = total / FPS
    tmp = tempfile.mkdtemp()
    audio, info = make_music(seed=seed, duration=dur)
    wav = os.path.join(tmp, "m.wav")
    write_wav(wav, audio)

    # mouvements et transitions variés
    moves_img = ["pan_r", "zoomout", "pan_l", "punch"]
    rng.shuffle(moves_img)
    moves, mi = [], 0
    for i, c in enumerate(cards):
        if c.get("fin"):
            moves.append(None)
        elif i == 0:
            moves.append("punch")
        elif "video" in c:
            moves.append("push" if i % 2 else "pan_r")
        else:
            moves.append(moves_img[mi % len(moves_img)]); mi += 1
    trans_cycle = ["whip", "flash", "glitch", "whip", "glitch", "flash"]
    off = rng.randrange(3)
    trans = [trans_cycle[(off + i) % len(trans_cycle)] for i in range(len(cards) - 1)]
    keycols = [PINK, YEL]
    plans = [Plan(c, i, len(cards), keycols[(i + seed) % 2]) for i, c in enumerate(cards)]
    step = min(6, max(3, int(round(beat / 2 * FPS))))   # un mot par demi-temps

    shade = shade_layer()
    pastille = pill("NÉOSOLUCE", 40, WHITE + (255,), NIGHT + (215,), BLACK, 26, 12, outline=PINK + (255,))
    credit_pills = {k: pill(v, 29, WHITE + (255,), (0, 0, 0, 175), BOLD, 18, 9) for k, v in CREDITS.items()}
    top_y = SAFE_TOP + 32
    endbg = end_background()
    sun_img = sun(560)
    sun_glow = Image.new("RGBA", (760, 760), (0, 0, 0, 0))
    sun_glow.alpha_composite(sun_img, (100, 100))
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(34))

    sources = {}

    def src(i):
        if i not in sources:
            sources[i] = Source(cards[i], cuts[i + 1] - cuts[i])
        for k in [k for k in sources if k < i - 1]:
            del sources[k]
        return sources[i]

    sheet_at = [int(total * (j + 0.55) / 6) for j in range(5)] + [total - 3]   # la dernière : fin du Reel
    for j, f in enumerate(sheet_at):          # évite les images de transition
        for c in cuts[1:-1]:
            if -4 <= f - c < 9:
                sheet_at[j] = min(total - 3, c + 12)
    shots = {}

    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a",
                            "-af", f"afade=t=in:d=0.3,afade=t=out:st={max(0, dur - 1.2):.3f}:d=1.2",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "12M", "-bufsize", "24M",
                            "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                            "-t", f"{dur:.3f}", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    grng = random.Random(seed * 7 + 1)
    for f in range(total):
        p = max(i for i in range(len(cards)) if cuts[i] <= f)
        t = f - cuts[p]
        n = cuts[p + 1] - cuts[p]
        u = t / max(1, n - 1)
        sec = t / FPS
        tb = (f / FPS) % beat
        pulse = math.exp(-tb / 0.09)
        plan = plans[p]
        # -- fond
        if plan.fin:
            fr = endbg.copy()
            d = ImageDraw.Draw(fr)
            hz = HZ
            for k in range(14):                   # grille synthwave qui défile
                z = ((k + (f % 12) / 12) / 14) ** 2.2
                y = hz + int(z * (H - hz))
                d.line([(0, y), (W, y)], fill=tuple(int(PINK[c] * (0.25 + 0.6 * z)) for c in range(3)), width=2 + int(3 * z))
            for k in range(-9, 10):
                d.line([(W / 2 + k * 30, hz), (W / 2 + k * 260, H)], fill=(120, 30, 90), width=2)
            s = 1 + 0.04 * pulse
            sz = int(560 * s)
            sy = HZ - int(sz * 0.62)
            gz = int(760 * s)
            paste(fr, sun_glow.resize((gz, gz)), ((W - gz) / 2, sy - (gz - sz) / 2), 0.95)
            paste(fr, sun_img.resize((sz, sz)), ((W - sz) / 2, sy))
            fr.paste(endbg.crop((0, hz, W, hz + 4)), (0, hz))
            d = ImageDraw.Draw(fr)
            for k in range(14):                   # repasse la grille devant le bas du soleil
                z = ((k + (f % 12) / 12) / 14) ** 2.2
                y = hz + int(z * (H - hz))
                d.line([(0, y), (W, y)], fill=tuple(int(PINK[c] * (0.25 + 0.6 * z)) for c in range(3)), width=2 + int(3 * z))
        else:
            sh = (0, 0)
            if p > 0 and trans[p - 1] == "flash" and t < 9:
                amp = 22 * (1 - t / 9)
                sh = (grng.uniform(-amp, amp), grng.uniform(-amp, amp))
            z, dx = camera(moves[p], src(p), u, sec, pulse)
            fr = src(p).view(t, z, dx, 0, sh)
            fr.paste(shade, (0, 0), shade)
        # -- transitions (fond uniquement : le crédit reste toujours net)
        if p < len(cards) - 1 and trans[p] == "whip" and n - t <= 4:
            fr = whip(fr, ((4 - (n - t) + 1) / 4) ** 1.5, -1)
        if p > 0 and trans[p - 1] == "whip" and t < 4:
            fr = whip(fr, ((4 - t) / 4) ** 1.5, 1)
        if p < len(cards) - 1 and trans[p] == "glitch" and n - t <= 2:
            fr = glitch(fr, 0.6, grng)
        if p > 0 and trans[p - 1] == "glitch" and t < 4:
            fr = glitch(fr, 1 - t / 4, grng)
        if p > 0 and trans[p - 1] == "flash" and t < 3:
            fr = flash(fr, (0.85, 0.5, 0.2)[t])
        # -- textes et habillage
        plan.draw_text(fr, t, step)
        d = ImageDraw.Draw(fr)
        d.rectangle([0, SAFE_TOP, W, SAFE_TOP + 9], fill=(40, 25, 70))
        d.rectangle([0, SAFE_TOP, int(W * (f + 1) / total), SAFE_TOP + 9], fill=PINK)
        d.ellipse([int(W * (f + 1) / total) - 8, SAFE_TOP - 3, int(W * (f + 1) / total) + 8, SAFE_TOP + 12], fill=CYAN)
        paste(fr, pastille, (40, top_y))
        if not plan.fin:
            cp = credit_pills["video" if "video" in cards[p] else "image"]
            paste(fr, cp, (W - 40 - cp.width, top_y + (pastille.height - cp.height) / 2))
        enc.stdin.write(fr.tobytes())
        if f in sheet_at:
            shots[f] = fr.copy()
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("échec de l'encodage ffmpeg")

    # planche d'aperçu : 6 images, 3 colonnes x 2 lignes
    tw, th = 540, 960
    sheet = Image.new("RGB", (tw * 3, th * 2), NIGHT)
    d = ImageDraw.Draw(sheet)
    for j, f in enumerate(sorted(shots)):
        sheet.paste(shots[f].resize((tw, th), Image.LANCZOS), ((j % 3) * tw, (j // 3) * th))
        d.text(((j % 3) * tw + 14, (j // 3) * th + th - 56), f"{f / FPS:.1f} s", font=font(BLACK, 34), fill=YEL, stroke_width=3, stroke_fill=NIGHT)
    sheet.save(os.path.splitext(out)[0] + "-apercu.jpg", quality=88)
    print("ok", out, f"durée {dur:.2f} s", f"plans (temps) {beats}", f"transitions {trans}",
          f"musique {info['style_fr']} {bpm} bpm", f"rendu {time.time() - t_start:.0f} s")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    render(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 11)
