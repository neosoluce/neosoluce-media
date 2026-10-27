"""Shorts YouTube / TikTok / Reels de Léona (NéoSoluce) : voix off + images officielles + sous-titres.

Recette (voir YOUTUBE-LEONA.md) :
  1. Les scripts sont dans shorts/leona_shorts.json (texte affiché, texte dit, fait, image, source).
  2. UNE narration longue AITOPIA (MiniMax speech-02-turbo, voix French_MovieLeadFemale) enchaîne plusieurs
     scripts : pause <#0.8#> entre les morceaux d'un script, <#3.0#> entre deux scripts.
     python3 tools/make_short.py prompt --dates 2026-10-28,2026-10-29   -> texte à coller dans generate_audio
  3. Découpage de la narration (silencedetect) : un .wav et un .json de timings par date.
     python3 tools/make_short.py split narration.mp3 --dates 2026-10-28,2026-10-29 --out work/
  4. Montage 1080x1920 (H.264 veryfast CRF 23, AAC normalisé, < 15 Mo) :
     python3 tools/make_short.py render --date 2026-10-28 --work work/ --out work/2026-10-28.mp4
     (--fake : timings estimés et piste muette, pour un aperçu sans voix)
  5. Livraison dans le planning (reel.mp4 + legende.txt + calendrier.json) :
     python3 tools/make_short.py deliver --date 2026-10-28 --video work/2026-10-28.mp4 --stock <dossier stock>
Dossiers par défaut : variables NEOSOLUCE_STOCK (faits.json, calendrier.json, jours/), NEOSOLUCE_IMG (images
officielles <id>.jpg), NEOSOLUCE_CLIPS (clips officiels *.mp4).
"""
import argparse, json, os, re, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SPEC = os.path.join(REPO, "shorts", "leona_shorts.json")
LEONA_HOOK = os.path.join(REPO, "mascotte", "references", "leona-police.png")
LEONA_END = os.path.join(REPO, "mascotte", "references", "leona-ps5.jpg")
FONT_DIR = "/usr/share/fonts/opentype/inter/"
BLACK, BOLD, SEMI = FONT_DIR + "InterDisplay-Black.otf", FONT_DIR + "InterDisplay-Bold.otf", FONT_DIR + "Inter-SemiBold.otf"
W, H, FPS = 1080, 1920, 30
PINK, CYAN, YEL, WHITE, NIGHT = (255, 61, 154), (45, 226, 230), (255, 209, 102), (255, 255, 255), (12, 5, 32)
SEG_PAUSE, SCRIPT_PAUSE = 0.8, 3.0
MIN_DUR, END_HOLD = 30.0, 1.2


def env(name, default=""):
    return os.environ.get(name, default)


def load_spec():
    return json.load(open(SPEC))


def short_for(date, spec=None):
    for s in (spec or load_spec())["shorts"]:
        if s["date"] == date:
            return s
    sys.exit(f"pas de Short pour {date}")


def segments_of(s):
    """Morceaux dans l'ordre : accroche, faits, fin. Chaque morceau : (type, texte dit, texte affiché, fait)."""
    out = [("hook", s["hook_dit"], s["hook_ecran"], None)]
    out += [("fait", f["dit"], f["ecran"], f) for f in s["faits"]]
    out.append(("fin", s["fin_dit"], s["fin_ecran"], None))
    return out


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout)


# ---------------------------------------------------------------- 1. texte de la narration
def cmd_prompt(a):
    spec = load_spec()
    parts = []
    for d in a.dates.split(","):
        s = short_for(d, spec)
        parts.append(f" <#{SEG_PAUSE}#> ".join(x[1] for x in segments_of(s)))
    t = f" <#{SCRIPT_PAUSE}#> ".join(parts)
    print(t)
    print(f"\n[{len(t)} caractères ; constaté le 27/10/2026 : environ 3 crédits AITOPIA pour 1 000 caractères]", file=sys.stderr)


# ---------------------------------------------------------------- 2. découpage
def silences(path, noise="-38dB", mind=0.3):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n={noise}:d={mind}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(st, en))


def pick_longest(sil, n):
    """Garde les n silences les plus longs, remis dans l'ordre chronologique."""
    return sorted(sorted(sil, key=lambda x: x[1] - x[0], reverse=True)[:n])


