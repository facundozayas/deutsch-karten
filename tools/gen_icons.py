#!/usr/bin/env python3
"""Genera los íconos PWA (192, 512, 512 maskable, apple-touch-icon)."""
from PIL import Image, ImageDraw, ImageFont

BG = (108, 140, 255)       # --accent
BG_DARK = (15, 17, 21)     # --bg (fondo detrás del glifo, para contraste sutil)
WHITE = (255, 255, 255)
FLAG_BLACK = (20, 20, 22)
FLAG_RED = (222, 41, 44)
FLAG_GOLD = (255, 206, 0)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def draw_icon(size, maskable=False, opaque=True):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fondo: rounded square (o full-bleed cuadrado si es maskable)
    radius = 0 if maskable else int(size * 0.22)
    draw.rounded_rectangle([0, 0, size, size], radius=radius, fill=BG + (255,))

    # Zona segura para maskable: contenido dentro del 80% central
    safe = size if not maskable else int(size * 0.7)
    offset = (size - safe) // 2

    # Letra "D" central
    font_size = int(safe * 0.52)
    font = ImageFont.truetype(FONT_PATH, font_size)
    text = "D"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = offset + (safe - tw) / 2 - bbox[0]
    ty = offset + (safe - th) / 2 - bbox[1] - safe * 0.06
    draw.text((tx, ty), text, font=font, fill=WHITE + (255,))

    # Franja tricolor sutil (alemana) debajo de la letra
    stripe_w = int(safe * 0.5)
    stripe_h = max(4, int(size * 0.035))
    stripe_x = offset + (safe - stripe_w) / 2
    stripe_y = offset + safe * 0.68
    seg_w = stripe_w / 3
    for i, color in enumerate([FLAG_BLACK, FLAG_RED, FLAG_GOLD]):
        x0 = stripe_x + i * seg_w
        draw.rectangle([x0, stripe_y, x0 + seg_w, stripe_y + stripe_h], fill=color + (255,))

    if opaque:
        base = Image.new("RGB", (size, size), BG)
        base.paste(img, (0, 0), img)
        return base
    return img


if __name__ == "__main__":
    out_dir = "/root/german-app/icons"

    draw_icon(192).save(f"{out_dir}/icon-192.png")
    draw_icon(512).save(f"{out_dir}/icon-512.png")
    draw_icon(512, maskable=True).save(f"{out_dir}/icon-512-maskable.png")
    draw_icon(180, opaque=True).save(f"{out_dir}/apple-touch-icon.png")

    print("Íconos generados en", out_dir)
