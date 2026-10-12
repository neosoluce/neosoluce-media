from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import os

OUT = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts"

def find(name):
    for root, _, files in os.walk(FD):
        if name in files:
            return os.path.join(root, name)
    raise FileNotFoundError(name)

BLACK_IT = find("InterDisplay-BlackItalic.otf")
BOLD_IT = find("InterDisplay-BoldItalic.otf")

PINK = (255, 61, 154)
CYAN = (45, 226, 230)
YELLOW = (255, 209, 102)
ORANGE = (255, 122, 89)
NIGHT = (15, 8, 38)


def sun(size, stripes_color=NIGHT, transparent_stripes=True):
    """Retro striped sunset sun, yellow -> orange -> pink."""
    s = size
    grad = Image.new("RGBA", (s, s))
    gd = ImageDraw.Draw(grad)
    for y in range(s):
        t = y / (s - 1)
        if t < 0.55:
            k = t / 0.55
            c = tuple(int(YELLOW[i] + (ORANGE[i] - YELLOW[i]) * k) for i in range(3))
        else:
            k = (t - 0.55) / 0.45
            c = tuple(int(ORANGE[i] + (PINK[i] - ORANGE[i]) * k) for i in range(3))
        gd.line([(0, y), (s, y)], fill=c + (255,))
    mask = Image.new("L", (s, s), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, s - 1, s - 1], fill=255)
    # horizontal cut stripes on the lower half, getting thicker
    stripes = [(0.58, 0.035), (0.68, 0.05), (0.79, 0.065), (0.90, 0.08)]
    for top, h in stripes:
        md.rectangle([0, int(s * top), s, int(s * (top + h))], fill=0)
    grad.putalpha(mask)
    return grad


def glow(layer, radius, strength=2):
    g = layer.filter(ImageFilter.GaussianBlur(radius))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    for _ in range(strength):
        out = Image.alpha_composite(out, g)
    return out


def text_layer(size, text, font, color, pos, tracking=0):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = pos
    for ch in text:
        d.text((x, y), ch, font=font, fill=color + (255,))
        x += d.textlength(ch, font=font) + tracking
    return layer, x


def neon(layer, color):
    """Neon tube look: colored glow + bright core."""
    base = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    base = Image.alpha_composite(base, glow(layer, 18, 2))
    base = Image.alpha_composite(base, glow(layer, 6, 2))
    base = Image.alpha_composite(base, layer)
    # whitish core: shrink the letter slightly and lighten
    core = layer.filter(ImageFilter.MinFilter(5))
    r, g, b, a = core.split()
    light = Image.new("RGBA", layer.size, tuple(min(255, c + 120) for c in color) + (0,))
    light.putalpha(ImageChops.multiply(a, Image.new("L", layer.size, 170)))
    return Image.alpha_composite(base, light)


def wordmark(scale=1, with_bg=False):
    W, H = int(1700 * scale), int(360 * scale)
    canvas = Image.new("RGBA", (W, H), NIGHT + (255,) if with_bg else (0, 0, 0, 0))
    # emblem, glow computed on a full-canvas layer so it is not clipped
    s = int(250 * scale)
    em = sun(s)
    ex, ey = int(50 * scale), (H - s) // 2
    em_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    em_layer.alpha_composite(em, (ex, ey))
    canvas = Image.alpha_composite(canvas, glow(em_layer, int(20 * scale), 1))
    canvas = Image.alpha_composite(canvas, em_layer)
    # text
    f1 = ImageFont.truetype(BLACK_IT, int(190 * scale))
    f2 = ImageFont.truetype(BOLD_IT, int(150 * scale))
    tx = ex + s + int(55 * scale)
    asc1 = f1.getbbox("NÉO")
    ty = (H - (asc1[3] - asc1[1])) // 2 - asc1[1] + int(6 * scale)
    neo, x_end = text_layer((W, H), "NÉO", f1, PINK, (tx, ty), tracking=int(4 * scale))
    canvas = Image.alpha_composite(canvas, neon(neo, PINK))
    asc2 = f2.getbbox("SOLUCE")
    ty2 = ty + (asc1[3] - asc2[3])  # align baselines
    sol, x_end2 = text_layer((W, H), "SOLUCE", f2, CYAN, (x_end + int(22 * scale), ty2), tracking=int(10 * scale))
    canvas = Image.alpha_composite(canvas, neon(sol, CYAN))
    # crop to content with margin
    bbox = canvas.getbbox() if not with_bg else (0, 0, int(x_end2 + 60 * scale), H)
    if not with_bg:
        m = int(10 * scale)
        bbox = (max(0, bbox[0] - m), max(0, bbox[1] - m), min(W, bbox[2] + m), min(H, bbox[3] + m))
    return canvas.crop(bbox)


def icon(size=512):
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    bg = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=NIGHT + (255,))
    img = Image.alpha_composite(img, bg)
    es = int(s * 0.74)
    em = sun(es)
    off = ((s - es) // 2, (s - es) // 2)
    layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    layer.alpha_composite(em, off)
    img = Image.alpha_composite(img, glow(layer, int(s * 0.03), 1))
    img = Image.alpha_composite(img, layer)
    # neon N on top of the sun
    f = ImageFont.truetype(BLACK_IT, int(s * 0.56))
    bb = f.getbbox("N")
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    n, _ = text_layer((s, s), "N", f, CYAN, ((s - w) // 2 - bb[0], (s - h) // 2 - bb[1] - int(s * 0.02)))
    img = Image.alpha_composite(img, neon(n, CYAN))
    # keep rounded corners clean
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=255)
    img.putalpha(ImageChops.multiply(img.getchannel("A"), mask))
    return img


if __name__ == "__main__":
    wm = wordmark(1)
    wm.save(os.path.join(OUT, "neosoluce-logo.png"))
    prev = Image.new("RGBA", (wm.width + 80, wm.height + 80), NIGHT + (255,))
    prev.alpha_composite(wm, (40, 40))
    prev.save(os.path.join(OUT, "preview-logo-sur-fond.png"))
    ic = icon(512)
    ic.save(os.path.join(OUT, "neosoluce-icone.png"))
    print(wm.size, ic.size)