def cmd_split(a):
    spec = load_spec()
    dates = a.dates.split(",")
    total = duration(a.audio)
    sil = silences(a.audio)
    # silences de début et de fin du fichier : on les retire des candidats
    inner = [x for x in sil if x[0] > 0.05 and x[1] < total - 0.05]
    cuts = pick_longest(inner, len(dates) - 1)
    bounds, start = [], 0.0
    for c in cuts:
        bounds.append((start, c[0] + 0.05)); start = c[1] - 0.05
    bounds.append((start, total))
    os.makedirs(a.out, exist_ok=True)
    for d, (b0, b1) in zip(dates, bounds):
        s = short_for(d, spec)
        segs = segments_of(s)
        wav = os.path.join(a.out, d + ".wav")
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{b0:.3f}", "-to", f"{b1:.3f}", "-i", a.audio, "-ac", "1", "-ar", "44100", wav])
        dur = duration(wav)
        ss = silences(wav)
        lead = ss[0][1] if ss and ss[0][0] < 0.05 else 0.0           # silence au début
        tail = ss[-1][0] if ss and ss[-1][1] > dur - 0.05 else dur    # silence à la fin
        inner = [x for x in ss if x[0] > lead + 0.05 and x[1] < tail - 0.05]
        found = pick_longest(inner, len(segs) - 1)
        if len(found) == len(segs) - 1:
            marks = [lead] + [(x[0] + x[1]) / 2 for x in found] + [tail]
            speech_end = [x[0] for x in found] + [tail]
            mode = "silences"
        else:  # repli : proportionnel au nombre de caractères dits
            n = [len(x[1]) for x in segs]; tot = sum(n); marks = [lead]
            for k in n:
                marks.append(marks[-1] + (tail - lead) * k / tot)
            speech_end = marks[1:]
            mode = "proportionnel"
        t = dict(date=d, wav=os.path.basename(wav), duree=dur, debut_voix=lead, fin_voix=tail, mode=mode,
                 segments=[dict(type=segs[i][0], debut=marks[i], fin=marks[i + 1], fin_parole=speech_end[i]) for i in range(len(segs))])
        json.dump(t, open(os.path.join(a.out, d + ".json"), "w"), indent=1)
        print(d, f"{dur:.1f} s", mode, [round(m, 2) for m in marks])


def fake_timings(s):
    segs = segments_of(s)
    t, out = 0.15, []
    for typ, dit, _, _ in segs:
        d = len(dit) / 15.5
        out.append(dict(type=typ, debut=t, fin=t + d + SEG_PAUSE / 2)); t += d + SEG_PAUSE
    return dict(date=s["date"], duree=t, debut_voix=0.15, fin_voix=t - SEG_PAUSE, mode="estimé", segments=out)


# ---------------------------------------------------------------- 3. montage
def font(p, s):
    return ImageFont.truetype(p, s)


