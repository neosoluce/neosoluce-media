"""Visuels réseaux sociaux à partir des images OFFICIELLES de GTA VI publiées par Rockstar Games
(https://www.rockstargames.com/VI/media), déposées par Noah dans le dossier officiel/ du dépôt.

Cadre légal (politique de Rockstar/Take-Two sur les contenus des fans) : usage de fan NON commercial uniquement.
Donc : jamais sur une publication sponsorisée, boostée, en partenariat ou qui fait la promotion d'un produit ;
crédit « © Rockstar Games » toujours visible ; image non déformée ; aucun spoiler ; aucune image qui a fuité.

Usage :
    python3 tools/make_official.py post  officiel/<image> out.jpg "BADGE" "Titre" "Texte"
    python3 tools/make_official.py story officiel/<image> out.jpg "BADGE" "Titre" "Texte"
    python3 tools/make_official.py reel  cartes.json out.mp4 [graine]
        cartes.json = [{"image": "officiel/<fichier>", "badge": "...", "titre": "...", "texte": "..."}, ...] (3 à 6)
        ou, pour une VIDÉO officielle : {"video": "officiel/videos/<fichier>.mp4", "x": 0.5, "cadre": "remplir"|"entier",
        "debut": 0, "badge": ..., "titre": ..., "texte": ...} (son d'origine coupé, crédit « Vidéo officielle © Rockstar Games »)
"""
import json, os, subprocess, sys, tempfile, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_logo import find  # noqa: E402

BLACK, BOLD = find("InterDisplay-Black.otf"), find("InterDisplay-Bold.otf")
PINK, CYAN, YEL, WHITE, NIGHT = (255, 61, 154), (45, 226, 230), (255, 209, 102), (255, 255, 255), (12, 5, 32)
CREDIT = "Image officielle © Rockstar Games"


def fit_cover(img, w, h):
    return ImageOps.fit(img.convert("RGB"), (w, h), Image.LANCZOS, centering=(0.5, 0.45))


def panel(w, badge, titre, texte):
    """Encart néon en bas de l'image, hauteur adaptée au texte."""
    fk, ft, fs = ImageFont.truetype(BOLD, 40), ImageFont.truetype(BLACK, 74), ImageFont.truetype(BOLD, 42)
    tl, sl = textwrap.wrap(titre, 20), textwrap.wrap(texte, 36)
    h = 70 + 70 + len(tl) * 84 + 20 + len(sl) * 54 + 50
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([50, 10, w - 50, h - 10], 32, fill=NIGHT + (225,), outline=PINK + (255,), width=4)
    y = 40
    kw = d.textlength(badge, font=fk)
    d.rounded_rectangle([90, y, 90 + kw + 40, y + 56], 22, fill=CYAN + (255,))
    d.text((110, y + 4), badge, font=fk, fill=NIGHT + (255,))
    y += 86
    for l in tl:
        d.text((90, y), l, font=ft, fill=WHITE + (255,))
        y += 84
    y += 16
    for l in sl:
        d.text((90, y), l, font=fs, fill=YEL + (255,))
        y += 54
    return img


def overlay(w, h, badge, titre, texte, credit=CREDIT):
    """Calque transparent : dégradé sombre, pastille NÉOSOLUCE, encart néon, crédit."""
    grad = Image.new("L", (1, h))
    for y in range(h):
        grad.putpixel((0, y), int(230 * max(0, (y - h * 0.45) / (h * 0.55)) ** 1.3))
    base = Image.new("RGBA", (w, h), NIGHT + (0,))
    base.putalpha(grad.resize((w, h)))
    return decorate(base, w, h, badge, titre, texte, credit)


def frame(src, w, h, badge, titre, texte):
    base = fit_cover(Image.open(src), w, h).convert("RGBA")
    return Image.alpha_composite(base, overlay(w, h, badge, titre, texte)).convert("RGB")


def decorate(base, w, h, badge, titre, texte, credit):
    d = ImageDraw.Draw(base)
    tall = h > 1500  # story / reel : marges plus grandes (zoom et interface des applis)
    top = 110 if tall else 50
    fb = ImageFont.truetype(BLACK, 44)
    d.rounded_rectangle([60, top, 60 + d.textlength("NÉOSOLUCE", font=fb) + 50, top + 74], 24, fill=NIGHT + (210,))
    d.text((85, top + 10), "NÉOSOLUCE", font=fb, fill=WHITE + (255,))
    p = panel(w, badge, titre, texte)
    base.alpha_composite(p, (0, h - p.height - (190 if tall else 80)))
    fc = ImageFont.truetype(BOLD, 28)
    d = ImageDraw.Draw(base)
    d.text(((w - d.textlength(credit, font=fc)) / 2, h - (150 if tall else 58)), credit, font=fc, fill=(255, 255, 255, 220))
    return base


