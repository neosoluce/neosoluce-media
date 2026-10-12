"""Générateur de musiques de fond originales pour les Reels NéoSoluce.

Chaque graine (seed) donne un morceau différent : style, tonalité, tempo, grille d'accords,
motif d'arpège et batterie changent, tout en restant dans l'ambiance néon / Miami / années 80.
Toute la musique est synthétisée ici : aucun échantillon externe, aucun droit d'auteur tiers.

Usage :
    from music import make_music, write_wav
    audio, info = make_music(seed=37, duration=8.0)
    write_wav("musique.wav", audio)
    python3 tools/music.py 37 8 sortie.wav   # en ligne de commande
"""
import sys, wave, random
import numpy as np
from scipy.signal import lfilter, butter

SR = 44100

STYLES = {
    # nom : (tempo min, tempo max, caractère)
    "synthwave": (104, 118),
    "outrun": (124, 138),
    "darkwave": (92, 104),
    "phonk": (128, 144),
    "chillwave": (82, 94),
    "retro-funk": (108, 116),
}
STYLE_NAMES_FR = {
    "synthwave": "synthwave néon",
    "outrun": "outrun (course de nuit)",
    "darkwave": "darkwave (ambiance polar)",
    "phonk": "phonk drift",
    "chillwave": "chillwave coucher de soleil",
    "retro-funk": "funk rétro années 80",
}
# grilles d'accords en degrés d'une gamme mineure naturelle (0 = tonique)
PROGRESSIONS = [
    [0, 5, 2, 6],   # i VI III VII
    [0, 6, 5, 6],   # i VII VI VII
    [0, 3, 5, 4],   # i iv VI v
    [0, 5, 3, 4],   # i VI iv v
    [0, 2, 6, 5],   # i III VII VI
    [5, 6, 0, 0],   # VI VII i i
]
MINOR = [0, 2, 3, 5, 7, 8, 10]


def hz(semi):  # demi-tons depuis La 440
    return 440.0 * 2 ** (semi / 12)


def lp(x, cutoff, order=2):
    b, a = butter(order, min(cutoff / (SR / 2), 0.99), "low")
    return lfilter(b, a, x)


def hp(x, cutoff, order=2):
    b, a = butter(order, min(cutoff / (SR / 2), 0.99), "high")
    return lfilter(b, a, x)


def saw(f, t):
    return 2 * ((f * t) % 1.0) - 1


def square(f, t, pw=0.5):
    return np.where((f * t) % 1.0 < pw, 1.0, -1.0)


def tri(f, t):
    return 2 * np.abs(2 * ((f * t) % 1.0) - 1) - 1


def env_adsr(n, a=0.01, d=0.1, s=0.6, r=0.1):
    t = np.arange(n) / SR
    L = n / SR
    e = np.where(t < a, t / max(a, 1e-4), np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-4), s))
    rel = np.clip((L - t) / max(r, 1e-4), 0, 1)
    return e * rel


