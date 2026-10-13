"""Reel « meme POV » NéoSoluce (format des TikToks viraux) à partir d'un court clip vidéo.

Usage :
    python3 tools/make_meme_reel.py clip.mp4 "Texte du meme" sortie.mp4 [--boucles N] [--musique graine|aucune] [--garder-son]

    - Sortie : MP4 1080x1920, 30 i/s, H.264 yuv420p + AAC, faststart.
    - Cadrage : le clip est rempli en 9:16 en recadrant au centre ; s'il est plus petit, il est agrandi (lanczos).
    - Boucle : le clip est répété N fois, en aller simple (pas d'aller-retour). Par défaut, assez de fois pour
      atteindre au moins 10 s, sans dépasser 20 s (un clip de plus de 20 s n'est pas bouclé).
    - Texte : bloc blanc à coins arrondis, texte noir gras centré (Inter Display Bold), 1 à 3 lignes,
      largeur max ~860 px, vers y=200, affiché pendant toute la vidéo.
    - Signature « NÉOSOLUCE » blanche semi-transparente en bas à droite (au-dessus des boutons TikTok).
    - Son : par défaut, son du clip coupé + musique originale (tools/music.py) avec la graine donnée (7 par défaut) ;
      --musique aucune : piste silencieuse (pour ajouter un son tendance dans l'appli) ;
      --garder-son : garde le son du clip (sans musique).
    - Écrit aussi <sortie>-apercu.jpg (image à mi-parcours) : regarde-le, puis ne le commite pas.

Règles :
    - JAMAIS de vidéo d'un autre créateur ni de trailer : uniquement des clips générés pour NéoSoluce
      ou des captures de Noah.
    - Contenu généré par IA : à signaler à la publication (isAiGenerated / isAigc selon la plateforme).
"""
import argparse, json, math, os, subprocess, sys, tempfile

import numpy as np  # noqa: F401  (utilisé par music.py)
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_logo import find  # noqa: E402
from music import make_music, write_wav  # noqa: E402

W, H, FPS = 1080, 1920, 30
BOX_W, PAD_X, PAD_Y = 860, 44, 30
TEXT_Y = 200
SIGN_Y, SIGN_MARGIN, SIGN_SIZE = 1500, 70, 34


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("Erreur ffmpeg :\n" + r.stderr[-1500:])
    return r.stdout


def probe(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
               "-of", "json", path])
    j = json.loads(out)
    dur = float(j["format"]["duration"])
    has_audio = any(s.get("codec_type") == "audio" for s in j["streams"])
    return dur, has_audio


def wrap(draw, text, font, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            test = (cur + " " + word).strip()
            if draw.textlength(test, font=font) <= max_w or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def make_overlay(text, path):
    bold = find("InterDisplay-Bold.otf")
    black = find("InterDisplay-Black.otf")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    inner = BOX_W - 2 * PAD_X
    for size in range(64, 27, -2):
        font = ImageFont.truetype(bold, size)
        lines = wrap(d, text, font, inner)
        if len(lines) <= 3 and max(d.textlength(l, font=font) for l in lines) <= inner:
            break
    else:
        sys.exit("Texte trop long : 3 lignes maximum dans 860 px.")
    lh = int(size * 1.22)
    box_h = lh * len(lines) + 2 * PAD_Y - (lh - size) // 2
    widest = max(d.textlength(l, font=font) for l in lines)
    box_w = int(min(BOX_W, widest + 2 * PAD_X))
    x0 = (W - box_w) // 2
    d.rounded_rectangle([x0, TEXT_Y, x0 + box_w, TEXT_Y + box_h], radius=34, fill=(255, 255, 255, 255))
    y = TEXT_Y + PAD_Y - (lh - size) // 4
    for l in lines:
        d.text((W // 2, y + lh // 2), l, font=font, fill=(0, 0, 0, 255), anchor="mm")
        y += lh
    # signature
    sf = ImageFont.truetype(black, SIGN_SIZE)
    sig = "NÉOSOLUCE"
    track = 3
    wsig = sum(d.textlength(c, font=sf) + track for c in sig) - track
    x = W - SIGN_MARGIN - wsig
    for c in sig:
        d.text((x, SIGN_Y), c, font=sf, fill=(255, 255, 255, 165), anchor="ls")
        x += d.textlength(c, font=sf) + track
    img.save(path)
    return size, len(lines)


def main():
    ap = argparse.ArgumentParser(description="Reel meme POV NéoSoluce")
    ap.add_argument("clip")
    ap.add_argument("texte")
    ap.add_argument("sortie")
    ap.add_argument("--boucles", type=int, default=None)
    ap.add_argument("--musique", default="7", help="graine entière (défaut 7) ou « aucune »")
    ap.add_argument("--garder-son", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.clip):
        sys.exit("Clip introuvable : " + a.clip)
    seed = None
    if a.musique.lower() != "aucune":
        try:
            seed = int(a.musique)
        except ValueError:
            sys.exit("--musique : un entier (graine) ou « aucune ».")
    cdur, has_audio = probe(a.clip)
    if cdur <= 0.1:
        sys.exit("Clip trop court.")
    if a.boucles is not None:
        n = max(1, a.boucles)
    else:
        n = max(1, math.ceil(10 / cdur))
        while n > 1 and n * cdur > 20:
            n -= 1
    total = n * cdur
    print(f"Clip {cdur:.2f}s x {n} boucle(s) = {total:.2f}s")

    tmp = tempfile.mkdtemp(prefix="memereel_")
    ov = os.path.join(tmp, "overlay.png")
    size, nl = make_overlay(a.texte, ov)
    print(f"Texte : {nl} ligne(s), police {size}px")

    cmd = ["ffmpeg", "-y", "-v", "error", "-stream_loop", str(n - 1), "-i", a.clip,
           "-loop", "1", "-framerate", str(FPS), "-i", ov]
    use_clip_audio = a.garder_son and has_audio
    if a.garder_son and not has_audio:
        print("Avertissement : le clip n'a pas de son, piste silencieuse.")
    if use_clip_audio:
        amap = "0:a:0"
    elif seed is not None and not a.garder_son:
        wav = os.path.join(tmp, "musique.wav")
        audio, info = make_music(seed=seed, duration=total)
        write_wav(wav, audio)
        print("Musique :", info)
        cmd += ["-i", wav]
        amap = "2:a:0"
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
        amap = "2:a:0"
    vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
          f"crop={W}:{H},setsar=1,fps={FPS},format=yuv420p[bg];"
          f"[bg][1:v]overlay=0:0:format=auto,format=yuv420p[v]")
    cmd += ["-filter_complex", vf, "-map", "[v]", "-map", amap, "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2",
            "-movflags", "+faststart", a.sortie]
    run(cmd)

    base, _ = os.path.splitext(a.sortie)
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{total / 2:.3f}", "-i", a.sortie,
         "-frames:v", "1", "-q:v", "3", base + "-apercu.jpg"])
    print("OK :", a.sortie, "+", base + "-apercu.jpg")


if __name__ == "__main__":
    main()
