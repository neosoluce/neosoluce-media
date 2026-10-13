"""Montage des vidéos de Léona (mascotte NéoSoluce générée avec OpenArt par Noah).

Usage :
    python3 tools/make_leona_reel.py video.mp4 "Texte exact dit par Léona" reels/AAAA-MM-JJ-leona.mp4

- Garde la voix d'origine de la vidéo (pas de musique ajoutée).
- Met la vidéo au format 1080x1920 (recadrage ou fond flou si besoin).
- Ajoute : une enseigne néon « NEOSOLUCE.COM » en haut, l'étiquette « LÉONA »,
  les sous-titres (découpés en petits morceaux, répartis sur la durée) et la mention « Contenu généré par IA ».
- Crée un aperçu « -apercu.jpg » à vérifier avec Read, puis à supprimer.
"""
import os, subprocess, sys, tempfile, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_logo import find  # noqa: E402

BLACK, BOLD = find("InterDisplay-Black.otf"), find("InterDisplay-Bold.otf")
PINK, CYAN, YEL, WHITE, NIGHT = (255, 61, 154), (45, 226, 230), (255, 209, 102), (255, 255, 255), (12, 5, 32)
W, H = 1080, 1920


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True, check=True).stdout.strip())


def glow(img, color, radius=14, strength=2):
    g = Image.new("RGBA", img.size, color + (0,))
    a = img.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
    g.putalpha(a.point(lambda v: min(255, v * strength)))
    return Image.alpha_composite(g, img)


def static_layer(path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # enseigne néon en haut (remplace la pastille, au-dessus de la tête de Léona)
    sign = Image.new("RGBA", (W, 150), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sign)
    fs = ImageFont.truetype(BLACK, 56)
    s = "NEOSOLUCE.COM"
    sw = ds.textlength(s, font=fs)
    ds.text(((W - sw) / 2, 45), s, font=fs, fill=(255, 220, 240, 255), stroke_width=3, stroke_fill=PINK + (255,))
    sign = glow(sign, PINK, 18, 3)
    img.alpha_composite(sign, (0, 40))
    # mention IA, en bas à droite à côté de l'étiquette LÉONA
    d = ImageDraw.Draw(img)
    fi = ImageFont.truetype(BOLD, 26)
    t = "Contenu généré par IA"
    tw = d.textlength(t, font=fi)
    d.rounded_rectangle([W - 60 - tw - 36, H - 552, W - 60, H - 506], 18, fill=NIGHT + (180,))
    d.text((W - 60 - tw - 18, H - 544), t, font=fi, fill=(255, 255, 255, 220))
    # étiquette LÉONA
    fl = ImageFont.truetype(BLACK, 38)
    d = ImageDraw.Draw(img)
    lw = d.textlength("LÉONA", font=fl)
    d.rounded_rectangle([60, H - 560, 60 + lw + 44, H - 498], 22, fill=CYAN + (255,))
    d.text((82, H - 553), "LÉONA", font=fl, fill=NIGHT + (255,))
    img.save(path)


def subtitle(text, path):
    img = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(BLACK, 60)
    lines = textwrap.wrap(text, 28)
    y = 300 - len(lines) * 76 - 20
    for l in lines:
        lw = d.textlength(l, font=f)
        d.text(((W - lw) / 2, y), l, font=f, fill=WHITE + (255,), stroke_width=7, stroke_fill=NIGHT + (255,))
        y += 76
    img.save(path)


def chunks(text, n=4):
    words = text.split()
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= n or w[-1] in ".?!…,":
            out.append(" ".join(cur)); cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def main():
    src, text, out = sys.argv[1], sys.argv[2], sys.argv[3]
    dur = duration(src)
    tmp = tempfile.mkdtemp()
    static_layer(os.path.join(tmp, "s.png"))
    parts = chunks(text)
    start, end = 0.25, dur - 0.35
    weights = [len(p) for p in parts]
    total = sum(weights)
    times, t = [], start
    for w in weights:
        nt = t + (end - start) * w / total
        times.append((round(t, 2), round(nt, 2))); t = nt
    inputs = ["-i", src, "-loop", "1", "-t", str(dur), "-i", os.path.join(tmp, "s.png")]
    for i, p in enumerate(parts):
        subtitle(p, os.path.join(tmp, f"t{i}.png"))
        inputs += ["-loop", "1", "-t", str(dur), "-i", os.path.join(tmp, f"t{i}.png")]
    fc = ["[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:2[bg];"
          "[b]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=30[v0]",
          "[v0][1:v]overlay=0:0[w0]"]
    cur = "[w0]"
    for i, (a, b) in enumerate(times):
        fc.append(f"{cur}[{i+2}:v]overlay=0:{H-470}:enable='between(t,{a},{b})'[x{i}]")
        cur = f"[x{i}]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc),
                    "-map", cur, "-map", "0:a?", "-t", str(dur), "-c:v", "libx264", "-crf", "20", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    mid = times[len(times) // 2][0] + 0.2
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(mid), "-i", out, "-frames:v", "1",
                    os.path.splitext(out)[0] + "-apercu.jpg"], check=True)
    print("ok", out, "durée", round(dur, 2), "sous-titres", parts)


if __name__ == "__main__":
    main()