def chord_notes(root, degree):
    idx = [degree, degree + 2, degree + 4]
    return [root + MINOR[i % 7] + 12 * (i // 7) for i in idx]


def add(buf, sig, start):
    s = int(start * SR)
    if s >= len(buf):
        return
    e = min(len(buf), s + len(sig))
    buf[s:e] += sig[: e - s]


def make_music(seed=0, duration=8.0, style=None):
    rng = random.Random(seed)
    style = style or list(STYLES)[seed % len(STYLES)]   # style différent d'un jour à l'autre
    lo, hi = STYLES[style]
    bpm = rng.randint(lo, hi)
    beat = 60 / bpm
    bar = 4 * beat
    root = rng.randint(-14, -7)          # tonique entre Si et Mi graves
    prog = rng.choice(PROGRESSIONS)
    n = int(SR * duration)
    pad = np.zeros(n); bass = np.zeros(n); lead = np.zeros(n); drums = np.zeros(n)
    nprng = np.random.default_rng(seed)
    bars = int(np.ceil(duration / bar)) + 1
    arp_pattern = rng.choice([[0, 1, 2, 1], [0, 2, 1, 2], [0, 1, 2, 3], [2, 1, 0, 1], [0, 0, 2, 1]])
    swing = 0.06 if style in ("chillwave", "retro-funk") else 0.0
    half_time = style in ("phonk", "darkwave")

    for b in range(bars):
        deg = prog[b % len(prog)]
        ch = chord_notes(root + 12, deg)
        t0 = b * bar
        # ---- nappe / accords
        L = int(bar * SR)
        t = np.arange(L) / SR
        if style == "chillwave":
            sig = sum(tri(hz(x), t) + 0.3 * np.sin(2 * np.pi * hz(x + 12) * t) for x in ch)
            e = env_adsr(L, 0.08, 0.6, 0.5, 0.3)
        elif style == "retro-funk":
            # accords staccato sur les contretemps
            sig = np.zeros(L); e = np.ones(L)
            for k in range(8):
                if k % 2 == 1 or rng.random() < 0.3:
                    s = int(k * beat / 2 * SR); m = int(beat * 0.22 * SR)
                    tt = np.arange(m) / SR
                    sig[s:s + m] += sum(square(hz(x), tt, 0.3) for x in ch) * env_adsr(m, 0.002, 0.08, 0.2, 0.03)
        else:
            sig = sum(saw(hz(x - 0.07), t) + saw(hz(x + 0.07), t) for x in ch)
            e = env_adsr(L, 0.3 if style != "outrun" else 0.05, 0.4, 0.75, 0.2)
        add(pad, sig * e * 0.05, t0)
        # ---- basse
        bn = root + MINOR[deg % 7] - 12
        if style == "phonk":
            # 808 longues avec glissando
            for k, pos in enumerate([0, 1.5, 2.5] if b % 2 == 0 else [0, 2, 3.25]):
                L2 = int(beat * 1.2 * SR); tt = np.arange(L2) / SR
                f = hz(bn) * (1 + 0.12 * np.exp(-tt * 12) * (1 if k == 0 else -0.5))
                ph = 2 * np.pi * np.cumsum(f) / SR
                add(bass, np.tanh(2.2 * np.sin(ph)) * np.exp(-tt * 1.6) * 0.45, t0 + pos * beat)
        else:
            step = beat / 2 if style in ("synthwave", "darkwave", "chillwave") else beat / 4
            if style == "retro-funk":
                step = beat / 2
            for k in range(int(bar / step)):
                if style == "chillwave" and k % 2:
                    continue
                if style == "retro-funk" and rng.random() < 0.25:
                    continue
                oct_ = 12 if (style == "synthwave" and k % 2) or (style == "retro-funk" and k % 4 == 3) else 0
                L2 = int(step * SR * 0.9); tt = np.arange(L2) / SR
                wave_ = saw(hz(bn + oct_), tt) if style != "chillwave" else np.sin(2 * np.pi * hz(bn) * tt)
                add(bass, wave_ * np.exp(-tt * (5 if style != "outrun" else 9)) * 0.38, t0 + k * step + (swing if k % 2 else 0))
        # ---- arpège / mélodie
        if b >= 1 or style in ("outrun", "chillwave"):
            if style == "phonk":
                # « cowbell » mélodique typique du phonk
                notes = [ch[0] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12]
                for k in range(8):
                    if k in (0, 3, 5, 6) or rng.random() < 0.2:
                        L3 = int(0.18 * SR); tt = np.arange(L3) / SR
                        f = hz(notes[k % 4])
                        sig = (square(f, tt) + square(f * 1.48, tt)) * np.exp(-tt * 22)
                        add(lead, sig * 0.06, t0 + k * beat / 2)
            elif style == "darkwave":
                for k in range(4):
                    L3 = int(beat * 0.9 * SR); tt = np.arange(L3) / SR
                    x = ch[arp_pattern[k] % 3] + 12
                    add(lead, square(hz(x), tt, 0.25) * env_adsr(L3, 0.01, 0.3, 0.3, 0.2) * 0.05, t0 + k * beat)
            else:
                step = beat / 4 if style in ("synthwave", "outrun") else beat / 2
                for k in range(int(bar / step)):
                    x = ch[arp_pattern[k % 4] % 3] + (12 if arp_pattern[k % 4] < 3 else 24)
                    L3 = int(step * SR); tt = np.arange(L3) / SR
                    w = square(hz(x), tt) if style != "chillwave" else np.sin(2 * np.pi * hz(x + 12) * tt)
                    add(lead, w * np.exp(-tt * (16 if style != "chillwave" else 6)) * 0.055,
                        t0 + k * step + (swing if k % 2 else 0))
        # ---- batterie
        for k in range(4):
            tb = t0 + k * beat
            kick = (k in (0, 2)) if half_time else True
            if style == "chillwave":
                kick = k in (0, 2)
            if kick:
                L4 = int(0.35 * SR); tt = np.arange(L4) / SR
                f = 42 + (130 if style != "phonk" else 90) * np.exp(-tt * 28)
                add(drums, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8) * 0.6, tb)
            snare_on = (k == 2) if half_time else (k % 2 == 1)
            if snare_on:
                L4 = int(0.3 * SR); tt = np.arange(L4) / SR
                nz = nprng.standard_normal(L4)
                sn = hp(nz, 1500) * np.exp(-tt * (18 if style != "outrun" else 9)) * 0.28 \
                    + np.sin(2 * np.pi * 185 * tt) * np.exp(-tt * 25) * 0.15
                if style in ("phonk", "chillwave"):  # clap
                    sn = hp(nz, 900) * (np.exp(-tt * 30) + 0.6 * np.exp(-np.abs(tt - 0.012) * 300)) * 0.3
                add(drums, sn, tb)
            # charleston
            subdiv = 4 if style in ("outrun", "phonk") else 2
            for h in range(subdiv):
                if style == "chillwave" and h == 0:
                    continue
                L5 = int(0.05 * SR)
                hn = hp(nprng.standard_normal(L5), 7000) * np.exp(-np.arange(L5) / SR * 70)
                vel = 0.12 if h % 2 else 0.07
                add(drums, hn * vel, tb + h * beat / subdiv + (swing if h % 2 else 0))
    # ---- mixage
    pad = lp(pad, {"chillwave": 1800, "darkwave": 1200}.get(style, 2600))
    bass = lp(bass, 500 if style != "phonk" else 300)
    lead = lp(lead, 4500)
    d = int(SR * beat * 0.75)                      # écho sur la mélodie
    lead[d:] += 0.35 * lead[:-d]
    mix = pad + bass + lead + drums
    if style == "chillwave":                       # léger souffle vinyle
        mix += lp(nprng.standard_normal(n) * 0.012, 3000)
    # intro douce et fin en fondu
    fi = int(0.25 * SR); fo = int(0.7 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo)
    mix = np.tanh(mix * 1.3)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.89
    info = {"style": style, "style_fr": STYLE_NAMES_FR[style], "bpm": bpm, "seed": seed}
    return mix.astype(np.float32), info


def write_wav(path, audio):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    dur = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
    out = sys.argv[3] if len(sys.argv) > 3 else "musique.wav"
    a, info = make_music(seed, dur)
    write_wav(out, a)
    print(info)
