"""Marketplace banner: pixel-art landscape, chunky title and real in-game butterfly models.

Run after generate.py (it reads the generated textures):
    python3 tools/banner.py
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

import generate as g

W, H = 1920, 1080
PX = 4                      # background pixel size
LW, LH = W // PX, H // PX   # low-res canvas for the landscape
R = random.Random(11)

FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": [".#.", "##.", ".#.", ".#.", ".#.", ".#.", "###"],
    ",": ["..", "..", "..", "..", "..", ".#", "#."],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
    " ": ["..", "..", "..", "..", "..", "..", ".."],
}


def rgb(c):
    return g.rgb(c)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------------------
# Landscape (drawn small, then scaled up so every pixel is a chunky block)
# ---------------------------------------------------------------------------

def landscape():
    img = Image.new("RGB", (LW, LH))
    px = img.load()
    cx, cy = LW / 2, LH * 0.52
    sky_top, sky_mid, glow = rgb("#4FB4F0"), rgb("#9ADCF8"), rgb("#FFF4C0")
    for y in range(LH):
        for x in range(LW):
            t = min(1, y / (LH * 0.62))
            c = lerp(sky_top, sky_mid, t)
            ang = math.atan2(y - cy, x - cx)
            if int((ang + math.pi) / (math.pi / 10)) % 2 == 0:
                c = lerp(c, (255, 255, 255), 0.16)
            d = math.hypot((x - cx) / 1.4, y - cy) / (LH * 0.55)
            c = lerp(glow, c, min(1, d))
            # Quantise into bands for a pixel-art look.
            c = tuple(v // 6 * 6 for v in c)
            px[x, y] = c
    d = ImageDraw.Draw(img)

    # Blocky clouds.
    for x0, y0, w in ((30, 40, 46), (360, 28, 54), (300, 70, 30), (90, 92, 26)):
        for i in range(w // 6):
            h = 6 + (3 if i % 3 == 1 else 0)
            d.rectangle([x0 + i * 6, y0 - h, x0 + i * 6 + 6, y0 + 4], fill=(250, 252, 255))
        d.rectangle([x0 - 4, y0, x0 + w + 4, y0 + 6], fill=(250, 252, 255))
        d.rectangle([x0 - 4, y0 + 6, x0 + w + 4, y0 + 8], fill=(214, 232, 246))

    # Distant hills.
    for layer, (base, col) in enumerate(((176, "#7CC85A"), (196, "#5EAE44"))):
        for x in range(0, LW, 4):
            h = base - int(14 * math.sin(x / (38 + layer * 9) + layer)) - int(6 * math.sin(x / 13))
            d.rectangle([x, h, x + 4, LH], fill=rgb(col))

    def tree(x, ground, s=1.0, dark=False):
        trunk, leaf, leaf_dk = rgb("#6E4A2A"), rgb("#3E9A36" if not dark else "#2E7A2A"), rgb("#2A6A24")
        th = int(18 * s)
        d.rectangle([x - 2, ground - th, x + 2, ground], fill=trunk)
        r = int(14 * s)
        for bx, by, bw, bh in ((-r, -th - r, 2 * r, r), (-r + 4, -th - r - 8, 2 * r - 8, 8), (-r - 4, -th - 6, 2 * r + 8, 10)):
            d.rectangle([x + bx, ground + by, x + bx + bw, ground + by + bh], fill=leaf)
        d.rectangle([x - r - 4, ground - th + 2, x + r + 4, ground - th + 4], fill=leaf_dk)
        for _ in range(int(14 * s)):
            lx, ly = x + R.randint(-r, r), ground - th - R.randint(0, r + 4)
            d.rectangle([lx, ly, lx + 2, ly + 2], fill=lerp(leaf, (255, 255, 255), 0.18))

    for x, gnd, s in ((22, 214, 1.2), (70, 206, 0.9), (420, 210, 1.15), (466, 218, 1.3), (380, 214, 0.8)):
        tree(x, gnd, s)

    # Grass blocks in the foreground, stepped like terrain, with a Minecraft grass-block side.
    grass, grass_lt, grass_dk = rgb("#6CC24A"), rgb("#86D45E"), rgb("#4E9E34")
    dirt, dirt_dk, dirt_lt = rgb("#8A5E3A"), rgb("#6E4A2C"), rgb("#9E7048")
    block = 16
    tops = []
    for i in range(LW // block + 1):
        x = i * block
        top = 222 + (block if i in (3, 4, 5, 24, 25) else 0) - (block if i in (0, 27, 28, 29) else 0)
        tops.append((x, top))
        drip = [R.randint(3, 7) for _ in range(block)]
        for y in range(top, LH, block):
            for bx in range(block):
                for by in range(block):
                    if y + by >= LH or x + bx >= LW:
                        continue
                    n = (bx * 7 + by * 13 + y * 3 + i * 5) % 11
                    if y == top and by < drip[bx]:
                        c = grass_lt if by == 0 else (grass if n > 2 else grass_dk)
                    else:
                        c = dirt if n > 3 else (dirt_dk if n < 2 else dirt_lt)
                    if bx == block - 1 or by == block - 1:
                        c = lerp(c, (0, 0, 0), 0.18)
                    px[x + bx, y + by] = c
    for x, top in tops:
        for _ in range(R.randint(1, 3)):
            fx = x + R.randint(2, 13)
            kind = R.random()
            if kind < 0.35:
                d.rectangle([fx, top - 4, fx, top - 1], fill=rgb("#3E8A2E"))
                d.rectangle([fx - 1, top - 3, fx - 1, top - 2], fill=rgb("#3E8A2E"))
            else:
                col = R.choice([rgb("#E83A3A"), rgb("#F2D84A"), rgb("#F07AC0"), rgb("#7A9AF0"), rgb("#F4F2EA")])
                d.rectangle([fx, top - 6, fx, top - 1], fill=rgb("#3E8A2E"))
                d.rectangle([fx + 1, top - 3, fx + 1, top - 3], fill=rgb("#5AA840"))
                d.rectangle([fx - 1, top - 9, fx + 1, top - 7], fill=col)
                d.point((fx, top - 8), fill=rgb("#F8E070") if col != rgb("#F2D84A") else rgb("#C87A1A"))
    return img.resize((W, H), Image.NEAREST)


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------

def text_mask(text, scale, gap=1):
    cols = sum(len(FONT[ch][0]) + gap for ch in text) - gap
    m = Image.new("L", (cols * scale, 7 * scale), 0)
    d = ImageDraw.Draw(m)
    x = 0
    for ch in text:
        glyph = FONT[ch]
        for gy, row in enumerate(glyph):
            for gx, c in enumerate(row):
                if c == "#":
                    d.rectangle([(x + gx) * scale, gy * scale, (x + gx + 1) * scale - 1, (gy + 1) * scale - 1], fill=255)
        x += len(glyph[0]) + gap
    return m


def grow(mask, r):
    return mask.filter(ImageFilter.MaxFilter(r * 2 + 1))


def chunky_text(text, scale, top, bottom, outline, bevel=True):
    """Letters built from bevelled blocks, with a thick outline and a drop shadow."""
    gap = 1
    cols = sum(len(FONT[ch][0]) + gap for ch in text) - gap
    pad = scale
    w, h = cols * scale + pad * 2, 7 * scale + pad * 2
    mask = Image.new("L", (w, h), 0)
    face = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    md, fd = ImageDraw.Draw(mask), ImageDraw.Draw(face)
    b = max(2, scale // 5)
    x = 0
    for ch in text:
        glyph = FONT[ch]
        for gy, row in enumerate(glyph):
            c = lerp(rgb(top), rgb(bottom), gy / 6)
            for gx, cell in enumerate(row):
                if cell != "#":
                    continue
                x0, y0 = pad + (x + gx) * scale, pad + gy * scale
                x1, y1 = x0 + scale - 1, y0 + scale - 1
                md.rectangle([x0, y0, x1, y1], fill=255)
                fd.rectangle([x0, y0, x1, y1], fill=(*c, 255))
                if bevel:
                    fd.rectangle([x0, y0, x1, y0 + b - 1], fill=(*lerp(c, (255, 255, 255), 0.45), 255))
                    fd.rectangle([x0, y0, x0 + b - 1, y1], fill=(*lerp(c, (255, 255, 255), 0.25), 255))
                    fd.rectangle([x0, y1 - b + 1, x1, y1], fill=(*lerp(c, rgb(outline), 0.35), 255))
                    fd.rectangle([x1 - b + 1, y0 + b, x1, y1], fill=(*lerp(c, rgb(outline), 0.2), 255))
        x += len(glyph[0]) + gap
    edge = grow(mask, max(3, scale // 3))
    out = Image.new("RGBA", (w + scale, h + scale), (0, 0, 0, 0))
    shadow_off = max(4, scale // 2)
    out.paste(Image.new("RGBA", (w, h), (*rgb("#14203A"), 140)), (shadow_off, shadow_off), edge)
    out.paste(Image.new("RGBA", (w, h), (*rgb(outline), 255)), (0, 0), edge)
    out.alpha_composite(face, (0, 0))
    return out


# ---------------------------------------------------------------------------
# Butterflies
# ---------------------------------------------------------------------------

def butterfly(sid, size, yaw, pitch, flap, shiny=False):
    tex = Image.open(os.path.join(g.RP, "textures", "entity", "butterflies",
                                  f"{sid}{'_shiny' if shiny else ''}.png")).convert("RGBA")
    shot = g.render_model(g.BUTTERFLY_GEO, tex, {"wing_left": -flap, "wing_right": flap}, yaw=yaw, pitch=pitch, size=size)
    # A soft dark rim so every butterfly pops off the background.
    a = shot.split()[3].filter(ImageFilter.MaxFilter(5))
    rim = Image.new("RGBA", shot.size, (*rgb("#1A2440"), 0))
    rim.putalpha(a.point(lambda v: 110 if v else 0))
    rim.alpha_composite(shot)
    return rim


def sparkle(img, x, y, s, col=(255, 252, 220)):
    d = ImageDraw.Draw(img)
    d.rectangle([x - s, y - s // 3, x + s, y + s // 3], fill=(*col, 255))
    d.rectangle([x - s // 3, y - s, x + s // 3, y + s], fill=(*col, 255))
    d.rectangle([x - s // 3, y - s // 3, x + s // 3, y + s // 3], fill=(255, 255, 255, 255))


def build():
    img = landscape().convert("RGBA")

    # Title.
    t1 = chunky_text("BUTTERFLIES", 20, "#9AF4FF", "#2A72E0", "#0C1E4A")
    t2 = chunky_text("GALORE", 25, "#FFE88A", "#F0701A", "#481804")
    y1 = 36
    img.alpha_composite(t1, ((W - t1.width) // 2 + 10, y1))
    y2 = y1 + t1.height - 34
    img.alpha_composite(t2, ((W - t2.width) // 2 + 12, y2))
    tag = chunky_text("1,000 BUTTERFLIES!", 7, "#FFFFFF", "#E0F2FF", "#3A0A22", bevel=False)
    tx, ty = (W - tag.width) // 2 + 4, y2 + t2.height - 8
    d = ImageDraw.Draw(img)
    rib, rib_dk = rgb("#E8407A"), rgb("#A8285A")
    for side in (-1, 1):
        ex = tx - 10 if side < 0 else tx + tag.width + 4
        d.polygon([(ex, ty + 6), (ex + side * 64, ty + 6), (ex + side * 40, ty + tag.height // 2),
                   (ex + side * 64, ty + tag.height - 6), (ex, ty + tag.height - 6)], fill=(*rib_dk, 255))
    d.rectangle([tx - 14, ty, tx + tag.width + 8, ty + tag.height - 10], fill=(*rib, 255))
    d.rectangle([tx - 14, ty + tag.height - 18, tx + tag.width + 8, ty + tag.height - 10], fill=(*lerp(rib, rib_dk, 0.6), 255))
    d.rectangle([tx - 14, ty, tx + tag.width + 8, ty + 5], fill=(*lerp(rib, (255, 255, 255), 0.35), 255))
    img.alpha_composite(tag, (tx, ty - 6))

    # A swarm streaming across the meadow, with two big ones up front.
    flock = [
        ("common_rose", 130, 190, 300, 215, 35, 25, False),
        ("soulfire_wisp", 120, 1740, 330, 160, 35, 30, False),
        ("red_lacewing", 110, 300, 520, 225, 30, 20, False),
        ("malachite", 150, 520, 640, 220, 35, 30, False),
        ("peacock", 170, 760, 690, 205, 40, 30, False),
        ("cherry_blossom", 150, 1010, 640, 165, 35, 25, False),
        ("zebra_longwing", 140, 1220, 640, 150, 40, 20, False),
        ("emerald_swallowtail", 170, 640, 880, 230, 45, 15, False),
        ("sunset_morpho", 150, 1110, 860, 175, 35, 30, False),
        ("glasswing", 120, 1560, 300, 170, 30, 25, False),
        ("ulysses", 130, 1660, 560, 150, 40, 25, False),
    ]
    for sid, size, x, y, yaw, pitch, flap, shiny in flock:
        img.alpha_composite(butterfly(sid, size, yaw, pitch, flap, shiny), (x - size // 2, y - size // 2))

    shiny = butterfly("monarch", 230, 195, 40, 30, True)
    img.alpha_composite(shiny, (880 - 115, 860 - 115))
    for dx, dy, s in ((-110, -70, 10), (115, -50, 8), (95, 75, 7), (-90, 70, 6)):
        sparkle(img, 880 + dx, 860 + dy, s)

    left = butterfly("blue_morpho", 600, 215, 34, 28)
    img.alpha_composite(left, (-110, 520))
    right = butterfly("monarch", 660, 160, 36, 32)
    img.alpha_composite(right, (1330, 470))
    for x, y, s in ((1840, 470, 12), (1290, 520, 8), (260, 700, 9), (120, 1000, 7), (1630, 1010, 9), (450, 470, 6),
                    (1460, 420, 7), (980, 560, 6)):
        sparkle(img, x, y, s)

    out = img.convert("RGB")
    os.makedirs(g.DOCS, exist_ok=True)
    out.save(os.path.join(g.DOCS, "marketplace_banner.png"))
    out.resize((800, 450), Image.LANCZOS).save(os.path.join(g.DOCS, "marketplace_banner_800x450.png"))


if __name__ == "__main__":
    build()