def video_clip(c, seg, tmp, i):
    """Segment de Reel à partir d'une VIDÉO officielle de Rockstar (officiel/videos/).
    Son d'origine coupé. Les clips très courts (portraits animés de 1 à 1,5 s) sont joués en aller-retour
    en boucle ; les vidéos plus longues sont lues à partir de "debut" (secondes).
    "cadre": "remplir" (défaut, recadrage plein écran) ou "entier" (vidéo entière sur fond flou, ex. jaquette).
    "largeur": avec "entier", part centrale de la largeur gardée (1 = tout, 0.45 = la jaquette seule).
    "x": position horizontale du recadrage, de 0 (gauche) à 1 (droite), 0.5 par défaut : vérifie sur l'aperçu
    que le visage est bien dans le cadre."""
    ov = os.path.join(tmp, f"o{i}.png")
    overlay(1080, 1920, c["badge"], c["titre"], c["texte"], "Vidéo officielle © Rockstar Games").save(ov)
    frames = int(seg * 30)
    src = c["video"]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True, check=True).stdout.strip())
    if c.get("cadre") == "entier":
        z = float(c.get("largeur", 1))  # garde seulement la partie centrale (ex. 0.45 pour la jaquette)
        fit = (f"crop=iw*{z}:ih,split[s1][s2];[s1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,"
               "eq=brightness=-0.25[bg];[s2]scale=900:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-150")
    else:
        fit = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:x=(iw-1080)*{float(c.get('x', 0.5))}"
    if dur < seg:  # aller-retour en boucle
        chain = f"[0:v]fps=30,{fit},split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0,loop=loop=-1:size=32767[v]"
        inp = ["-i", src]
    else:
        chain = f"[0:v]fps=30,{fit}[v]"
        inp = ["-ss", str(c.get("debut", 0)), "-i", src]
    out = os.path.join(tmp, f"c{i}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inp, "-i", ov, "-filter_complex",
                    chain + ";[v][1:v]overlay=0:0,format=yuv420p[o]", "-map", "[o]", "-an",
                    "-frames:v", str(frames), "-c:v", "libx264", "-crf", "20", out], check=True)
    return out


def reel(cards_path, out, seed):
    from music import make_music, write_wav
    cards = json.load(open(cards_path, encoding="utf-8"))
    assert 3 <= len(cards) <= 6, "3 à 6 encarts"
    tmp = tempfile.mkdtemp()
    seg = 3.6
    dur = round(seg * len(cards), 2)
    clips = []
    for i, c in enumerate(cards):
        if "video" in c:
            clips.append(video_clip(c, seg, tmp, i))
            continue
        fr = frame(c["image"], 1080, 1920, c["badge"], c["titre"], c["texte"])
        p = os.path.join(tmp, f"f{i}.jpg"); fr.save(p, quality=92)
        # léger zoom lent (effet Ken Burns) sur chaque image
        clip = os.path.join(tmp, f"c{i}.mp4")
        frames = int(seg * 30)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", p, "-vf",
                        f"scale=1296:2304,zoompan=z='min(zoom+0.0005,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30,format=yuv420p",
                        "-frames:v", str(frames), "-c:v", "libx264", "-crf", "20", clip], check=True)
        clips.append(clip)
    lst = os.path.join(tmp, "l.txt")
    open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
    audio, info = make_music(seed=seed, duration=dur)
    wav = os.path.join(tmp, "m.wav"); write_wav(wav, audio)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-map", "0:v", "-map", "1:a", "-t", str(dur), "-c:v", "libx264", "-crf", "23", "-preset", "slow",
                    "-maxrate", "12M", "-bufsize", "24M", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", out], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(seg + 1), "-i", out, "-frames:v", "1",
                    os.path.splitext(out)[0] + "-apercu.jpg"], check=True)
    print("ok", out, "durée", dur, "musique", info)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode in ("post", "story"):
        w, h = (1080, 1350) if mode == "post" else (1080, 1920)
        frame(sys.argv[2], w, h, sys.argv[4], sys.argv[5], sys.argv[6]).save(sys.argv[3], quality=92)
        print("ok", sys.argv[3])
    elif mode == "reel":
        reel(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 11)