def wrap_px(d, text, f, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def nbsp(text):
    """Espaces insécables de la typographie française : jamais de « : » ou « ? » seul en début de ligne."""
    text = re.sub(r" ([:;?!»])", "\u00a0\\1", text)
    return re.sub(r"« ", "«\u00a0", text)


def text_block(text, size, maxw=920, fill=WHITE, stroke=8, fnt=BLACK, line_gap=1.18, align="center"):
    f = font(fnt, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lines = wrap_px(tmp, nbsp(text), f, maxw)
    lh = int(size * line_gap)
    img = Image.new("RGBA", (W, lh * len(lines) + stroke * 2 + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=f)
        x = (W - lw) / 2 if align == "center" else 70
        d.text((x, stroke + i * lh), l, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=NIGHT + (255,))
    return img


def chunks(text, maxc=44):
    """Découpe le texte affiché en morceaux équilibrés de 2 lignes au plus (sous-titres par groupe de mots),
    en coupant de préférence après une ponctuation."""
    words = []
    for w in text.split():  # ponctuation française et nombres collés au mot voisin
        num = re.fullmatch(r"(\d+[,.]?\d*|III|IV|VI|X\|S)[.,;:]?", w)
        if words and (re.fullmatch(r"[:;?!»]+[.,]?", w) or words[-1] == "«" or re.fullmatch(r"\d+[,.]?\d*", words[-1])
                      or (num and words[-1].split()[-1] in ("PlayStation", "trailer", "GTA", "Redemption", "Series"))):
            words[-1] += " " + w
        else:
            words.append(w)
    k = max(1, -(-len(text) // maxc))
    target = len(text) / k
    out, cur = [], ""
    for i, w in enumerate(words):
        cur = (cur + " " + w).strip()
        left = len(words) - i - 1
        punct = bool(re.search(r"[.!?:;,]$", w))
        short = (len(w) <= 3 and not punct) or (cur.count("«") > cur.count("»") and len(cur) < target * 1.3)
        if left and not short and len(out) < k - 1 and (len(cur) >= target or (punct and len(cur) >= target * 0.6)):
            out.append(cur); cur = ""
    if cur:
        out.append(cur)
    return out


def pill(text, color):
    f = font(BLACK, 34)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = d.textlength(text, font=f)
    img = Image.new("RGBA", (int(tw) + 92, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, 63], 32, fill=color + (255,))
    # coche
    d.line([(24, 33), (34, 44), (52, 22)], fill=NIGHT + (255,), width=7, joint="curve")
    d.text((66, 12), text, font=f, fill=NIGHT + (255,))
    return img


def small(text, size=30, fill=(255, 255, 255), bg=True, fnt=SEMI):
    f = font(fnt, size)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lines = wrap_px(d, text, f, 900)
    lh = int(size * 1.3)
    tw = max(d.textlength(l, font=f) for l in lines)
    img = Image.new("RGBA", (int(tw) + 36, lh * len(lines) + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if bg:
        d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], 14, fill=NIGHT + (170,))
    for i, l in enumerate(lines):
        d.text((18, 8 + i * lh), l, font=f, fill=fill + (235,))
    return img


def cover(img, cx=0.5, cy=0.5, zoom=1.0):
    """Recadre img (PIL) en 9:16 autour de (cx, cy), avec un zoom de base."""
    iw, ih = img.size
    tw = min(iw, ih * 9 / 16) / zoom
    th = tw * 16 / 9
    x0 = min(max(cx * iw - tw / 2, 0), iw - tw)
    y0 = min(max(cy * ih - th / 2, 0), ih - th)
    return (x0, y0, tw, th)


def kb_frame(src, box, t, dur, direction, out=(W, H)):
    """Ken Burns : zoom lent de 1.00 à 1.10 (ou l'inverse) dans la boîte box."""
    x0, y0, bw, bh = box
    p = min(max(t / max(dur, 0.01), 0), 1)
    p = p * p * (3 - 2 * p)
    z = 1 + 0.10 * (p if direction % 2 == 0 else 1 - p)
    w2, h2 = bw / z, bh / z
    dx = (bw - w2) * (0.5 + (0.25 if direction % 3 == 0 else -0.25) * (p - 0.5))
    dy = (bh - h2) / 2
    return src.resize(out, Image.BICUBIC, box=(x0 + dx, y0 + dy, x0 + dx + w2, y0 + dy + h2))


def leona_card(path, crop, fg_y):
    """Léona au premier plan (recadrage sans le buste) sur un fond flou et sombre du même recadrage."""
    im = Image.open(path).convert("RGB").crop(crop)
    fgw = W
    fg = im.resize((fgw, int(im.height * fgw / im.width)), Image.LANCZOS)
    bx = cover(im)
    bg = im.resize((W, H), Image.BICUBIC, box=(bx[0], bx[1], bx[0] + bx[2], bx[1] + bx[3])).filter(ImageFilter.GaussianBlur(28))
    bg = Image.blend(bg, Image.new("RGB", (W, H), NIGHT), 0.45)
    bg.paste(fg, (0, fg_y))
    # fondu du bas du premier plan
    grad = Image.new("L", (W, 260))
    for y in range(260):
        grad.paste(int(255 * y / 259), (0, y, W, y + 1))
    shade = Image.new("RGB", (W, 260), NIGHT)
    region = bg.crop((0, fg_y + fg.height - 260, W, fg_y + fg.height))
    bg.paste(Image.composite(shade, region, grad), (0, fg_y + fg.height - 260))
    return bg


def clip_frames(name, cx):
    cdir = env("NEOSOLUCE_CLIPS")
    f = [x for x in os.listdir(cdir) if name in x and x.endswith(".mp4")][0]
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(cdir, f), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True).stdout
    info = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                os.path.join(cdir, f)]).stdout.strip().split(",")
    iw, ih = int(info[0]), int(info[1])
    n = len(p) // (iw * ih * 3)
    frames = []
    for i in range(n):
        im = Image.frombytes("RGB", (iw, ih), p[i * iw * ih * 3:(i + 1) * iw * ih * 3])
        b = cover(im, cx)
        frames.append(im.resize((W, H), Image.BICUBIC, box=(b[0], b[1], b[0] + b[2], b[1] + b[3])))
    return frames


def cmd_render(a):
    s = short_for(a.date)
    faits = {x["id"]: x for x in json.load(open(os.path.join(env("NEOSOLUCE_STOCK"), "faits.json")))["faits"]}
    if a.fake:
        tm, wav = fake_timings(s), None
    else:
        tm = json.load(open(os.path.join(a.work, a.date + ".json")))
        wav = os.path.join(a.work, tm["wav"])
    segs = segments_of(s)
    T = tm["segments"]
    voice_end = tm["fin_voix"]
    total = max(MIN_DUR, voice_end + END_HOLD)
    # visuels de chaque morceau
    hook = leona_card(LEONA_HOOK, (0, 120, 1296, 1150), 560)      # tête et cou seulement
    end = leona_card(LEONA_END, (360, 0, 1200, 768), 640)
    vis = []
    for (typ, dit, ecran, f), t in zip(segs, T):
        if typ == "fait":
            assert f["id"] in faits, f["id"]
            if f["img"].startswith("clip:"):
                vis.append(("clip", clip_frames(f["img"][5:], f.get("x", 0.5))))
            else:
                im = Image.open(os.path.join(env("NEOSOLUCE_IMG"), f["img"] + ".jpg")).convert("RGB")
                vis.append(("img", im, cover(im, f.get("x", 0.5), 0.5, f.get("zoom", 1.0))))
        else:
            vis.append(("leona", hook if typ == "hook" else end))
    # textes
    hook_txt = text_block(s["hook_ecran"], 92, maxw=960, fill=WHITE, stroke=10)
    leona_tag = small("Léona · personnage IA · NéoSoluce", 26)
    credit = small("© Rockstar Games", 26)
    pills = {"VÉRIFIÉ": pill("VÉRIFIÉ", CYAN), "2 SOURCES": pill("2 SOURCES", YEL)}
    cta_main = text_block("Les sources sont sur", 64, fill=WHITE, stroke=8)
    cta_url = text_block("neosoluce.com", 96, fill=PINK, stroke=10)
    fin_q = s["fin_ecran"].split("·")[-1].strip()
    cta_q = text_block(fin_q, 58, fill=YEL, stroke=8)
    subs = []  # (debut, fin, image)
    for i, ((typ, dit, ecran, f), t) in enumerate(zip(segs, T)):
        if typ != "fait":
            continue
        parts = chunks(ecran)
        n = sum(len(p) for p in parts)
        t0 = t["debut"] if i else 0
        span = t.get("fin_parole", t["fin"] - SEG_PAUSE / 2) - t0
        for p in parts:
            d = span * len(p) / n
            subs.append((i, t0, text_block(p, 66, stroke=8)))
            t0 += d
    srcs = {}
    for (typ, dit, ecran, f), t in zip(segs, T):
        if typ == "fait":
            srcs[t["debut"]] = (small("Source : " + f["source"], 30), pills[f.get("badge", "VÉRIFIÉ")])
    # encodage
    out = a.out
    tmpv = out + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-maxrate", "2400k",
                            "-bufsize", "4800k", "-pix_fmt", "yuv420p", tmpv], stdin=subprocess.PIPE)
    nfr = int(total * FPS)
    hook_end = max(2.5, T[0]["fin"])
    for k in range(nfr):
        t = k / FPS
        # morceau courant (le premier fait commence après l'accroche ; la fin dure jusqu'au bout)
        idx = 0
        for i, seg in enumerate(T):
            if t >= (seg["debut"] if i else 0):
                idx = i
        if idx == 0 and t >= hook_end:
            idx = 1
        if idx == 1 and t < hook_end:
            idx = 0
        seg = T[idx]
        s0 = hook_end if idx == 1 else (0 if idx == 0 else seg["debut"])
        s1 = total if idx == len(T) - 1 else T[idx + 1]["debut"]
        v = vis[idx]
        lt = t - s0
        if v[0] == "leona":
            src = v[1]
            z = 1 + 0.05 * min(lt / max(s1 - s0, 0.1), 1)
            w2, h2 = W / z, H / z
            fr = src.resize((W, H), Image.BICUBIC, box=((W - w2) / 2, (H - h2) / 2.6, (W - w2) / 2 + w2, (H - h2) / 2.6 + h2))
        elif v[0] == "img":
            fr = kb_frame(v[1], v[2], lt, s1 - s0, idx)
        else:  # clip officiel au ralenti (x0,5) puis image figée
            fi = min(int(lt * FPS / 2), len(v[1]) - 1)
            fr = v[1][fi]
            if lt * FPS / 2 >= len(v[1]):
                hold = lt - len(v[1]) * 2 / FPS
                z = 1 + 0.06 * min(hold / max(s1 - s0, 0.1), 1)
                w2, h2 = W / z, H / z
                fr = fr.resize((W, H), Image.BICUBIC, box=((W - w2) / 2, (H - h2) / 2, (W - w2) / 2 + w2, (H - h2) / 2 + h2))
        fr = fr.convert("RGBA")
        typ = segs[idx][0]
        if typ == "hook":
            fr.alpha_composite(hook_txt, (0, 250))
            fr.alpha_composite(leona_tag, (60, 1440))
        elif typ == "fin":
            fr.alpha_composite(cta_main, (0, 230))
            fr.alpha_composite(cta_url, (0, 310))
            fr.alpha_composite(cta_q, (0, 1330))
            fr.alpha_composite(leona_tag, (60, 1520))
        else:
            # dégradé sombre en bas pour la lisibilité
            fr.alpha_composite(SHADE, (0, 0))
            sl, pl = srcs[seg["debut"]]
            fr.alpha_composite(pl, (60, 230))
            fr.alpha_composite(credit, (W - credit.width - 140, 240))
            cur = [im for (si, a0, im) in subs if si == idx and a0 <= max(t, s0)]
            if cur:
                im = cur[-1]
                fr.alpha_composite(im, (0, 1180 - im.height // 2))
            fr.alpha_composite(sl, ((W - sl.width) // 2, 1395))
        enc.stdin.write(fr.convert("RGB").tobytes())
    enc.stdin.close(); enc.wait()
    # audio : voix normalisée, complétée par du silence
    if wav:
        run(["ffmpeg", "-y", "-v", "error", "-i", tmpv, "-i", wav, "-filter_complex",
             f"[1:a]loudnorm=I=-15:TP=-1.5:LRA=11,aresample=44100,apad=whole_dur={total:.3f}[a]", "-map", "0:v", "-map", "[a]",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out])
    else:
        run(["ffmpeg", "-y", "-v", "error", "-i", tmpv, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "64k", "-shortest", "-movflags", "+faststart", out])
    os.remove(tmpv)
    print(out, f"{duration(out):.1f} s", f"{os.path.getsize(out) / 1e6:.2f} Mo")


def make_shade():
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for y in range(900, H):
        a = int(200 * min(1, (y - 900) / 380))
        d.line([(0, y), (W, y)], fill=NIGHT + (a,))
    for y in range(0, 380):
        d.line([(0, y), (W, y)], fill=NIGHT + (int(150 * (1 - y / 380)),))
    return g


SHADE = make_shade()


# ---------------------------------------------------------------- 4. textes de publication
def texts(s, faits):
    urls = []
    for f in s["faits"]:
        for u in faits[f["id"]]["sources"]:
            if u not in urls:
                urls.append(u)
    tags = " ".join(s["hashtags"])
    desc = "\n".join([s["ligne1"], s["ligne2"], "", "Sources :"] + ["- " + u for u in urls] +
                     ["", "L'article complet : " + s["article"], "",
                      "Images © Rockstar Games / Take-Two Interactive. NéoSoluce n'est pas affilié à Rockstar Games. "
                      "Léona est un personnage original généré par IA.", "", "#Shorts " + tags])
    tiktok = f"{s['ligne1']} Sources sur neosoluce.com (lien en bio). {s['question']} · © Rockstar Games · Léona est un personnage IA {tags} #Léona #GTA6FR"
    insta = "\n".join([s["ligne1"], ""] + [f"✅ {f['ecran'].lstrip('0123456789. ')}" for f in s["faits"]] +
                      ["", s["question"] + " 👇", "", "Toutes les sources : neosoluce.com (lien en bio).",
                       "Images © Rockstar Games · Léona est un personnage original généré par IA.", "",
                       tags + " #ViceCity #GamersFR #GamersBE #NéoSoluce"])
    pin = "📌 Les sources de cette vidéo :\n" + "\n".join("- " + u for u in urls) + \
          f"\nL'article complet : {s['article']}\n{s['question']}"
    return dict(titre=s["titre"], description=desc, tiktok=tiktok, instagram=insta, commentaire=pin, sources=urls)


def cmd_deliver(a):
    stock = env("NEOSOLUCE_STOCK")
    s = short_for(a.date)
    faits = {x["id"]: x for x in json.load(open(os.path.join(stock, "faits.json")))["faits"]}
    t = texts(s, faits)
    day = os.path.join(stock, "jours", a.date)
    dst = os.path.join(day, "reel.mp4")
    run(["cp", a.video, dst])
    dur = round(duration(dst), 1)
    cal_p = os.path.join(stock, "calendrier.json")
    cal = json.load(open(cal_p))
    for j in cal["jours"]:
        if j["date"] == a.date:
            j["short"] = dict(t, fichier=f"jours/{a.date}/reel.mp4", duree_s=dur, taille_mo=round(os.path.getsize(dst) / 1e6, 2),
                              faits=[f["id"] for f in s["faits"]], voix="Léona (AITOPIA MiniMax speech-02-turbo, French_MovieLeadFemale)",
                              specs="1080x1920, H.264 veryfast CRF 23, 30 ips, voix AAC normalisée, sans musique")
            j["reel"].update(fichier=f"jours/{a.date}/reel.mp4", duree_s=dur, format="Short Léona (YouTube, TikTok, Reels)",
                             remplace_le="2026-10-27")
    json.dump(cal, open(cal_p, "w"), ensure_ascii=False, indent=1)
    lp = os.path.join(day, "legende.txt")
    old = open(lp).read().split("\n\n=== SHORT LÉONA")[0]
    block = (f"\n\n=== SHORT LÉONA (remplace le Reel du jour : même vidéo sur YouTube Shorts, TikTok et Instagram) ===\n"
             f"Durée : {dur} s · sans musique : ajoute un son dans l'appli, volume bas (10 à 20 %) sous la voix.\n\n"
             f"--- TITRE YOUTUBE ---\n{t['titre']}\n\n--- DESCRIPTION YOUTUBE ---\n{t['description']}\n\n"
             f"--- LÉGENDE TIKTOK ---\n{t['tiktok']}\n\n--- LÉGENDE INSTAGRAM ---\n{t['instagram']}\n\n"
             f"--- COMMENTAIRE ÉPINGLÉ ---\n{t['commentaire']}\n")
    open(lp, "w").write(old + block)
    print(a.date, "livré", dur, "s")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("prompt"); x.add_argument("--dates", required=True); x.set_defaults(f=cmd_prompt)
    x = sp.add_parser("split"); x.add_argument("audio"); x.add_argument("--dates", required=True); x.add_argument("--out", required=True)
    x.set_defaults(f=cmd_split)
    x = sp.add_parser("render"); x.add_argument("--date", required=True); x.add_argument("--work", default=".")
    x.add_argument("--out", required=True); x.add_argument("--fake", action="store_true"); x.set_defaults(f=cmd_render)
    x = sp.add_parser("deliver"); x.add_argument("--date", required=True); x.add_argument("--video", required=True)
    x.set_defaults(f=cmd_deliver)
    a = p.parse_args(); a.f(a)


if __name__ == "__main__":
    main()
