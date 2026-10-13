"""Reel « gameplay » NéoSoluce à partir d'une capture de jeu filmée par Noah sur SA console.

Usage :
    python3 tools/make_gameplay_reel.py capture.mp4 cartes.json reels/AAAA-MM-JJ-gameplay.mp4 [graine] [debut_s] [duree_s]

- capture.mp4 : vidéo enregistrée par Noah (PS5 : bouton Créer). Jamais une vidéo de Rockstar, d'un trailer
  ou d'un autre créateur.
- cartes.json : 2 à 5 encarts [{"badge": "...", "titre": "...", "texte": "..."}] affichés à tour de rôle
  en bas de l'écran (titre ≤ 40 caractères, texte ≤ 90). Le dernier encart reste jusqu'à la fin.
- Le son du jeu est COUPÉ : il contient des musiques sous droits (radios). Il est remplacé par une musique
  originale de tools/music.py (et, sur Instagram, par un titre de la bibliothèque sous licence).
- Format de sortie : 1080x1920, 30 i/s, H.264 + AAC, 8 à 45 s.
- Une mention « Capture NéoSoluce · GTA VI © Rockstar Games » est incrustée en permanence.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_logo import find  # noqa: E402
from music import make_music, write_wav  # noqa: E402
from make_info_reel import card  # noqa: E402

BLACK = find("InterDisplay-Black.otf")
BOLD = find("InterDisplay-Bold.otf")
PINK, CYAN, WHITE, NIGHT = (255, 61, 154), (45, 226, 230), (255, 255, 255), (12, 5, 32)
W, H = 1080, 1920


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def overlay_frame(path):
    """Bandeau haut (marque) + mention de capture, sur fond transparent."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f_brand, f_small = ImageFont.truetype(BLACK, 64), ImageFont.truetype(BOLD, 30)
    # bandeau haut
    d.rounded_rectangle([60, 70, W - 60, 190], 30, fill=NIGHT + (210,), outline=PINK + (255,), width=4)
    t = "NÉOSOLUCE"
    d.text(((W - d.textlength(t, font=f_brand)) / 2, 92), t, font=f_brand, fill=WHITE + (255,))
    d.line([(W / 2 - 120, 172), (W / 2 + 120, 172)], fill=CYAN + (255,), width=4)
    # mention capture
    m = "Capture NéoSoluce · GTA VI © Rockstar Games"
    d.text(((W - d.textlength(m, font=f_small)) / 2, H - 70), m, font=f_small, fill=(255, 255, 255, 200))
    g = Image.new("RGBA", img.size, PINK + (0,))
    g.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(14)).point(lambda v: v // 3))
    Image.alpha_composite(g, img).save(path)


def main():
    src, cards_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else abs(hash(out)) % 1000
    start = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
    total = probe_duration(src)
    dur = float(sys.argv[6]) if len(sys.argv) > 6 else min(30.0, total - start)
    dur = round(max(8.0, min(45.0, dur, total - start)), 2)
    cards = json.load(open(cards_path, encoding="utf-8"))
    assert 2 <= len(cards) <= 5, "2 à 5 encarts"
    tmp = tempfile.mkdtemp()
    overlay_frame(os.path.join(tmp, "top.png"))
    seg = dur / len(cards)
    for i, c in enumerate(cards):
        card(c["badge"], c["titre"], c["texte"], os.path.join(tmp, f"c{i}.png"))
    audio, info = make_music(seed=seed, duration=dur)
    wav = os.path.join(tmp, "m.wav"); write_wav(wav, audio)

    inputs = ["-ss", str(start), "-t", str(dur), "-i", src, "-loop", "1", "-t", str(dur), "-i", os.path.join(tmp, "top.png")]
    for i in range(len(cards)):
        inputs += ["-loop", "1", "-t", str(dur), "-i", os.path.join(tmp, f"c{i}.png")]
    inputs += ["-i", wav]
    n = len(cards)
    fc = [
        # fond : la capture agrandie et floutée ; devant : la capture entière centrée
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:2,eq=brightness=-0.18[bg]",
        "[0:v]scale=1080:-2[fg]",
        "[bg][fg]overlay=(W-w)/2:(H-h)/2-140[base]",
        "[base][1:v]overlay=0:0[v0]",
    ]
    cur = "[v0]"
    for i in range(n):
        a0 = round(i * seg, 2)
        a1 = dur if i == n - 1 else round((i + 1) * seg, 2)
        fc.append(f"[{i+2}:v]format=rgba,fade=in:st={a0}:d=0.35:alpha=1[c{i}]")
        fc.append(f"{cur}[c{i}]overlay=0:1150:enable='between(t,{a0},{a1})'[w{i}]")
        cur = f"[w{i}]"
    fc.append(f"[{n+2}:a]afade=t=in:d=0.4,afade=t=out:st={max(0, dur-0.8)}:d=0.8[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc),
                    "-map", cur, "-map", "[a]", "-t", str(dur), "-r", "30",
                    "-c:v", "libx264", "-crf", "23", "-preset", "slow", "-maxrate", "12M", "-bufsize", "24M",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(min(dur - 0.5, seg + 1)), "-i", out,
                    "-frames:v", "1", os.path.splitext(out)[0] + "-apercu.jpg"], check=True)
    print("ok", out, "durée", dur, "musique", info, "(son du jeu coupé)")


if __name__ == "__main__":
    main()
