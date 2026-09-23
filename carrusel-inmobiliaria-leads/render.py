"""
HEXA · Carrusel inmobiliario «¿Cuánto te cuesta una consulta sin responder?»

1080×1350 PNG · tokens HEXA (design-tokens.json) · estética Organizagram:
palabra héroe en Playfair italic, foto full-bleed con overlay, pills/tags,
anatomy-callouts, dual tipografía Manrope (títulos) + Inter (cuerpo).

Cobre #C46A32 → acción y palabra héroe (marca primaria).
Azul  #2F90C9 → dato / destacado (nunca CTA).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "assets" / "fonts"
ASSETS = ROOT / "assets"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
M = 72
FOOTER_LINE_Y = 1266
FOOTER_TEXT_Y = 1286

# HEXA tokens
BG = (245, 244, 241)
WHITE = (255, 255, 255)
GRAPHITE = (47, 52, 58)
GRAY = (90, 96, 104)
MUTED = (160, 162, 166)
COPPER = (196, 106, 50)
BLUE = (47, 144, 201)
BORDER = (226, 224, 220)
INK = (18, 18, 20)

MANROPE = FONTS / "Manrope-wght.ttf"
INTER = FONTS / "Inter-opsz-wght.ttf"
INTER_I = FONTS / "Inter-Italic-opsz-wght.ttf"
PLAYFAIR = FONTS / "PlayfairDisplay-wght.ttf"
PLAYFAIR_I = FONTS / "PlayfairDisplay-Italic-wght.ttf"

_DUMMY = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def F(kind: str, size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    """kind: manrope | inter | interi | playfair | playfairi"""
    if kind == "manrope":
        f = ImageFont.truetype(str(MANROPE), size)
        f.set_variation_by_axes([max(200, min(800, weight))])
        return f
    if kind == "inter":
        f = ImageFont.truetype(str(INTER), size)
        opsz = max(14.0, min(32.0, size * 0.42))
        f.set_variation_by_axes([opsz, max(100, min(900, weight))])
        return f
    if kind == "interi":
        f = ImageFont.truetype(str(INTER_I), size)
        opsz = max(14.0, min(32.0, size * 0.42))
        f.set_variation_by_axes([opsz, max(100, min(900, weight))])
        return f
    if kind == "playfair":
        f = ImageFont.truetype(str(PLAYFAIR), size)
        f.set_variation_by_axes([max(400, min(900, weight))])
        return f
    if kind == "playfairi":
        f = ImageFont.truetype(str(PLAYFAIR_I), size)
        f.set_variation_by_axes([max(400, min(900, weight))])
        return f
    raise ValueError(kind)


def measure(text: str, fnt) -> tuple[int, int, int, int]:
    bb = _DUMMY.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0], bb[3] - bb[1], bb[0], bb[1]


def txt(d, xy, s, fnt, fill) -> tuple[int, int]:
    """Draw so (x, y) is the visual top-left of the ink."""
    w, h, lb, tb = measure(s, fnt)
    d.text((xy[0] - lb, xy[1] - tb), s, font=fnt, fill=fill)
    return w, h


def wrap(text: str, fnt, max_w: int) -> list[str]:
    out: list[str] = []
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


def draw_wrapped(d, text, x, y, fnt, fill, max_w, lh=None, align="left") -> int:
    if lh is None:
        lh = int(fnt.size * 1.45)
    lines = wrap(text, fnt, max_w)
    cy = y
    for ln in lines:
        if not ln:
            cy += lh // 2
            continue
        if align == "center":
            lw = measure(ln, fnt)[0]
            cx = x + (max_w - lw) // 2
        else:
            cx = x
        txt(d, (cx, cy), ln, fnt, fill)
        cy += lh
    return cy


def rr(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def hand_underline(d, x1, y, x2, color, width=5, jitter=2.4, seed=3):
    rng = random.Random(seed)
    steps = max(12, (x2 - x1) // 8)
    pts = []
    for i in range(steps + 1):
        t = i / steps
        pts.append((x1 + (x2 - x1) * t, y + rng.uniform(-jitter, jitter)))
    if len(pts) >= 2:
        d.line(pts, fill=color, width=width, joint="curve")


def pill(d, text, x, y, *, fill=None, outline=None, text_fill=WHITE, size=18, weight=700, pad_x=16, pad_y=9):
    fnt = F("manrope", size, weight)
    tw, th, _, _ = measure(text, fnt)
    w = tw + pad_x * 2
    h = th + pad_y * 2
    rr(d, [x, y, x + w, y + h], 4, fill=fill, outline=outline, width=2)
    txt(d, (x + pad_x, y + pad_y), text, fnt, text_fill)
    return w, h


def brand(d, on_dark=False):
    col = WHITE if on_dark else GRAPHITE
    f = F("manrope", 20, 800)
    tw, th, _, _ = measure("HEXA", f)
    x = W - M - tw - 18
    txt(d, (x, 78), "HEXA", f, col)
    d.rectangle([W - M - 10, 84, W - M, 94], fill=COPPER)


def footer(d, n, total=9, dark=False):
    col = (190, 190, 192) if dark else GRAY
    line = (70, 70, 74) if dark else BORDER
    d.line([(M, FOOTER_LINE_Y), (W - M, FOOTER_LINE_Y)], fill=line, width=1)
    f = F("inter", 18, 500)
    txt(d, (M, FOOTER_TEXT_Y), f"{n:02d}  /  {total:02d}", f, col)
    handle = "@hexa.inmo"
    hw = measure(handle, f)[0]
    txt(d, (W - M - hw, FOOTER_TEXT_Y), handle, f, col)


def grain(img: Image.Image, amount=0.06, seed=7) -> Image.Image:
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


def offwhite() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    return grain(img, 0.045, seed=4)


def fit_word(text: str, max_w: int, max_size=220, min_size=96, weight=700):
    size = max_size
    while size > min_size:
        f = F("playfairi", size, weight)
        if measure(text, f)[0] <= max_w:
            return f, size
        size -= 4
    return F("playfairi", min_size, weight), min_size


def cover_crop(src: Image.Image, bias: float = 0.65) -> Image.Image:
    """Cover-crop to 1080×1350. bias 0 = keep left, 1 = keep right (face)."""
    img = src.convert("RGB")
    src_ratio = img.width / img.height
    dst_ratio = W / H
    if src_ratio > dst_ratio:
        new_h = img.height
        new_w = int(new_h * dst_ratio)
        left = int((img.width - new_w) * bias)
        left = max(0, min(left, img.width - new_w))
        img = img.crop((left, 0, left + new_w, new_h))
    else:
        new_w = img.width
        new_h = int(new_w / dst_ratio)
        top = int((img.height - new_h) * 0.15)
        top = max(0, min(top, img.height - new_h))
        img = img.crop((0, top, new_w, top + new_h))
    return img.resize((W, H), Image.LANCZOS)


def portrait_bg(path: Path, *, darken=0.55, bias=0.7, left_shade=0.0, warm=0.14) -> Image.Image:
    img = cover_crop(Image.open(path), bias=bias)
    img = ImageEnhance.Color(img).enhance(0.92)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    if warm:
        tint = Image.new("RGB", (W, H), (70, 32, 12))
        img = Image.blend(img, tint, warm)
    img = img.convert("RGBA")
    # overall darken
    img.alpha_composite(Image.new("RGBA", (W, H), (8, 8, 10, int(255 * darken))))
    if left_shade > 0:
        g = Image.new("L", (W, 1), 0)
        gp = g.load()
        band = int(W * 0.68)
        for x in range(W):
            if x < band:
                a = int(255 * left_shade * (1 - (x / band) * 0.78))
            else:
                a = int(255 * left_shade * 0.12)
            gp[x, 0] = a
        g = g.resize((W, H), Image.BILINEAR)
        shade = Image.new("RGBA", (W, H), (8, 8, 10, 255))
        shade.putalpha(g)
        img.alpha_composite(shade)
    # bottom fade for footer
    bg = Image.new("L", (1, H), 0)
    bp = bg.load()
    for y in range(H):
        if y > H - 220:
            bp[0, y] = int(180 * ((y - (H - 220)) / 220))
        else:
            bp[0, y] = 0
    bg = bg.resize((W, H), Image.BILINEAR)
    bot = Image.new("RGBA", (W, H), (8, 8, 10, 255))
    bot.putalpha(bg)
    img.alpha_composite(bot)
    return grain(img.convert("RGB"), 0.05, seed=11)


# ---------- slides ----------

def slide_cover(s, portrait: Path) -> Image.Image:
    img = portrait_bg(portrait, darken=0.28, bias=0.78, left_shade=0.72, warm=0.12)
    d = ImageDraw.Draw(img)

    pill(
        d, s["eyebrow"], M, 78,
        outline=COPPER, text_fill=COPPER, size=15, weight=700, pad_x=14, pad_y=8,
    )
    brand(d, on_dark=True)

    y = 200
    f_top = F("manrope", 44, 700)
    h1 = s["title_top"]
    txt(d, (M, y), h1, f_top, WHITE)
    y += measure(h1, f_top)[1] + 8

    # palabra héroe a la izquierda para no tapar los ojos
    word = s["display_word"]
    f_word, _ = fit_word(word, 700, max_size=188, min_size=120, weight=700)
    ww, wh, _, _ = measure(word, f_word)
    txt(d, (M, y), word, f_word, COPPER)
    hand_underline(d, M, y + wh + 6, M + min(ww, 480), COPPER, width=6, jitter=2.2, seed=2)
    y += wh + 32

    f_bot = F("manrope", 46, 700)
    txt(d, (M, y), s["title_bottom"], f_bot, WHITE)
    y += measure(s["title_bottom"], f_bot)[1] + 28

    f_cap = F("inter", 26, 400)
    draw_wrapped(d, s["caption"], M, y, f_cap, (210, 210, 212), 560, lh=38)

    f_sw = F("manrope", 16, 700)
    txt(d, (M, FOOTER_LINE_Y - 42), "DESLIZA  →", f_sw, MUTED)

    footer(d, s["n"], dark=True)
    return img


def slide_stat(s) -> Image.Image:
    img = offwhite()
    d = ImageDraw.Draw(img)

    # data eyebrow → azul (dato, no acción)
    pill(
        d, s["eyebrow"], M, 78,
        fill=BLUE, text_fill=WHITE, size=15, weight=700, pad_x=14, pad_y=8,
    )
    brand(d)

    y = 190
    number = s["number"]
    max_size = 200 if len(number) > 4 else 260
    f_n, _ = fit_word(number, W - 2 * M, max_size=max_size, min_size=140, weight=700)
    nw, nh, _, _ = measure(number, f_n)
    txt(d, (M, y), number, f_n, BLUE)
    y += nh + 18

    f_h = F("manrope", 48, 700)
    hy = draw_wrapped(d, s["headline"], M, y, f_h, GRAPHITE, W - 2 * M, lh=60)

    f_b = F("inter", 28, 400)
    draw_wrapped(d, s["body"], M, hy + 28, f_b, GRAY, W - 2 * M, lh=42)

    d.line([(M, FOOTER_LINE_Y - 88), (W - M, FOOTER_LINE_Y - 88)], fill=BORDER, width=1)
    f_q = F("playfairi", 26, 500)
    quotes = {
        2: "Si tú no respondes en 5 minutos, otro lo hará.",
        5: "Pasados 5 minutos, no estás compitiendo. Ya perdiste.",
    }
    quote = quotes.get(s["n"], quotes[2])
    txt(d, (M, FOOTER_LINE_Y - 70), quote, f_q, COPPER)

    footer(d, s["n"])
    return img


def slide_dark_image(s, portrait: Path) -> Image.Image:
    # full-bleed retrato, overlay oscuro — look Organizagram
    biases = {3: 0.84, 4: 0.70, 7: 0.90}
    darkens = {3: 0.62, 4: 0.58, 7: 0.64}
    img = portrait_bg(
        portrait,
        darken=darkens.get(s["n"], 0.62),
        bias=biases.get(s["n"], 0.82),
        left_shade=0.55,
        warm=0.16,
    )
    d = ImageDraw.Draw(img)

    pill(
        d, s["eyebrow"], M, 78,
        outline=COPPER, text_fill=COPPER, size=15, weight=700, pad_x=14, pad_y=8,
    )
    brand(d, on_dark=True)

    y = 200
    f_title = F("manrope", 52, 700)
    txt(d, (M, y), s["title"], f_title, WHITE)
    y += measure(s["title"], f_title)[1] + 4

    word = s["display_word"]
    f_word, _ = fit_word(word, W - 2 * M, max_size=200, min_size=110, weight=700)
    ww, wh, _, _ = measure(word, f_word)
    txt(d, (M, y), word, f_word, COPPER)
    hand_underline(d, M, y + wh + 4, M + min(ww, 480), COPPER, width=5, jitter=2, seed=s["n"])
    y += wh + 36

    f_b = F("inter", 28, 400)
    # leave room for two callout pills
    body_bottom = H - 340
    lines = wrap(s["body"], f_b, W - 2 * M)
    cy = y
    for ln in lines:
        if cy + 40 > body_bottom:
            break
        txt(d, (M, cy), ln, f_b, (220, 220, 222))
        cy += 42

    def callout_row(text, cx, cy, fill):
        f_c = F("manrope", 18, 700)
        tw, th, _, _ = measure(text, f_c)
        pad_x, pad_y = 16, 11
        rr(d, [cx, cy, cx + tw + pad_x * 2, cy + th + pad_y * 2], 4, fill=fill)
        txt(d, (cx + pad_x, cy + pad_y), text, f_c, WHITE)
        # pin
        pin_x = cx + 22
        pin_y = cy - 16
        d.line([(pin_x, cy), (pin_x, pin_y)], fill=fill, width=2)
        d.ellipse([pin_x - 5, pin_y - 5, pin_x + 5, pin_y + 5], fill=fill)

    cot_top = s.get("callout_top") or ""
    cot_bot = s.get("callout_bot") or ""
    if cot_top:
        callout_row(cot_top, M, H - 292, COPPER)
    if cot_bot:
        callout_row(cot_bot, M, H - 214, (58, 58, 62))

    footer(d, s["n"], dark=True)
    return img


def slide_portrait_anatomy(s, portrait: Path) -> Image.Image:
    """Retrato full-bleed + anatomy callouts (feed 2x1 «+Leads / +Vendas»)."""
    img = portrait_bg(portrait, darken=0.50, bias=0.88, left_shade=0.70, warm=0.12)
    d = ImageDraw.Draw(img)

    pill(
        d, s["eyebrow"], M, 78,
        outline=COPPER, text_fill=COPPER, size=15, weight=700, pad_x=14, pad_y=8,
    )
    brand(d, on_dark=True)

    y = 168
    f_t = F("manrope", 40, 700)
    y = draw_wrapped(d, s["title"], M, y, f_t, WHITE, 640, lh=50)

    colors = [COPPER, BLUE, (220, 220, 222)]
    f_lab = F("manrope", 24, 800)
    f_tx = F("inter", 22, 400)
    # callouts sobre el pecho/hombro, no cruzando los ojos
    cy = max(y + 28, 500)
    targets_x = [720, 780, 700]
    for i, pt in enumerate(s["points"]):
        col = colors[i % len(colors)]
        txt(d, (M, cy), pt["label"], f_lab, col)
        lw = measure(pt["label"], f_lab)[0]
        line_y = cy + measure(pt["label"], f_lab)[1] // 2
        x1 = M + lw + 16
        x2 = targets_x[i]
        d.line([(x1, line_y), (x2, line_y)], fill=col, width=2)
        d.ellipse([x2 - 6, line_y - 6, x2 + 6, line_y + 6], fill=col)
        cy += 30
        cy = draw_wrapped(d, pt["text"], M, cy, f_tx, (200, 200, 202), 500, lh=32)
        cy += 26

    footer(d, s["n"], dark=True)
    return img


def slide_checklist(s) -> Image.Image:
    img = offwhite()
    d = ImageDraw.Draw(img)

    pill(
        d, s["eyebrow"], M, 78,
        fill=GRAPHITE, text_fill=WHITE, size=15, weight=700, pad_x=14, pad_y=8,
    )
    brand(d)

    y = 170
    f_t = F("manrope", 44, 700)
    y = draw_wrapped(d, s["title"], M, y, f_t, GRAPHITE, W - 2 * M, lh=56)
    y += 28

    f_num = F("playfairi", 42, 700)
    f_item = F("manrope", 26, 600)
    card_h = 148
    for item in s["items"]:
        rr(d, [M, y, W - M, y + card_h], 8, fill=WHITE, outline=BORDER, width=1)
        # left copper bar (acción: las reglas)
        d.rectangle([M, y, M + 6, y + card_h], fill=COPPER)
        ntxt = item["num"]
        nw, nh, _, _ = measure(ntxt, f_num)
        txt(d, (M + 36, y + (card_h - nh) // 2), ntxt, f_num, COPPER)
        draw_wrapped(d, item["text"], M + 130, y + 44, f_item, GRAPHITE, W - M - 160, lh=36)
        y += card_h + 16

    f_q = F("playfairi", 24, 500)
    txt(d, (M, y + 12), "Tres reglas. Cero excusas.", f_q, COPPER)

    footer(d, s["n"])
    return img


def slide_cta(s, portrait: Path) -> Image.Image:
    img = offwhite()
    d = ImageDraw.Draw(img)

    # circular headshot
    ph = Image.open(portrait).convert("RGB")
    size = 196
    # crop square around face (right-center of original)
    side = min(ph.size)
    left = ph.width - side
    top = 0
    ph = ph.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    # copper ring
    ring = Image.new("RGBA", (size + 10, size + 10), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([0, 0, size + 9, size + 9], outline=COPPER + (255,), width=4)
    circle = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    circle.paste(ph, (0, 0), mask)
    img_rgba = img.convert("RGBA")
    img_rgba.paste(ring, (W - M - size - 5, 72), ring)
    img_rgba.paste(circle, (W - M - size, 77), circle)
    img = img_rgba.convert("RGB")
    d = ImageDraw.Draw(img)

    pill(
        d, s["eyebrow"], M, 78,
        fill=COPPER, text_fill=WHITE, size=15, weight=700, pad_x=14, pad_y=8,
    )

    y = 200
    f_t = F("manrope", 48, 700)
    y = draw_wrapped(d, s["title_top"], M, y, f_t, GRAPHITE, W - 2 * M - 40, lh=60)

    # punchline: last clause in Playfair italic copper
    bottom = s["title_bottom"]
    # split so «no más suerte.» is the hero if present
    if ", no más" in bottom:
        pre, punch = bottom.split(", ", 1)
        f_pre = F("manrope", 40, 600)
        y = draw_wrapped(d, pre + ",", M, y + 4, f_pre, GRAPHITE, W - 2 * M, lh=52)
        f_punch, _ = fit_word(punch, W - 2 * M, max_size=92, min_size=56, weight=700)
        pw, ph_, _, _ = measure(punch, f_punch)
        txt(d, (M, y + 8), punch, f_punch, COPPER)
        hand_underline(d, M, y + 8 + ph_ + 4, M + min(pw, 640), COPPER, width=5, jitter=2, seed=9)
        y = y + 8 + ph_ + 36
    else:
        f_word, _ = fit_word(bottom, W - 2 * M, max_size=72, min_size=42, weight=700)
        ww, wh, _, _ = measure(bottom, f_word)
        txt(d, (M, y + 6), bottom, f_word, COPPER)
        y = y + wh + 36

    # CTA button — único bloque cobre sólido de acción
    f_btn = F("manrope", 28, 700)
    btn = s["cta_text"]
    btw, bth, _, _ = measure(btn, f_btn)
    pad_x, pad_y = 40, 22
    btn_w, btn_h = btw + pad_x * 2, bth + pad_y * 2
    bx, by = M, y
    rr(d, [bx, by, bx + btn_w, by + btn_h], 4, fill=COPPER)
    txt(d, (bx + pad_x, by + pad_y), btn, f_btn, WHITE)
    # arrow
    ax = bx + btn_w + 24
    ay = by + btn_h // 2
    d.line([(ax, ay), (ax + 64, ay)], fill=COPPER, width=4)
    d.polygon([(ax + 64, ay - 9), (ax + 84, ay), (ax + 64, ay + 9)], fill=COPPER)

    y = by + btn_h + 28
    f_sub = F("inter", 24, 400)
    draw_wrapped(d, s["sub_cta"], M, y, f_sub, GRAY, W - 2 * M, lh=36)

    f_note = F("playfairi", 22, 500)
    note = "Sin reunión de venta. Sin compromiso. Respuesta en 24h."
    nw = measure(note, f_note)[0]
    nx = (W - nw) // 2
    txt(d, (nx, FOOTER_LINE_Y - 52), note, f_note, COPPER)
    hand_underline(d, nx, FOOTER_LINE_Y - 26, nx + nw, COPPER, width=3, jitter=1.6, seed=5)

    footer(d, s["n"])
    return img


def make_grid():
    gap = 18
    cw, ch = 360, 450
    cols, rows = 3, 3
    gw = cols * cw + (cols + 1) * gap
    gh = rows * ch + (rows + 1) * gap
    canvas = Image.new("RGB", (gw, gh), (28, 28, 30))
    for i in range(9):
        r, c = divmod(i, 3)
        p = OUT / f"slide-{i + 1:02d}.png"
        im = Image.open(p).resize((cw, ch), Image.LANCZOS)
        canvas.paste(im, (gap + c * (cw + gap), gap + r * (ch + gap)))
    canvas.save(OUT / "feed-grid.png", "PNG", optimize=True)
    print("✓ feed-grid.png")


def render_all(copy_path: Path, portrait_path: Path):
    copy = json.loads(copy_path.read_text())
    for s in copy["slides"]:
        t = s["type"]
        if t == "cover":
            img = slide_cover(s, portrait_path)
        elif t == "stat":
            img = slide_stat(s)
        elif t == "dark_image":
            img = slide_dark_image(s, portrait_path)
        elif t == "portrait_anatomy":
            img = slide_portrait_anatomy(s, portrait_path)
        elif t == "checklist_light":
            img = slide_checklist(s)
        elif t == "cta":
            img = slide_cta(s, portrait_path)
        else:
            continue
        dest = OUT / f"slide-{s['n']:02d}.png"
        img.save(dest, "PNG", optimize=True)
        print(f"✓ {dest.name}  ({t})")
    make_grid()
    print(f"\n→ {OUT}")


if __name__ == "__main__":
    render_all(ROOT / "copy.json", ASSETS / "portrait.jpg")
