"""
Carrusel 5 slides · Por qué pierdes clientes en tu inmobiliaria
1080×1350 · Dark cinematic · Bebas Neue + Inter · UI cards ✔/✖
Portada: foto REAL, composición referencia-1 (titular ARRIBA, cara visible).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
M = 56

YELLOW = (255, 220, 0)
WHITE = (255, 255, 255)
OFF = (210, 210, 210)
DARK = (12, 12, 14)
RED = (226, 59, 59)
GREEN = (34, 168, 90)
GRAY = (160, 160, 162)

BEBAS = FONTS / "BebasNeue-Regular.ttf"
INTER = FONTS / "Inter-opsz-wght.ttf"
OSWALD = FONTS / "Oswald-wght.ttf"

_DUMMY = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def bebas(size: int):
    return ImageFont.truetype(str(BEBAS), size)


def inter(size: int, weight: int = 400):
    f = ImageFont.truetype(str(INTER), size)
    opsz = max(14.0, min(32.0, size * 0.42))
    f.set_variation_by_axes([opsz, max(100, min(900, weight))])
    return f


def oswald(size: int, weight: int = 700):
    f = ImageFont.truetype(str(OSWALD), size)
    f.set_variation_by_axes([max(200, min(700, weight))])
    return f


def measure(text, fnt):
    bb = _DUMMY.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0], bb[3] - bb[1], bb[0], bb[1]


def txt(d, xy, s, fnt, fill):
    w, h, lb, tb = measure(s, fnt)
    d.text((xy[0] - lb, xy[1] - tb), s, font=fnt, fill=fill)
    return w, h


def fit_bebas(text: str, max_w: int, max_size: int, min_size: int = 40):
    size = max_size
    while size > min_size:
        f = bebas(size)
        if measure(text, f)[0] <= max_w:
            return f, size
        size -= 2
    return bebas(min_size), min_size


def wrap(text, fnt, max_w):
    out = []
    for para in text.split("\n"):
        if not para:
            out.append("")
            continue
        line = ""
        for w in para.split(" "):
            cand = (line + " " + w).strip()
            if measure(cand, fnt)[0] <= max_w:
                line = cand
            else:
                if line:
                    out.append(line)
                line = w
        if line:
            out.append(line)
    return out


def draw_wrapped(d, text, x, y, fnt, fill, max_w, lh=None):
    if lh is None:
        lh = int(fnt.size * 1.35)
    cy = y
    for ln in wrap(text, fnt, max_w):
        if ln:
            txt(d, (x, cy), ln, fnt, fill)
        cy += lh
    return cy


def rr(d, box, r, fill=None, outline=None, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def vignette(img: Image.Image, strength=0.62) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    # ellipse bigger than canvas so center stays open
    pad = int(min(W, H) * 0.08)
    md.ellipse([-pad, -int(H * 0.02), W + pad, H + int(H * 0.15)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(90))
    inv = Image.eval(mask, lambda p: int(255 - (255 - p) * strength))
    shade = Image.new("RGBA", img.size, (0, 0, 0, 255))
    # alpha = how much dark to add: 255-inv
    alpha = Image.eval(inv, lambda p: 255 - p)
    shade.putalpha(alpha)
    out = img.convert("RGBA")
    out.alpha_composite(shade)
    return out.convert("RGB")


def left_gradient(img: Image.Image, until=0.52, strength=0.86) -> Image.Image:
    g = Image.new("L", (W, 1), 0)
    gp = g.load()
    band = int(W * until)
    for x in range(W):
        t = x / max(1, band)
        if t < 1:
            a = int(255 * strength * max(0.0, (1 - t) ** 1.55))
        else:
            a = 0
        gp[x, 0] = a
    g = g.resize((W, H), Image.BILINEAR)
    shade = Image.new("RGBA", (W, H), (8, 8, 10, 255))
    shade.putalpha(g)
    out = img.convert("RGBA")
    out.alpha_composite(shade)
    return out.convert("RGB")


def grain(img: Image.Image, amount=0.05, seed=5) -> Image.Image:
    rng = random.Random(seed)
    noise = Image.new("L", (W, H))
    nd = noise.load()
    for yy in range(0, H, 2):
        for xx in range(0, W, 2):
            v = rng.randint(0, 40)
            nd[xx, yy] = v
            if xx + 1 < W:
                nd[xx + 1, yy] = v
            if yy + 1 < H:
                nd[xx, yy + 1] = v
            if xx + 1 < W and yy + 1 < H:
                nd[xx + 1, yy + 1] = v
    nrgb = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img.convert("RGB"), nrgb, amount)


def grade(img: Image.Image, dark=0.92, contrast=1.12):
    img = ImageEnhance.Brightness(img).enhance(dark)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(0.9)
    return img


def counter(d, n, total=5):
    label = f"{n}/{total}"
    f = inter(18, 600)
    tw, th, _, _ = measure(label, f)
    pad_x, pad_y = 16, 8
    x2, y1 = W - M, 40
    x1 = x2 - tw - pad_x * 2
    y2 = y1 + th + pad_y * 2
    rr(d, [x1, y1, x2, y2], 20, fill=(0, 0, 0))
    txt(d, (x1 + pad_x, y1 + pad_y), label, f, WHITE)


def footer_handle(d, handle):
    f = inter(18, 500)
    tw, _, _, _ = measure(handle, f)
    txt(d, ((W - tw) // 2, H - 48), handle, f, (170, 170, 172))


def icon_x(d, cx, cy, r=22):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    w = 3
    s = int(r * 0.42)
    d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=WHITE, width=w)
    d.line([(cx + s, cy - s), (cx - s, cy + s)], fill=WHITE, width=w)


def icon_check(d, cx, cy, r=22):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    w = 4
    d.line([(cx - 9, cy + 1), (cx - 2, cy + 9)], fill=WHITE, width=w)
    d.line([(cx - 2, cy + 9), (cx + 11, cy - 8)], fill=WHITE, width=w)


def ui_card(d, x, y, w, h, kind, title, body):
    if kind == "bad":
        fill = (32, 16, 16)
        outline = (140, 40, 40)
        icon = icon_x
    else:
        fill = (14, 32, 22)
        outline = (30, 130, 70)
        icon = icon_check
    rr(d, [x, y, x + w, y + h], 16, fill=fill, outline=outline, width=3)
    cy = y + h // 2
    icon(d, x + 44, cy, r=22)
    f_t = inter(24, 700)
    f_b = inter(18, 400)
    tx = x + 80
    tw = w - 100
    # title + body stacked, vertically centered
    lines_t = wrap(title, f_t, tw)
    lines_b = wrap(body, f_b, tw) if body else []
    block_h = len(lines_t) * 30 + (len(lines_b) * 24 if lines_b else 0)
    ty = y + (h - block_h) // 2
    for ln in lines_t:
        txt(d, (tx, ty), ln, f_t, WHITE)
        ty += 30
    for ln in lines_b:
        txt(d, (tx, ty), ln, f_b, (190, 190, 192))
        ty += 24
    return y + h


def place_cover_photo(photo: Image.Image) -> Image.Image:
    """Studio continuo (sin franja). Titular sobre el fondo, cara libre debajo."""
    ph = photo.convert("RGB")
    # color del estudio para extender el fondo hacia arriba sin corte
    samples = [ph.getpixel((x, 6)) for x in range(0, ph.width, 12)]
    avg = tuple(sum(c[i] for c in samples) // len(samples) for i in range(3))
    canvas = Image.new("RGB", (W, H), avg)

    scale = (W / ph.width) * 1.10
    nw, nh = int(ph.width * scale), int(ph.height * scale)
    ph = ph.resize((nw, nh), Image.LANCZOS)
    x = (W - nw) // 2
    y = H - nh + 8
    canvas.paste(ph, (x, y))

    # oscurecer SOLO el tercio superior, suave, para que el amarillo explote
    top = Image.new("L", (W, H), 0)
    td = ImageDraw.Draw(top)
    for yy in range(0, 340):
        a = int(150 * (1 - yy / 340) ** 1.15)
        td.line([(0, yy), (W, yy)], fill=a)
    shade = Image.new("RGBA", (W, H), (8, 8, 10, 255))
    shade.putalpha(top)
    canvas = canvas.convert("RGBA")
    canvas.alpha_composite(shade)
    canvas = grade(canvas.convert("RGB"), dark=0.94, contrast=1.12)
    canvas = vignette(canvas, 0.42)
    canvas = grain(canvas, 0.04, seed=2)
    return canvas


def place_right_photo(photo: Image.Image, shift=280) -> Image.Image:
    """Persona anclada a la derecha. El tercio izquierdo queda limpio para UI."""
    canvas = Image.new("RGB", (W, H), DARK)
    ph = photo.convert("RGB")
    scale = H / ph.height
    nw, nh = int(ph.width * scale), H
    ph = ph.resize((nw, nh), Image.LANCZOS)
    canvas.paste(ph, (shift, 0))
    canvas = grade(canvas, dark=0.86, contrast=1.12)
    canvas = left_gradient(canvas, until=0.50, strength=0.92)
    canvas = vignette(canvas, 0.35)
    canvas = grain(canvas, 0.04, seed=8)
    return canvas


def place_scene(photo: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", (W, H), DARK)
    ph = photo.convert("RGB")
    # cover
    src_ratio = ph.width / ph.height
    dst_ratio = W / H
    if src_ratio > dst_ratio:
        new_h = ph.height
        new_w = int(new_h * dst_ratio)
        left = (ph.width - new_w) // 2
        ph = ph.crop((left, 0, left + new_w, new_h))
    else:
        new_w = ph.width
        new_h = int(new_w / dst_ratio)
        top = int((ph.height - new_h) * 0.2)
        top = max(0, min(top, ph.height - new_h))
        ph = ph.crop((0, top, new_w, top + new_h))
    ph = ph.resize((W, H), Image.LANCZOS)
    canvas.paste(ph, (0, 0))
    canvas = grade(canvas, dark=0.78, contrast=1.12)
    canvas = left_gradient(canvas, until=0.58, strength=0.86)
    # extra top shade for headline
    top = Image.new("L", (W, H), 0)
    td = ImageDraw.Draw(top)
    for y in range(0, 360):
        a = int(160 * (1 - y / 360))
        td.line([(0, y), (W, y)], fill=a)
    shade = Image.new("RGBA", (W, H), (8, 8, 10, 255))
    shade.putalpha(top)
    canvas = canvas.convert("RGBA")
    canvas.alpha_composite(shade)
    canvas = grain(canvas.convert("RGB"), 0.04, seed=3)
    return canvas


def draw_headline(d, lines, y, max_w, fill=YELLOW, max_size=140):
    cy = y
    for i, line in enumerate(lines):
        # last line can be bigger
        ms = max_size + (18 if i == len(lines) - 1 else 0)
        f, sz = fit_bebas(line, max_w, ms, 48)
        wh = measure(line, f)[1]
        txt(d, (M, cy), line, f, fill)
        cy += int(sz * 0.92)
    return cy


def slide_cover(s, handle):
    img = place_cover_photo(Image.open(ROOT / s["foto"]))
    d = ImageDraw.Draw(img)
    counter(d, s["slide_numero"])

    lines = s["texto"]["titular_lineas"]
    y = 56
    # line 1 slightly smaller, line 2 hero
    f1, sz1 = fit_bebas(lines[0], W - 2 * M, 92, 56)
    txt(d, (M, y), lines[0], f1, YELLOW)
    y += int(sz1 * 0.90)
    f2, sz2 = fit_bebas(lines[1], W - 2 * M, 168, 80)
    txt(d, (M, y), lines[1], f2, YELLOW)

    # subtitle over the torso
    sub = s["texto"]["subtitulo_o_bajada"]
    f_sub = inter(28, 500)
    draw_wrapped(d, sub, M, 980, f_sub, WHITE, W - 2 * M, lh=38)

    # yellow bar + bullets
    bullets = s["texto"]["bullets"]
    bx, by = M, 1108
    d.rectangle([bx, by, bx + 5, by + 90], fill=YELLOW)
    f_b = inter(20, 500)
    cy = by
    for b in bullets:
        txt(d, (bx + 18, cy), b, f_b, WHITE)
        cy += 30

    footer_handle(d, handle)
    return img


def slide_error(s, handle):
    layout = s.get("foto_layout", "right_fade")
    photo = Image.open(ROOT / s["foto"])
    if layout == "scene_left_text":
        img = place_scene(photo)
    else:
        img = place_right_photo(photo, shift=300)
    d = ImageDraw.Draw(img)
    counter(d, s["slide_numero"])

    y = 70
    y = draw_headline(d, s["texto"]["titular_lineas"], y, 640, YELLOW, 108)

    f_sub = inter(26, 500)
    y = draw_wrapped(d, s["texto"]["subtitulo_o_bajada"], M, y + 10, f_sub, WHITE, 520, lh=36)
    y += 28

    cards = s["texto"].get("cards") or []
    card_w = 500
    card_h = 144
    for c in cards:
        ui_card(d, M, y, card_w, card_h, c["kind"], c["title"], c.get("body", ""))
        y += card_h + 16

    punch = s["texto"].get("punchline") or ""
    if punch:
        f_p = inter(24, 600)
        draw_wrapped(d, punch, M, min(y + 18, H - 120), f_p, YELLOW, 500, lh=34)

    footer_handle(d, handle)
    return img


def slide_cta(s, handle):
    img = place_right_photo(Image.open(ROOT / s["foto"]), shift=0)
    d = ImageDraw.Draw(img)
    counter(d, s["slide_numero"])

    y = 80
    y = draw_headline(d, s["texto"]["titular_lineas"], y, 520, YELLOW, 120)

    f_sub = inter(26, 500)
    y = draw_wrapped(d, s["texto"]["subtitulo_o_bajada"], M, y + 12, f_sub, WHITE, 600, lh=36)
    y += 36

    # CTA button yellow
    cta = s["texto"]["cta"]
    f_btn = bebas(42)
    tw, th, _, _ = measure(cta, f_btn)
    pad_x, pad_y = 36, 18
    bw, bh = tw + pad_x * 2, th + pad_y * 2
    rr(d, [M, y, M + bw, y + bh], 8, fill=YELLOW)
    txt(d, (M + pad_x, y + pad_y), cta, f_btn, (16, 16, 16))
    y += bh + 28

    f_sub2 = inter(22, 400)
    y = draw_wrapped(d, s["texto"]["sub_cta"], M, y, f_sub2, OFF, 600, lh=32)

    nota = s["texto"].get("nota") or ""
    if nota:
        f_n = inter(18, 500)
        txt(d, (M, H - 88), nota, f_n, YELLOW)

    footer_handle(d, handle)
    return img


def render_all():
    data = json.loads((ROOT / "guion.json").read_text())
    c = data["carrusel"]
    handle = c.get("handle", "@hexa.inmo")
    for s in c["diapositivas"]:
        t = s["tipo"]
        if t == "Portada":
            img = slide_cover(s, handle)
        elif t == "CTA":
            img = slide_cta(s, handle)
        else:
            img = slide_error(s, handle)
        dest = OUT / f"slide-{s['slide_numero']:02d}.png"
        img.save(dest, "PNG", optimize=True)
        print(f"✓ {dest.name}  ({t})")
    print(f"→ {OUT}")


if __name__ == "__main__":
    render_all()
