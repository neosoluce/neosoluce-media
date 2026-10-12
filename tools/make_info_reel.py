"""Reel « info » NéoSoluce : encarts texte néon sur fond de scènes originales, musique originale.

Usage :
    python3 tools/make_info_reel.py cartes.json reels/AAAA-MM-JJ-info.mp4 [graine_musique]

cartes.json = liste d'encarts dans l'ordre, chacun {"badge": "...", "titre": "...", "texte": "..."}.
- 3 à 6 encarts. Le premier est l'accroche, le dernier l'appel à l'action (ex. badge « NÉOSOLUCE »,
  titre « Tous les guides GTA 6 », texte « neosoluce.com · Abonne-toi »).
- Chaque encart reste ~4,5 s (le premier 3,2 s). Titre : 40 caractères max. Texte : 90 caractères max.
- Pas de flèches ni d'émojis (les polices ne les affichent pas).
"""
import json, os, subprocess, sys, tempfile, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_logo import find  # noqa: E402
from music import make_music, write_wav  # noqa: E402

ROOT = os.path.dirname(HERE)
SCENES = [os.path.join(ROOT, "scenes", "scene-vice-1.mp4"), os.path.join(ROOT, "scenes", "scene-vice-2.mp4")]
BLACK = find("InterDisplay-Black.otf")
BOLD = find("InterDisplay-Bold.otf")
PINK, CYAN, YEL, WHITE, NIGHT = (255, 61, 154), (45, 226, 230), (255, 209, 102), (255, 255, 255), (12, 5, 32)
W = 1080


def card(badge, titre, texte, path):
    img = Image.new("RGBA", (W, 900), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fk, ft, fs = ImageFont.truetype(BOLD, 46), ImageFont.truetype(BLACK, 88), ImageFont.truetype(BOLD, 50)
    tl = textwrap.wrap(titre, 17)
    sl = textwrap.wrap(texte, 31)
    h = 90 + len(tl) * 100 + 30 + len(sl) * 64 + 50
    d.rounded_rectangle([70, 40, W - 70, 40 + h], 34, fill=NIGHT + (205,), outline=PINK + (255,), width=5)
    y = 70
    kw = d.textlength(badge, font=fk)
    d.rounded_rectangle([(W - kw) / 2 - 24, y - 6, (W + kw) / 2 + 24, y + 58], 20, fill=CYAN + (255,))
    d.text(((W - kw) / 2, y), badge, font=fk, fill=NIGHT + (255,))
    y += 90
    for l in tl:
        d.text(((W - d.textlength(l, font=ft)) / 2, y), l, font=ft, fill=WHITE + (255,), stroke_width=3, stroke_fill=NIGHT + (255,))
        y += 100
    y += 30
    for l in sl:
        d.text(((W - d.textlength(l, font=fs)) / 2, y), l, font=fs, fill=YEL + (255,))
        y += 64
    g = Image.new("RGBA", img.size, PINK + (0,))
    g.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(18)).point(lambda v: v // 3))
    Image.alpha_composite(g, img).save(path)


def main():
    cards = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else abs(hash(out)) % 1000
    assert 3 <= len(cards) <= 6, "3 à 6 encarts"
    times, t = [], 0.0
    for i in range(len(cards)):
        d = 3.2 if i == 0 else 4.6
        times.append((t, t + d)); t += d
    dur = round(t, 2)
    tmp = tempfile.mkdtemp()
    for i, c in enumerate(cards):
        card(c["badge"], c["titre"], c["texte"], os.path.join(tmp, f"c{i}.png"))
    audio, info = make_music(seed=seed, duration=dur)
    wav = os.path.join(tmp, "m.wav"); write_wav(wav, audio)
    n = int(dur // 5) + 2
    with open(os.path.join(tmp, "list.txt"), "w") as f:
        for k in range(n):
            f.write(f"file '{SCENES[k % 2]}'\n")
    inputs = ["-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "list.txt")]
    for i in range(len(cards)):
        inputs += ["-loop", "1", "-t", str(dur), "-i", os.path.join(tmp, f"c{i}.png")]
    inputs += ["-i", wav]
    fc = [f"[0:v]trim=0:{dur},setpts=PTS-STARTPTS[bg]"]
    cur = "[bg]"
    for i, (a0, a1) in enumerate(times):
        fc.append(f"[{i+1}:v]format=rgba,fade=in:st={a0}:d=0.35:alpha=1,fade=out:st={a1-0.3}:d=0.3:alpha=1[c{i}]")
        fc.append(f"{cur}[c{i}]overlay=0:230:enable='between(t,{a0},{a1})'[v{i}]")
        cur = f"[v{i}]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc), "-map", cur,
                    "-map", f"{len(cards)+1}:a", "-t", str(dur), "-c:v", "libx264", "-crf", "24", "-preset", "slow",
                    "-maxrate", "12M", "-bufsize", "24M", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac",
                    "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    # aperçu : 2e encart
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(times[1][0] + 1), "-i", out, "-frames:v", "1",
                    os.path.splitext(out)[0] + "-apercu.jpg"], check=True)
    print("ok", out, "durée", dur, "musique", info)


if __name__ == "__main__":
    main()
