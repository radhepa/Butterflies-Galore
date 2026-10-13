#!/usr/bin/env python3
"""Builds the Butterflies Galore behavior pack, resource pack and .mcaddon.

Every texture, model, mob, spawn rule, handbook entry and language string is
generated from the species table below, so adding or tweaking a species is a
one-line change followed by:

    python3 tools/generate.py
"""
import colorsys
import json
import math
import os
import random
import re
import shutil
import uuid
import zipfile
from collections import deque

from PIL import Image, ImageDraw

import species_more

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "ButterfliesGalore_BP")
RP = os.path.join(ROOT, "ButterfliesGalore_RP")
DIST = os.path.join(ROOT, "dist")
DOCS = os.path.join(ROOT, "docs")
NS = "butterflies"
VERSION = [1, 1, 0]
MIN_ENGINE = [1, 21, 90]
UUID_NS = uuid.UUID("6f1d2c4e-8a8b-4f0e-9a51-0b7e0c1d2a33")


def uid(name):
    return str(uuid.uuid5(UUID_NS, name))


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def rgb(c):
    if isinstance(c, tuple):
        return c[:3]
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, f):
    return tuple(max(0, min(255, round(v * f))) for v in rgb(c))


def hexc(c):
    return "#%02X%02X%02X" % c


def vivid(c, sat_f=1.2, val_f=1.04):
    h, s, v = colorsys.rgb_to_hsv(*(x / 255 for x in c))
    if s > 0.15:
        s = min(1.0, s * sat_f)
    v = min(1.0, v * val_f)
    return tuple(round(x * 255) for x in colorsys.hsv_to_rgb(h, s, v))


def lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def sat(c):
    return colorsys.rgb_to_hsv(*(x / 255 for x in c[:3]))[1]


# ---------------------------------------------------------------------------
# Wing painter
# ---------------------------------------------------------------------------
# A wing is painted on a 16 x 22 grid. u runs from the body (0) to the wing tip
# (15); v runs from the leading edge (0) to the rear (21). Wing outlines are
# polygons, so the forewing and hindwing are separate shapes.
#
# Species patterns are written in a compact 10 x 14 "design space" and scaled
# onto the grid by T() / R(), which keeps the species table short and readable.

WW, WH = 16, 22


def T(p):
    return (p[0] * 1.5 + 0.4, p[1] * 1.5 + 0.8)


def R(r):
    return r * 1.5


ROUND_FORE = [(0, 2), (4, 1), (9, 1.5), (12.5, 3.5), (13.5, 6.5), (12, 9.5), (8, 11), (0, 10.5)]
POLYS = {
    "classic": ([(0, 1.5), (4, 0.8), (9, 1), (13, 2), (14.6, 3.5), (14, 6), (12, 9), (9, 11), (0, 10.5)],
                [(0, 9), (6, 9.5), (10, 10.5), (12, 13), (11.5, 16), (9.5, 18.5), (6.5, 20), (3, 20), (1, 18)]),
    "pointed": ([(0, 1.5), (5, 0.8), (10, 1.2), (14.6, 2.5), (14, 5), (11.5, 8), (8, 10), (0, 10)],
                [(0, 9), (7, 9.5), (10.5, 11), (11.5, 14), (10.5, 17), (8, 19), (4.5, 19.8), (1.5, 18.5)]),
    "rounded": (ROUND_FORE,
                [(0, 9.5), (7, 10), (11, 11.5), (12.5, 14.5), (11.5, 17.5), (8.5, 19.5), (4, 19.8), (1, 18)]),
    "swallowtail": ([(0, 1.5), (5, 0.8), (10, 1.2), (14.6, 2.5), (14, 5.5), (11, 9), (7, 10.5), (0, 10)],
                    [(0, 9), (7, 9.5), (10, 11), (10.5, 14), (9, 16.5), (7.9, 17), (7.7, 21.5), (6.3, 21.5),
                     (6.1, 17.5), (4, 18.5), (1.5, 17.5)]),
    "kite": ([(0, 1.5), (5, 0.8), (10, 1.2), (14.6, 2.5), (14, 5.5), (11, 9), (7, 10.5), (0, 10)],
             [(0, 9), (6.5, 9.5), (9, 11), (9, 14), (7.4, 16), (6.7, 21.5), (5.5, 21.5), (5.3, 16.5), (3, 17.5),
              (1, 16)]),
    "longwing": ([(0, 1.5), (6, 0.8), (11, 1), (14.6, 2.2), (14, 4.5), (11, 7), (6, 9), (0, 9.5)],
                 [(0, 8.5), (6, 9), (9.5, 10.5), (10, 13), (8, 15.5), (4.5, 16.5), (1.5, 15.5)]),
    "leaf": ([(0, 1.5), (6, 0.6), (11, 0.8), (14.9, 0.3), (13.6, 3), (13.6, 6), (12, 10), (0, 10.5)],
             [(0, 9.5), (8, 10), (11.5, 12), (11, 16), (8, 19), (4.8, 21.6), (3.6, 21.6), (1, 18)]),
    "scalloped": ([(0, 1.5), (5, 0.8), (10, 1.2), (14.5, 2.5), (13, 4.5), (14.2, 6), (12, 8), (12.6, 9.5),
                   (9, 11), (0, 10.5)],
                  [(0, 9), (7, 9.5), (11, 10.5), (12.6, 12.5), (11.5, 14), (12.2, 15.5), (10.5, 17), (10.2, 18.5),
                   (7.5, 19.5), (6.6, 21), (5, 19.6), (3, 20.6), (1, 18)]),
    "skipper": ([(0, 2), (4, 1.2), (8.5, 1.5), (12.5, 3), (13.2, 5.5), (11, 8.5), (6, 10), (0, 10)],
                [(0, 9), (6, 9.5), (9.5, 11), (10, 14), (8.5, 16.5), (5, 17.5), (1.5, 16.5)]),
    "birdwing": ([(0, 1.2), (6, 0.5), (11.5, 0.8), (14.9, 2), (14.7, 5), (13, 8.5), (9, 11), (0, 10.5)],
                 [(0, 9), (7, 9.5), (11, 11), (12.5, 14), (11.5, 17.5), (8.5, 20), (4.5, 20.6), (1.5, 19)]),
    "hairstreak": (ROUND_FORE,
                   [(0, 9.5), (7, 10), (11, 11.5), (12.5, 14.5), (11.5, 17), (9.2, 18.5), (8.9, 21.6),
                    (7.9, 21.6), (7.7, 19), (4, 19.8), (1, 18)]),
}
TAILED = {"swallowtail", "kite", "hairstreak", "leaf"}

VEIN_BASE = (0.0, 5.0)
VEIN_TIPS = [(9, 1), (9, 3), (8, 5), (5, 6), (7, 8), (7, 10), (5, 12), (2, 12)]


def inside(poly, x, y):
    hit = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0 if l2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / l2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def design(p):
    """Grid pixel -> nearest design-space cell (for lattice patterns)."""
    return round((p[0] - 0.4) / 1.5), round((p[1] - 0.8) / 1.5)


class Wing:
    def __init__(self, shape):
        fore_poly, hind_poly = POLYS[shape]
        self.fore, self.hind = set(), set()
        for u in range(WW - 1):
            for v in range(WH):
                if inside(fore_poly, u + 0.5, v + 0.5):
                    self.fore.add((u, v))
                elif inside(hind_poly, u + 0.5, v + 0.5):
                    self.hind.add((u, v))
        self.mask = self.fore | self.hind
        self.tail = {p for p in self.hind if shape in TAILED and p[1] >= 17 and p[0] >= 5}
        # Distance (in pixels) from the outer margin. The body side is not a margin.
        self.dist = {}
        q = deque()
        for u in range(0, WW + 1):
            for v in range(-1, WH + 1):
                if (u, v) not in self.mask:
                    q.append(((u, v), -1))
        seen = set(p for p, _ in q)
        while q:
            (u, v), d = q.popleft()
            for n in ((u + 1, v), (u - 1, v), (u, v + 1), (u, v - 1)):
                if n in self.mask and n not in seen:
                    seen.add(n)
                    self.dist[n] = d + 1
                    q.append((n, d + 1))
        for p in self.mask:
            self.dist.setdefault(p, 0)
        self.px = {p: (0, 0, 0, 0) for p in self.mask}
        self.rowmax = {}
        for u, v in self.mask:
            self.rowmax[v] = max(self.rowmax.get(v, 0), u)
        self.apex = max((p for p in self.fore if p[1] <= 9), key=lambda p: p[0] - 0.3 * p[1])

    def region(self, name):
        if name == "inner":
            return {p for p in self.mask if self.dist[p] >= 1}
        return {"all": self.mask, "fore": self.fore, "hind": self.hind, "tail": self.tail}[name]

    def put(self, p, c, t=1.0):
        if p not in self.mask:
            return
        c = rgb(c)
        old = self.px[p]
        if old[3] == 0 or t >= 1:
            self.px[p] = (*c, 255)
        else:
            self.px[p] = (*mix(old[:3], c, t), 255)


# Feature builders. Each returns a function that paints onto a Wing.

def fill(c, region="all"):
    return lambda w: [w.put(p, c) for p in w.region(region)]


def grad(c, s=0.6, region="all"):
    return lambda w: [w.put(p, c, s * p[0] / max(1, w.rowmax[p[1]])) for p in w.region(region)]


def basal(c, n=2, region="all"):
    edge = n * 1.5

    def f(w):
        for p in w.region(region):
            if p[0] < edge - 1:
                w.put(p, c)
            elif p[0] < edge:
                w.put(p, c, 0.55)
    return f


def border(c, width=1, region="all"):
    wpx = max(1, int(width * 1.2 + 0.5))
    return lambda w: [w.put(p, c) for p in w.region(region) if w.dist[p] < wpx]


def ring(c, k=1, region="all", spaced=True):
    kpx = k * 3 // 2
    period = 2 if kpx == 0 else 3
    return lambda w: [w.put(p, c) for p in w.region(region)
                      if w.dist[p] == kpx and (not spaced or (p[0] + p[1]) % period == 0)]


def veins(c, width=0.9, region="all"):
    base = T(VEIN_BASE)
    tips = [T(t) for t in VEIN_TIPS]

    def f(w):
        for p in w.region(region):
            if any(seg_dist(p, base, tip) <= width * 0.6 for tip in tips):
                w.put(p, c)
    return f


def apex(c, r=2.0):
    def f(w):
        ax, ay = w.apex
        for p in w.fore:
            if math.hypot(p[0] - ax, p[1] - ay) <= R(r):
                w.put(p, c)
    return f


def line(c, a, b, width=1.0, region="all"):
    a, b = T(a), T(b)
    return lambda w: [w.put(p, c) for p in w.region(region) if seg_dist(p, a, b) <= width * 0.9]


def circle(c, pos, r=1.0, region="all"):
    pos = T(pos)
    return lambda w: [w.put(p, c) for p in w.region(region) if math.hypot(p[0] - pos[0], p[1] - pos[1]) <= R(r)]


def eye(pos, layers):
    """layers: [(radius, colour), ...] from the outside in."""
    return lambda w: [circle(col, pos, r)(w) for r, col in layers]


def spots(c, pts):
    pts = [T(p) for p in pts]
    return lambda w: [w.put(p, c) for p in w.mask for q in pts if math.hypot(p[0] - q[0], p[1] - q[1]) <= 0.85]


def checker(c, region="all"):
    def f(w):
        for p in w.region(region):
            du, dv = design(p)
            if w.dist[p] >= 1 and (du + 2 * dv) % 4 == 0:
                w.put(p, c)
    return f


def stripes(c, period=3, phase=0, region="all", slope=1):
    def f(w):
        for p in w.region(region):
            du, dv = design(p)
            if (du + slope * dv) % period == phase:
                w.put(p, c)
    return f


def clear(region="all"):
    def f(w):
        for p in w.region(region):
            if w.dist[p] >= 1:
                w.px[p] = (0, 0, 0, 0)
    return f


def sheen(c, s=0.6, region="all"):
    return lambda w: [w.put(p, c, s) for p in w.region(region)
                      if w.dist[p] >= 1 and p[0] >= 3 and (p[0] * 3 + p[1] * 5) % 7 in (0, 3)]


def speckle(c, density=0.2, region="all", seed=7):
    def f(w):
        r = random.Random(seed)
        for p in sorted(w.region(region)):
            if r.random() < density:
                w.put(p, c)
    return f


# ---------------------------------------------------------------------------
# Species table
# ---------------------------------------------------------------------------
_section = ["Meadows & Fields"]


def SECTION(name):
    _section[0] = name


K = "#1A1612"   # soot black
W = "#F4F2EA"   # wing white
RARITY = {"common": 10, "uncommon": 6, "rare": 3, "legendary": 1}


class Species:
    def __init__(self, id, name, shape, habitat, scale, flap, rarity, feats,
                 body="#1E1A16", accent=None, category=None):
        self.id, self.name, self.shape = id, name, shape
        # Scales were tuned for the original 22-pixel wingspan; the model is now 35 pixels wide.
        self.habitat, self.scale, self.flap = habitat, round(scale * 0.75, 3), flap
        self.rarity, self.feats = rarity, feats
        self.body, self.accent = body, accent
        self.category = category or _section[0]


S = Species
SPECIES = [
    SECTION("Meadows & Fields"),
    S("monarch", "Monarch", "pointed", ["plains", "meadow", "flower_forest", "savanna"], 0.5, 0.9, "common",
      [fill("#E8761C"), grad("#F4A23C", 0.45), basal("#B4500F", 1), veins(K), border(K, 2), ring(W, 1),
       spots(W, [(7, 1), (8, 2), (6, 1), (5, 0)])], accent=W),
    S("viceroy", "Viceroy", "classic", ["swamp", "plains", "river"], 0.45, 1.1, "common",
      [fill("#E2701E"), grad("#F09A3A", 0.4), veins(K), line(K, (1, 9), (7, 9), 0.9), border(K, 2), ring(W, 1),
       spots(W, [(7, 1), (8, 2)])]),
    S("painted_lady", "Painted Lady", "classic", ["plains", "desert", "savanna", "meadow"], 0.42, 1.2, "common",
      [fill("#E88A3A"), grad("#F2B068", 0.35), basal("#7A5236", 2), apex(K, 3.2), spots(W, [(7, 1), (8, 3), (6, 2), (9, 2)]),
       spots(K, [(4, 4), (3, 3), (5, 9), (3, 10), (6, 10)]), border("#3A2A1E", 1), ring(W, 0, "hind")]),
    S("red_admiral", "Red Admiral", "classic", ["forest", "plains", "birch"], 0.45, 1.1, "common",
      [fill("#1E1A1A"), line("#D8402A", (3, 0), (7, 6), 1.3), ring("#D8402A", 1, "hind", False),
       spots(W, [(7, 1), (8, 2), (6, 0), (9, 3)]), border("#141010", 1), ring(W, 0, "all")]),
    S("peacock", "Peacock", "classic", ["forest", "flower_forest", "meadow"], 0.48, 1.0, "common",
      [fill("#A8231F"), grad("#C4442E", 0.3), basal("#5A1A14", 2),
       eye((7, 2), [(2.0, "#E8C84A"), (1.4, "#3D5BA8"), (0.6, "#1A1A1A")]),
       eye((5, 10), [(1.8, "#2A2A3A"), (1.2, "#4A6AC0"), (0.5, "#101018")]), border("#4A2A20", 1)]),
    S("common_buckeye", "Common Buckeye", "classic", ["plains", "savanna", "desert"], 0.42, 1.2, "common",
      [fill("#7A5636"), line("#EFE6D2", (5, 1), (8, 4), 1.0), eye((6, 4), [(1.4, "#E8A53A"), (0.6, "#1C1C2E")]),
       eye((5, 9), [(1.6, "#D96C2C"), (1.0, "#3B4FA0"), (0.4, "#101010")]),
       eye((3, 11), [(1.2, "#D96C2C"), (0.5, "#5A2A6A")]), spots("#E07A2A", [(1, 1), (2, 2)]), border("#4A3420", 1)]),
    S("cabbage_white", "Cabbage White", "classic", ["plains", "meadow", "birch"], 0.4, 1.3, "common",
      [fill("#F2F0E6"), basal("#8A8A80", 1), apex("#3A3A3A", 1.6), spots("#2A2A2A", [(5, 3), (4, 1)]),
       spots("#CFCFC4", [(6, 8), (2, 8)])], accent="#D8D8D0"),
    S("orange_tip", "Orange Tip", "classic", ["flower_forest", "meadow", "plains"], 0.38, 1.3, "common",
      [fill("#F7F5EE"), apex("#F08A1E", 2.8), apex("#2A2A2A", 0.9), spots(K, [(4, 3)]),
       speckle("#9BAE6E", 0.35, "hind", 3), basal("#7A7A70", 1)]),
    S("brimstone", "Brimstone", "leaf", ["forest", "birch", "flower_forest"], 0.45, 1.0, "common",
      [fill("#F2E64A"), grad("#F8F098", 0.3), basal("#C8B83A", 1), spots("#E59630", [(4, 3), (4, 9)]),
       border("#D8C838", 1)]),
    S("clouded_yellow", "Clouded Yellow", "classic", ["plains", "meadow", "savanna"], 0.4, 1.3, "common",
      [fill("#F4B832"), grad("#F8D060", 0.3), border("#3A2A1A", 2, "fore"), border("#3A2A1A", 1, "hind"),
       ring("#F4D060", 1, "fore"), spots(K, [(4, 3)]), spots("#F07A1E", [(4, 9)])]),
    SECTION("Swallowtails"),
    S("tiger_swallowtail", "Eastern Tiger Swallowtail", "swallowtail", ["forest", "flower_forest", "birch"], 0.6, 0.8, "common",
      [fill("#F5D33A"), grad("#F8E27A", 0.3), line(K, (2, 0), (1, 6), 0.9), line(K, (4, 0), (3, 4), 0.9),
       line(K, (6, 0), (5, 3), 0.9), line(K, (0, 7), (3, 10), 0.9), border(K, 2), ring("#F5D33A", 1, "fore"),
       ring("#3E6FB8", 1, "hind"), spots("#E8702A", [(2, 11)]), fill(K, "tail")]),
    S("black_swallowtail", "Black Swallowtail", "swallowtail", ["plains", "meadow"], 0.58, 0.8, "uncommon",
      [fill("#141414"), ring("#F2D04A", 1, "all"), line("#3E62B0", (2, 10), (6, 9), 0.9),
       spots("#E8702A", [(1, 11)]), spots(K, [(1, 12)]), ring("#F2D04A", 3, "fore")]),
    S("zebra_swallowtail", "Zebra Swallowtail", "kite", ["forest", "swamp"], 0.55, 0.8, "uncommon",
      [fill("#F2F2EA"), stripes(K, 3, 0, "all", -1), border(K, 1), spots("#D8302A", [(2, 11), (3, 10)]),
       spots("#3E62B0", [(3, 12)]), fill(K, "tail")]),
    S("pipevine_swallowtail", "Pipevine Swallowtail", "swallowtail", ["forest", "roofed"], 0.55, 0.8, "uncommon",
      [fill("#12161E"), grad("#2C5FA8", 0.75, "hind"), sheen("#4A8AD8", 0.5, "hind"), ring("#F2A23A", 1, "hind"),
       ring("#E8E8E0", 0, "fore")]),
    S("giant_swallowtail", "Giant Swallowtail", "swallowtail", ["savanna", "jungle"], 0.7, 0.6, "uncommon",
      [fill("#1E1A12"), line("#F0CE3E", (8, 1), (1, 6), 1.2), line("#F0CE3E", (1, 7), (6, 9), 1.1),
       ring("#F0CE3E", 1, "fore"), spots("#F0CE3E", [(4, 12), (5, 13)]), spots("#E8702A", [(2, 11)])]),
    S("old_world_swallowtail", "Old World Swallowtail", "swallowtail", ["mountains", "meadow"], 0.58, 0.8, "uncommon",
      [fill("#F0D84A"), basal(K, 2), veins(K), border(K, 2), ring("#F0D84A", 1, "fore"), ring("#3E6FB8", 1, "hind", False),
       spots("#D8302A", [(1, 11)]), fill(K, "tail")]),
    S("scarce_swallowtail", "Scarce Swallowtail", "kite", ["mountains", "savanna"], 0.55, 0.8, "uncommon",
      [fill("#F4EEC4"), stripes(K, 3, 1, "fore", -1), line(K, (0, 8), (4, 12), 0.9), border(K, 1),
       ring("#5A7AD0", 1, "hind"), spots("#E8902A", [(2, 11)]), fill(K, "tail")]),
    S("spicebush_swallowtail", "Spicebush Swallowtail", "swallowtail", ["forest", "roofed"], 0.55, 0.8, "uncommon",
      [fill("#161616"), ring("#C8E0B8", 1, "fore"), grad("#4E8E9A", 0.7, "hind"), ring("#B8D8E8", 1, "hind"),
       spots("#E8902A", [(1, 11), (6, 9)])]),
    SECTION("Woodland"),
    S("mourning_cloak", "Mourning Cloak", "scalloped", ["taiga", "forest", "birch"], 0.55, 0.9, "uncommon",
      [fill("#4A2219"), grad("#6A3424", 0.3), border("#E8D9A0", 1), ring("#3C6CC0", 1, "all", True)]),
    S("question_mark", "Question Mark", "scalloped", ["forest", "roofed"], 0.48, 1.0, "common",
      [fill("#D8752A"), grad("#E89A4A", 0.3), spots(K, [(3, 2), (4, 4), (2, 4), (5, 2), (6, 3)]),
       fill("#7A3E28", "hind"), border("#5A3A22", 1), ring("#B48AD0", 0, "hind")]),
    S("comma", "Comma", "scalloped", ["forest", "birch", "flower_forest"], 0.45, 1.0, "common",
      [fill("#D0792C"), spots(K, [(2, 2), (4, 3), (3, 5), (6, 2), (5, 5)]), fill("#A85A24", "hind"),
       spots(K, [(2, 9), (4, 8)]), border("#4A2A18", 1), spots(W, [(3, 10)])]),
    S("small_tortoiseshell", "Small Tortoiseshell", "classic", ["meadow", "mountains", "plains"], 0.42, 1.2, "common",
      [fill("#E5602A"), spots(K, [(2, 0), (4, 0), (6, 1), (3, 3), (5, 4)]), spots("#F2D04A", [(3, 0), (5, 0), (7, 1)]),
       basal("#3A2A20", 3, "hind"), border(K, 1), ring("#3E78C8", 1, "all")]),
    S("red_spotted_purple", "Red-spotted Purple", "classic", ["forest", "birch"], 0.5, 0.9, "uncommon",
      [fill("#1B2140"), grad("#3A62B8", 0.7, "hind"), sheen("#5A8AE0", 0.5), ring("#E07A2E", 1, "hind"),
       ring("#7AA0E0", 0, "all")]),
    S("white_admiral", "White Admiral", "classic", ["forest", "birch", "taiga"], 0.48, 0.9, "uncommon",
      [fill("#1A1A1A"), line(W, (5, 0), (4, 6), 1.1), line(W, (4, 7), (3, 12), 1.1), spots(W, [(7, 1)]),
       ring("#C84A2A", 1, "hind"), border("#0E0E0E", 1)]),
    S("great_spangled_fritillary", "Great Spangled Fritillary", "classic", ["meadow", "plains", "flower_forest"], 0.5, 1.0, "common",
      [fill("#D5822F"), grad("#E8A050", 0.3), basal("#6A3A1A", 2), checker("#2A1810"), border("#2A1810", 1),
       ring("#2A1810", 1, "all")]),
    S("pearl_bordered_fritillary", "Pearl-bordered Fritillary", "rounded", ["birch", "forest"], 0.36, 1.3, "uncommon",
      [fill("#E09038"), checker("#3A2010"), basal("#5A3418", 1), border("#3A2010", 1), ring(W, 0, "hind")]),
    S("gulf_fritillary", "Gulf Fritillary", "longwing", ["savanna", "jungle", "plains"], 0.45, 1.0, "common",
      [fill("#F06A1A"), grad("#F8902A", 0.3), spots(K, [(3, 2), (5, 2), (4, 4)]), spots(W, [(4, 2)]),
       veins("#B84A10"), border("#3A1A0A", 1, "fore")]),
    S("baltimore_checkerspot", "Baltimore Checkerspot", "classic", ["swamp"], 0.42, 1.1, "uncommon",
      [fill("#1A1A1A"), border("#E86A1E", 1), ring(W, 1, "all", False), ring(W, 3, "all", True),
       spots("#E86A1E", [(1, 1), (2, 2)])]),
    S("marsh_fritillary", "Marsh Fritillary", "rounded", ["swamp", "meadow"], 0.38, 1.2, "uncommon",
      [fill("#C76A2A"), checker("#F0CE6E"), veins("#4A2410"), border("#3A1A0A", 1), ring("#F0CE6E", 1, "hind")]),
    SECTION("Blues & Coppers"),
    S("common_blue", "Common Blue", "rounded", ["plains", "meadow"], 0.3, 1.5, "common",
      [fill("#7EA6F2"), grad("#A8C4F8", 0.3), basal("#5A80D8", 2), border("#2A2A3A", 1), ring(W, 0)], body="#3A3A4A"),
    S("adonis_blue", "Adonis Blue", "rounded", ["meadow", "mountains"], 0.3, 1.5, "uncommon",
      [fill("#3FA8F0"), sheen("#8AD4FF", 0.5), border(K, 1), ring(W, 0), veins("#2A78C8")], body="#2A2A3A"),
    S("holly_blue", "Holly Blue", "rounded", ["forest", "birch"], 0.3, 1.5, "common",
      [fill("#A7C2F2"), basal("#7A9AE0", 1), apex("#2A2A3A", 1.6), border("#5A6A8A", 1, "fore")], body="#3A3A4A"),
    S("karner_blue", "Karner Blue", "rounded", ["savanna", "plains"], 0.28, 1.5, "rare",
      [fill("#5A78D0"), border("#1A1A2A", 1), ring("#E8892C", 1, "hind", False), ring(K, 2, "hind", True), ring(W, 0)]),
    S("small_copper", "Small Copper", "rounded", ["plains", "meadow"], 0.3, 1.5, "common",
      [fill("#F06A1E"), spots(K, [(3, 2), (5, 3), (4, 5), (2, 4), (6, 1)]), border("#3A2014", 1, "fore"),
       fill("#5A3420", "hind"), ring("#F06A1E", 1, "hind", False), border("#3A2014", 1, "hind")]),
    S("large_copper", "Large Copper", "rounded", ["swamp", "river"], 0.34, 1.4, "rare",
      [fill("#F27A1A"), sheen("#FFB050", 0.4), border(K, 1), spots(K, [(4, 3), (3, 9)])]),
    S("purple_hairstreak", "Purple Hairstreak", "hairstreak", ["forest", "roofed"], 0.3, 1.5, "uncommon",
      [fill("#2A2A40"), sheen("#7E5CC8", 0.7, "fore"), basal("#6A4AB8", 2, "fore"), border("#141420", 1),
       spots("#E8902A", [(3, 11)]), fill(K, "tail")]),
    S("green_hairstreak", "Green Hairstreak", "hairstreak", ["meadow", "mountains"], 0.28, 1.5, "uncommon",
      [fill("#6FB04A"), grad("#9AD06A", 0.35), border("#3A6A2A", 1), ring(W, 1, "hind", True)]),
    S("apollo", "Apollo", "classic", ["mountains", "meadow"], 0.52, 0.8, "rare",
      [fill("#F0EEE6"), grad("#D8D8D0", 0.4, "fore"), spots(K, [(4, 2), (6, 3), (3, 4)]),
       eye((3, 9), [(1.5, K), (1.0, "#D8302A"), (0.3, W)]), eye((5, 10), [(1.3, K), (0.8, "#D8302A")]),
       border("#9A9A94", 1, "fore"), basal("#4A4A44", 1)]),
    SECTION("Skippers"),
    S("silver_spotted_skipper", "Silver-spotted Skipper", "skipper", ["plains", "forest"], 0.3, 1.8, "common",
      [fill("#5A4228"), spots("#E8B84A", [(5, 1), (4, 3), (6, 2), (3, 3)]), circle(W, (3, 9), 1.2),
       border("#3A2A18", 1)], body="#4A3820"),
    S("large_skipper", "Large Skipper", "skipper", ["meadow", "plains"], 0.28, 1.8, "common",
      [fill("#D58A2A"), border("#5A3A18", 2), spots("#F2C060", [(4, 2), (3, 8), (4, 9)]), line("#3A2410", (2, 2), (4, 4), 0.8)],
      body="#6A4A20"),
    S("fiery_skipper", "Fiery Skipper", "skipper", ["desert", "savanna", "mesa"], 0.27, 1.8, "common",
      [fill("#F09A2A"), border("#4A2A10", 1), ring("#4A2A10", 1, "all", True), spots("#4A2A10", [(3, 3)])],
      body="#8A5A20"),
    S("long_tailed_skipper", "Long-tailed Skipper", "kite", ["jungle", "savanna"], 0.35, 1.6, "uncommon",
      [fill("#4A3A2A"), basal("#3AA8A8", 4), spots(W, [(5, 2), (6, 3), (4, 3), (7, 1)]), border("#2A2018", 1),
       fill("#2A2018", "tail")], body="#3A8A8A"),
    S("checkered_skipper", "Checkered Skipper", "skipper", ["plains", "savanna"], 0.26, 1.8, "common",
      [fill("#2A2A2A"), checker("#F0F0F0"), stripes("#F0F0F0", 4, 1, "all", 2), ring(W, 0)], body="#4A4A54"),
    SECTION("Rainforest"),
    S("blue_morpho", "Blue Morpho", "birdwing", ["jungle"], 0.68, 0.55, "rare",
      [fill("#2E8CF0"), sheen("#8FD4FF", 0.7), basal("#1E5AC0", 1), border(K, 2), ring(W, 1, "fore", True)]),
    S("sunset_morpho", "Sunset Morpho", "birdwing", ["jungle"], 0.7, 0.55, "rare",
      [fill("#D27A30"), grad("#F2B060", 0.4), basal("#6A3418", 2), border("#2A1A10", 2), ring("#F4E2B0", 1, "all", True)]),
    S("white_morpho", "White Morpho", "birdwing", ["jungle", "bamboo"], 0.62, 0.6, "rare",
      [fill("#F4F4F0"), sheen("#D2E2F4", 0.7), border("#B8C0C8", 1), ring("#9AA4B0", 1, "fore", True)]),
    S("owl_butterfly", "Owl Butterfly", "classic", ["jungle", "roofed"], 0.62, 0.7, "uncommon",
      [fill("#6A5A48"), grad("#8A7A62", 0.3), line("#D8C8A0", (2, 2), (7, 5), 1.0), basal("#3A4A7A", 2),
       eye((4, 10), [(2.3, "#E8D07A"), (1.6, "#1A1A1A"), (0.6, "#E8E0C8")]), border("#3A3024", 1)]),
    S("glasswing", "Glasswing", "longwing", ["jungle", "flower_forest"], 0.42, 1.0, "uncommon",
      [fill("#3A2A20"), clear("all"), veins("#5A3A28", 0.8), border("#3A2A20", 1), spots("#E8702A", [(6, 0), (7, 1)]),
       spots(W, [(8, 2), (7, 3)])]),
    S("postman", "Postman", "longwing", ["jungle"], 0.45, 0.8, "common",
      [fill("#141414"), line("#D82A2A", (3, 2), (7, 4), 1.6), line("#F2E04A", (1, 8), (5, 9), 0.8), border("#0A0A0A", 1)]),
    S("zebra_longwing", "Zebra Longwing", "longwing", ["jungle", "swamp"], 0.45, 0.8, "common",
      [fill("#141414"), line("#F5E36A", (1, 1), (5, 1), 0.9), line("#F5E36A", (3, 3), (8, 2), 0.9),
       line("#F5E36A", (2, 5), (6, 4), 0.8), line("#F5E36A", (0, 8), (5, 10), 0.9), ring("#F5E36A", 1, "hind")]),
    S("julia", "Julia Heliconian", "longwing", ["savanna", "jungle"], 0.42, 1.0, "common",
      [fill("#F27B1A"), grad("#F8A040", 0.35), line("#3A1A0A", (6, 0), (6, 3), 0.8), border("#3A1A0A", 1, "fore")]),
    S("tiger_longwing", "Tiger Longwing", "longwing", ["jungle"], 0.45, 0.8, "uncommon",
      [fill("#E8822A"), circle(K, (4, 3), 1.2), apex(K, 2.5), spots("#F5E36A", [(7, 1), (8, 2), (6, 2)]),
       line(K, (1, 9), (5, 10), 0.9), border(K, 1, "hind")]),
    S("doris_longwing", "Doris Longwing", "longwing", ["jungle"], 0.44, 0.8, "uncommon",
      [fill("#1A1A1A"), circle("#F5E36A", (5, 3), 1.2), line("#4A8AE0", (1, 8), (5, 11), 0.9),
       line("#4A8AE0", (2, 8), (6, 9), 0.9), line("#4A8AE0", (0, 9), (3, 12), 0.8)]),
    S("sara_longwing", "Sara Longwing", "longwing", ["jungle", "mangrove_swamp"], 0.4, 0.9, "uncommon",
      [fill("#121A2A"), sheen("#3A7AE0", 0.6), line("#F2EAA0", (4, 1), (7, 4), 0.9), ring("#F2EAA0", 0, "hind")]),
    S("malachite", "Malachite", "classic", ["jungle", "mangrove_swamp"], 0.5, 0.9, "uncommon",
      [fill("#1E1E14"), circle("#7ED67A", (3, 3), 1.6), circle("#7ED67A", (6, 2), 0.9), circle("#7ED67A", (3, 9), 1.7),
       circle("#7ED67A", (6, 10), 1.0), spots("#B8F0A8", [(7, 1), (8, 3)]), border("#2A2A18", 1)]),
    S("rajah_brooke_birdwing", "Rajah Brooke's Birdwing", "birdwing", ["jungle", "bamboo"], 0.7, 0.5, "rare",
      [fill("#0E0E0E"), line("#4AE07A", (2, 1), (7, 2), 0.9), line("#4AE07A", (2, 4), (6, 5), 0.9),
       line("#4AE07A", (3, 3), (8, 3), 0.7), ring("#2A8A4A", 1, "hind", True)], body="#101010", accent="#D8302A"),
    S("queen_alexandra_birdwing", "Queen Alexandra's Birdwing", "birdwing", ["jungle"], 0.78, 0.45, "legendary",
      [fill("#1A1E2A"), line("#4AB6C8", (1, 1), (8, 1), 0.8), line("#4AB6C8", (1, 3), (8, 3), 0.8),
       line("#4AB6C8", (1, 5), (6, 5), 0.8), fill("#E0C83A", "hind"), grad("#4AB6C8", 0.4, "hind"),
       ring(K, 1, "hind", True), border(K, 1, "hind")], accent="#E0C83A"),
    S("golden_birdwing", "Golden Birdwing", "birdwing", ["jungle"], 0.72, 0.5, "rare",
      [fill("#121212"), veins(W, 0.7, "fore"), fill("#F2C62A", "hind"), grad("#F8E07A", 0.3, "hind"),
       veins(K, 0.8, "hind"), border(K, 1, "hind")], accent="#F2C62A"),
    S("great_mormon", "Great Mormon", "swallowtail", ["jungle", "bamboo"], 0.6, 0.7, "uncommon",
      [fill("#151515"), grad("#5A6A7A", 0.6, "hind"), veins("#0A0A0A"), basal("#D8302A", 1, "fore"),
       ring("#9AA4B0", 1, "hind"), fill(K, "tail")]),
    S("emerald_swallowtail", "Emerald Swallowtail", "swallowtail", ["jungle"], 0.55, 0.8, "rare",
      [fill("#1A2A1E"), speckle("#3A7A4A", 0.4, "all", 5), line("#3AD07A", (3, 1), (5, 6), 1.3),
       line("#3AD07A", (4, 7), (4, 11), 1.3), border("#0E160E", 1), fill(K, "tail")]),
    S("ulysses", "Ulysses Butterfly", "swallowtail", ["jungle"], 0.6, 0.7, "rare",
      [fill("#101418"), circle("#2A9AF0", (3, 5), 4.2), sheen("#7AD0FF", 0.5), border("#0A0C10", 2), fill(K, "tail")]),
    S("common_rose", "Common Rose", "swallowtail", ["jungle", "savanna"], 0.55, 0.8, "uncommon",
      [fill("#141414"), veins("#3A3A3A"), circle(W, (3, 9), 1.3), ring("#E0405A", 1, "hind", True), fill(K, "tail")],
      body="#D8304A"),
    S("five_bar_swordtail", "Five-bar Swordtail", "kite", ["jungle", "bamboo"], 0.48, 0.9, "uncommon",
      [fill("#F4F0D8"), line(K, (1, 0), (1, 5), 0.8), line(K, (3, 0), (2, 4), 0.8), line(K, (5, 0), (4, 3), 0.8),
       line(K, (7, 0), (6, 2), 0.8), line(K, (0, 7), (3, 10), 0.8), border(K, 1), fill(K, "tail")]),
    S("tailed_jay", "Tailed Jay", "hairstreak", ["jungle", "mangrove_swamp"], 0.42, 1.2, "common",
      [fill("#1A1A1A"), checker("#7EE07A"), spots("#7EE07A", [(2, 2), (4, 4), (6, 2), (3, 8), (5, 9)]),
       border("#0E0E0E", 1)]),
    S("common_bluebottle", "Common Bluebottle", "pointed", ["jungle", "mangrove_swamp"], 0.48, 1.1, "common",
      [fill("#121212"), line("#4AB8D8", (6, 0), (2, 6), 1.2), line("#4AB8D8", (2, 7), (2, 11), 1.1),
       ring("#4AB8D8", 1, "hind", True)]),
    S("leopard_lacewing", "Leopard Lacewing", "classic", ["jungle", "savanna"], 0.45, 1.0, "common",
      [fill("#E8781E"), grad("#F2A04A", 0.3), stripes("#2A1408", 5, 0, "inner", 3), line(W, (6, 0), (8, 3), 0.8),
       border(K, 1), ring(W, 0, "all")]),
    S("purple_emperor", "Purple Emperor", "classic", ["forest", "roofed"], 0.55, 0.8, "rare",
      [fill("#3A2A3A"), sheen("#8A5AD8", 0.7), line(W, (6, 1), (4, 6), 1.0), line(W, (3, 7), (5, 10), 1.0),
       eye((2, 11), [(1.0, "#E8902A"), (0.4, K)]), border("#1A141A", 1)]),
    S("dead_leaf", "Dead Leaf Butterfly", "leaf", ["jungle", "bamboo"], 0.55, 0.8, "rare",
      [fill("#1E2E5A"), basal("#3A5AB0", 3), line("#E8822A", (3, 3), (8, 2), 1.4), spots(W, [(8, 1), (7, 0)]),
       border("#141E3A", 1)]),
    S("great_eggfly", "Great Eggfly", "classic", ["jungle", "savanna"], 0.5, 0.9, "uncommon",
      [fill("#121214"), eye((4, 3), [(1.8, "#6A5AD8"), (1.2, "#F0F0F8")]), eye((3, 9), [(2.0, "#6A5AD8"), (1.4, "#F0F0F8")]),
       spots(W, [(7, 1), (8, 2)])]),
    SECTION("Savanna & Desert"),
    S("plain_tiger", "Plain Tiger", "pointed", ["savanna", "desert"], 0.48, 0.9, "common",
      [fill("#E89A4A"), grad("#F2BA7A", 0.3), apex(K, 3.0), line(W, (5, 1), (8, 3), 0.9), border(K, 1, "hind"),
       ring(W, 0, "hind"), spots(K, [(3, 8), (4, 9)])], accent=W),
    S("blue_tiger", "Blue Tiger", "pointed", ["savanna", "jungle"], 0.48, 0.9, "common",
      [fill("#9EC8F0"), veins("#1A1E2A", 1.4), border("#1A1E2A", 2), ring(W, 1, "all", True)], accent=W),
    S("common_jezebel", "Common Jezebel", "classic", ["jungle", "forest"], 0.45, 1.0, "common",
      [fill("#F2F2EE"), veins(K), border(K, 1), ring("#E0302A", 1, "hind", True), ring("#F2D04A", 2, "hind", True)]),
    S("yellow_pansy", "Yellow Pansy", "classic", ["savanna"], 0.38, 1.2, "common",
      [fill("#1A1A1A"), circle("#F0C83A", (4, 4), 1.9), circle("#F0C83A", (5, 10), 1.6), circle("#3A6AE0", (2, 9), 1.0),
       spots(W, [(7, 1)])]),
    S("blue_pansy", "Blue Pansy", "classic", ["savanna", "desert"], 0.38, 1.2, "common",
      [fill("#1A1A2A"), fill("#3A6AE0", "hind"), sheen("#7AA0F8", 0.5, "hind"), line(W, (5, 1), (8, 3), 0.9),
       eye((6, 4), [(1.0, "#E8902A"), (0.4, K)]), eye((3, 10), [(1.2, "#E8902A"), (0.5, K)]), border(K, 1)]),
    S("lime_swallowtail", "Lime Swallowtail", "classic", ["desert", "savanna"], 0.5, 0.9, "common",
      [fill("#141414"), speckle("#E8E080", 0.55, "all", 21), eye((1, 10), [(1.2, "#3A6AE0"), (0.6, "#E0402A")]),
       border("#0A0A0A", 1), ring("#E8E080", 1, "all", True)]),
    S("cloudless_sulphur", "Cloudless Sulphur", "classic", ["plains", "savanna"], 0.42, 1.2, "common",
      [fill("#F2E64A"), grad("#F8F08A", 0.4), border("#E0B030", 1), spots("#C88A20", [(4, 3)])]),
    S("dogface", "California Dogface", "classic", ["mesa", "desert", "savanna"], 0.42, 1.2, "uncommon",
      [fill("#F0C830"), apex(K, 4.2), border(K, 1, "fore"), spots(K, [(4, 3)]), border("#E0902A", 1, "hind")]),
    S("desert_marble", "Desert Marble", "classic", ["desert", "mesa"], 0.34, 1.3, "uncommon",
      [fill("#F4F0E4"), speckle("#8A9A6A", 0.4, "hind", 13), apex("#4A4A3A", 1.8), spots("#4A4A3A", [(4, 3)])]),
    S("pygmy_blue", "Western Pygmy Blue", "rounded", ["desert", "mesa", "beach"], 0.22, 1.7, "common",
      [fill("#8A6A4A"), basal("#5A7AD0", 3), border("#4A3424", 1), ring(W, 0)]),
    S("two_tailed_pasha", "Two-tailed Pasha", "swallowtail", ["savanna", "mesa"], 0.55, 0.8, "rare",
      [fill("#2A1E18"), line("#F2E2B8", (5, 0), (3, 13), 1.2), border("#E8902A", 1), ring("#4A8AD0", 1, "hind", True),
       fill("#2A1E18", "tail")]),
    SECTION("Wonders of the World"),
    S("cherry_blossom", "Cherry Blossom Wing", "classic", ["cherry_grove"], 0.42, 1.0, "common",
      [fill("#F6BCD6"), grad("#FFF0F6", 0.5), speckle(W, 0.18, "all", 4), border("#E07AA8", 1), basal("#D06A98", 1)],
      body="#5A2A3A"),
    S("azalea_flutter", "Azalea Flutter", "classic", ["lush_caves"], 0.4, 1.0, "uncommon",
      [fill("#6A9A3A"), grad("#8AB84A", 0.3), circle("#E58AC6", (4, 3), 1.3), circle("#E58AC6", (6, 1), 0.9),
       circle("#E58AC6", (4, 9), 1.2), border("#3A5A1E", 1)]),
    S("glowberry", "Glow Berry Wing", "rounded", ["lush_caves"], 0.36, 1.2, "uncommon",
      [fill("#2A3A1A"), spots("#F8B93A", [(2, 2), (4, 4), (6, 2), (3, 8), (5, 10), (2, 11), (7, 3)]),
       spots("#FFE08A", [(4, 1), (6, 9)]), border("#1A2410", 1)]),
    S("sculk_wisp", "Sculk Wisp", "longwing", ["deep_dark"], 0.45, 0.7, "rare",
      [fill("#0E2A30"), veins("#2ADFE0", 0.8), speckle("#4AF0F0", 0.12, "all", 9), border("#05141A", 1)],
      body="#0A1A20", accent="#2ADFE0"),
    S("crimson_ember", "Crimson Ember", "pointed", ["crimson_forest"], 0.45, 1.1, "uncommon",
      [fill("#8A1A1A"), grad("#F0602A", 0.6), speckle("#F8B43A", 0.15, "all", 17), border("#2A0A0A", 1)],
      body="#4A0E0E", accent="#F0602A"),
    S("warped_wanderer", "Warped Wanderer", "classic", ["warped_forest"], 0.45, 0.9, "uncommon",
      [fill("#13696A"), grad("#2AB5A0", 0.5), eye((5, 3), [(1.2, "#E86AC0"), (0.5, "#2A0A2A")]),
       circle("#E86AC0", (4, 10), 1.0), border("#1A1A2E", 1)], body="#1A1A2E"),
    S("ender_wing", "Ender Wing", "birdwing", ["the_end"], 0.5, 0.7, "rare",
      [fill("#1A1428"), speckle("#C77AF0", 0.2, "all", 23), eye((5, 3), [(1.5, "#2AA88A"), (0.7, "#0E5A4A")]),
       border("#0A0814", 1)], body="#0A0814", accent="#C77AF0"),
    S("amethyst_wing", "Amethyst Wing", "classic", ["meadow", "mountains"], 0.42, 1.0, "rare",
      [fill("#9A6AD8"), sheen("#E0C2FF", 0.7), border("#4A2A7A", 1), veins("#6A3AA8", 0.7)]),
    S("prismarine_flutter", "Prismarine Flutter", "classic", ["beach"], 0.4, 1.1, "uncommon",
      [fill("#5AA898"), checker("#2E6A62"), sheen("#9AE0D0", 0.5), border("#2A4A48", 1)]),
    S("frost_wing", "Frost Wing", "classic", ["frozen"], 0.4, 1.0, "uncommon",
      [fill("#E8F2FA"), grad("#9AC4EE", 0.6), veins("#B8D8F4", 0.7), border("#6A9AD0", 1), ring(W, 0)], body="#4A5A7A"),
]

SPECIES += [
    S("marbled_white", "Marbled White", "classic", ["meadow", "plains"], 0.42, 1.1, "common",
      [fill("#F4F2EA"), checker("#2A2A2A"), stripes("#2A2A2A", 4, 0, "inner", 1), basal("#2A2A2A", 2), border("#2A2A2A", 1),
       ring(W, 0)], category="Meadows & Fields"),
    S("ringlet", "Ringlet", "rounded", ["forest", "meadow"], 0.38, 1.2, "common",
      [fill("#3A2E28"), eye((5, 3), [(1.0, "#E8C87A"), (0.5, K)]), eye((4, 9), [(1.0, "#E8C87A"), (0.5, K)]),
       eye((5, 11), [(0.9, "#E8C87A"), (0.4, K)]), ring("#C8B8A0", 0)], category="Meadows & Fields"),
    S("meadow_brown", "Meadow Brown", "classic", ["plains", "meadow"], 0.42, 1.2, "common",
      [fill("#6A5040"), circle("#E8A04A", (5, 3), 1.6), eye((6, 2), [(0.8, K), (0.3, W)]), border("#4A3828", 1)], category="Meadows & Fields"),
    S("speckled_wood", "Speckled Wood", "classic", ["forest", "roofed", "taiga"], 0.4, 1.1, "common",
      [fill("#4A3A2A"), speckle("#E8D07A", 0.35, "inner", 31), eye((7, 2), [(0.8, K), (0.3, W)]),
       eye((5, 10), [(0.9, K), (0.3, W)]), border("#2A2018", 1)], category="Woodland"),
    S("wall_brown", "Wall Brown", "classic", ["mountains", "mesa"], 0.4, 1.2, "common",
      [fill("#D8902A"), stripes("#5A3A18", 3, 0, "inner", 1), eye((7, 2), [(1.0, K), (0.4, W)]),
       eye((5, 10), [(0.8, K), (0.3, W)]), border("#4A2A10", 1)], category="Meadows & Fields"),
    S("camberwell_beauty", "Camberwell Beauty", "scalloped", ["taiga", "birch"], 0.55, 0.9, "rare",
      [fill("#3A1A20"), border("#F2E2A0", 2), ring("#4A7AD8", 2, "all", True), spots("#F2E2A0", [(6, 0), (7, 1)])], category="Woodland"),
    S("map_butterfly", "Map Butterfly", "classic", ["forest", "taiga"], 0.38, 1.2, "uncommon",
      [fill("#1E1612"), line("#F2EEE0", (4, 1), (2, 6), 0.8), line("#F2EEE0", (2, 7), (4, 11), 0.9),
       line("#E8822A", (1, 9), (6, 9), 0.6), spots(W, [(7, 1), (8, 2)]), border("#120E0A", 1)], category="Woodland"),
    S("chequered_skipper", "Chequered Skipper", "skipper", ["birch", "taiga"], 0.27, 1.8, "uncommon",
      [fill("#3A2A1A"), checker("#E8B84A"), stripes("#E8B84A", 4, 2, "inner", 2), ring("#E8B84A", 0)], body="#3A2A1A", category="Skippers"),
    S("palamedes_swallowtail", "Palamedes Swallowtail", "swallowtail", ["swamp", "mangrove_swamp"], 0.6, 0.8, "uncommon",
      [fill("#1A1610"), line("#F2D84A", (1, 2), (1, 12), 1.1), ring("#F2D84A", 1, "all", False),
       ring("#5A7AD0", 2, "hind", True), fill(K, "tail")], category="Swallowtails"),
    S("banded_orange", "Banded Orange Heliconian", "longwing", ["jungle", "savanna"], 0.44, 1.0, "common",
      [fill("#F08A2A"), line(K, (2, 1), (8, 1), 0.7), line(K, (3, 3), (8, 3), 0.7), line(K, (1, 9), (5, 9), 0.7),
       border("#3A1A0A", 1)], category="Rainforest"),
]


SPECIES = [s for s in SPECIES if s is not None]
assert len(SPECIES) == 100, len(SPECIES)

CATEGORIES = ["Meadows & Fields", "Swallowtails", "Woodland", "Blues & Coppers", "Skippers", "Rainforest",
              "Savanna & Desert", "Mountains & Tundra", "Wetlands & Coasts", "Wonders of the World",
              "The Nether", "The End"]

INFO = {
    "monarch": "Famous for flying thousands of kilometres on its yearly migration. Its caterpillars eat only milkweed, which makes the adults taste terrible to birds.",
    "viceroy": "Looks almost exactly like a Monarch, but the black line across its hindwings gives it away.",
    "painted_lady": "One of the most widespread butterflies on Earth. Huge swarms migrate between continents every year.",
    "red_admiral": "A bold black-and-red flier that loves sipping juice from fallen, overripe fruit.",
    "peacock": "Flashes the big eyespots on its wings to startle hungry birds, and can even hiss by rubbing its wings together.",
    "common_buckeye": "Its eyespots stare back at predators. Males perch on bare ground and chase anything that flies past.",
    "cabbage_white": "One of the most common garden butterflies. Its caterpillars love cabbage leaves.",
    "orange_tip": "Only the males have bright orange wing tips. Its mottled green underside hides it among flowers.",
    "brimstone": "Its butter-yellow, leaf-shaped wings may be where the word 'butterfly' comes from.",
    "clouded_yellow": "A strong migrant that arrives from the south in warm summers and races over clover fields.",
    "tiger_swallowtail": "A large yellow swallowtail with tiger stripes. Its caterpillars have fake eyespots that look like a snake's eyes.",
    "black_swallowtail": "Its caterpillars eat carrot, parsley and dill, and push out a smelly orange 'horn' when threatened.",
    "zebra_swallowtail": "Its long, sword-like tails and zebra stripes make it one of the most elegant butterflies.",
    "pipevine_swallowtail": "Its caterpillars eat poisonous pipevine plants, so the shimmering blue adults are toxic to predators.",
    "giant_swallowtail": "One of the largest butterflies in North America. Its caterpillars look just like bird droppings!",
    "old_world_swallowtail": "A striking yellow-and-black swallowtail found from Europe to Japan, often gliding over mountain tops.",
    "scarce_swallowtail": "Despite its name it is fairly widespread. It glides gracefully with its long tails trailing behind.",
    "spicebush_swallowtail": "Its hindwings shimmer blue-green. The caterpillars hide inside rolled-up leaves during the day.",
    "mourning_cloak": "One of the longest-lived butterflies, surviving up to a year by hibernating through winter.",
    "question_mark": "Named after the tiny silver question mark on the underside of its hindwings.",
    "comma": "Its ragged wings look like a dead leaf when closed, marked with a small white comma.",
    "small_tortoiseshell": "A cheerful garden butterfly that often wanders into houses to spend the winter.",
    "red_spotted_purple": "It copies the colours of the toxic Pipevine Swallowtail to fool predators.",
    "white_admiral": "A graceful woodland glider with a bold white band across its dark wings.",
    "great_spangled_fritillary": "Its underside is decorated with shiny silver spots, like spangles on a costume.",
    "pearl_bordered_fritillary": "A small fritillary named for the row of pearl-white spots along its wing edges.",
    "gulf_fritillary": "Bright orange above with brilliant silver patches underneath. Its caterpillars feed on passion vines.",
    "baltimore_checkerspot": "Wears the orange and black colours of Lord Baltimore's coat of arms.",
    "marsh_fritillary": "Its caterpillars live together in silk webs, basking in the sun in big black clusters.",
    "common_blue": "Males are bright sky blue while females are mostly brown. Ants guard its caterpillars.",
    "adonis_blue": "Possibly the brightest blue butterfly in Europe, found on sunny chalk grassland.",
    "holly_blue": "Usually the first blue butterfly of spring, fluttering high around holly and ivy.",
    "karner_blue": "A tiny, endangered blue that depends on wild lupine plants to survive.",
    "small_copper": "A feisty little butterfly that defends its sunny patch against much bigger insects.",
    "large_copper": "A glowing copper-orange butterfly of wetlands that has become very rare in the wild.",
    "purple_hairstreak": "Lives high in oak treetops and drinks sweet honeydew instead of nectar.",
    "green_hairstreak": "The underside of its wings is bright green, so it vanishes when it lands on a leaf.",
    "apollo": "A mountain butterfly with red eyespots and almost see-through wings, built for cold, thin air.",
    "silver_spotted_skipper": "A speedy skipper with a bold silver patch on its hindwing.",
    "large_skipper": "Basks with its wings held like a tiny fighter jet, then zips away in a flash.",
    "fiery_skipper": "A bright orange skipper common on lawns. Its caterpillars eat grass.",
    "long_tailed_skipper": "A skipper with long tails and a shimmering blue-green body.",
    "checkered_skipper": "Covered in a checkerboard of white spots, it darts low over open ground.",
    "blue_morpho": "Its wings are not actually blue: tiny scales bend the light to create the dazzling colour.",
    "sunset_morpho": "A giant morpho with warm amber wings that glides slowly through the rainforest canopy.",
    "white_morpho": "A ghostly pearl-white morpho that drifts through jungle clearings.",
    "owl_butterfly": "The huge eyespots on its hindwings look just like an owl's eyes.",
    "glasswing": "Its wings are clear like glass, making it nearly invisible in flight.",
    "postman": "It visits the same flowers every day along a set route, just like a postman.",
    "zebra_longwing": "Sleeps in groups, returning to the same roost every evening. It can live for months.",
    "julia": "A fast, bright orange flier that sometimes drinks the tears of caimans for salt!",
    "tiger_longwing": "Its tiger pattern warns birds that it is poisonous to eat.",
    "doris_longwing": "Its hindwings can have blue, green or red rays depending on where it lives.",
    "sara_longwing": "A small longwing with a blue sheen that lays its eggs in neat clusters.",
    "malachite": "Named after the green gemstone because of its bright green wing windows.",
    "rajah_brooke_birdwing": "Named after Rajah James Brooke. Its emerald bands look like the feathers of a bird.",
    "queen_alexandra_birdwing": "The largest butterfly in the world, with wings up to 28 cm (11 inches) across!",
    "golden_birdwing": "A giant whose glowing golden hindwings shine in the sunlight.",
    "great_mormon": "Females come in many different colour forms, some copying poisonous butterflies.",
    "emerald_swallowtail": "Its glittering green bands are made by tiny bowl-shaped scales that mix light.",
    "ulysses": "Its electric blue wings can be seen flashing from far across the forest.",
    "common_rose": "Its bright red body warns predators that it is poisonous to eat.",
    "five_bar_swordtail": "Has incredibly long tails and black bars like a striped flag.",
    "tailed_jay": "A fast, restless flier covered in bright green spots.",
    "common_bluebottle": "A speedy swallowtail with a glowing blue-green band. Males gather at puddles to drink.",
    "leopard_lacewing": "Spotted like a leopard on top, with delicate lace patterns underneath.",
    "purple_emperor": "Its wings flash purple only at certain angles. It prefers tree sap to flowers.",
    "dead_leaf": "With its wings closed it looks exactly like a dry dead leaf, complete with vein and stalk.",
    "great_eggfly": "Males have glowing white-and-violet patches like eggs on their dark wings.",
    "plain_tiger": "Also called the African Monarch. It is toxic to predators, and other butterflies copy its colours.",
    "blue_tiger": "Its pale blue streaks are a warning sign. It migrates in huge swarms.",
    "common_jezebel": "Its bright red and yellow markings warn birds that it tastes bad.",
    "yellow_pansy": "Big yellow patches and a small blue spot make it easy to recognise.",
    "blue_pansy": "Males have shining blue hindwings and love to bask on bare, sunny ground.",
    "lime_swallowtail": "A speckled swallowtail with no tails, often found in citrus orchards.",
    "cloudless_sulphur": "A big lemon-yellow butterfly that flies fast and straight across open fields.",
    "dogface": "The yellow pattern on each forewing looks like the head of a poodle.",
    "desert_marble": "Its marbled green underside helps it hide among desert plants.",
    "pygmy_blue": "One of the smallest butterflies in the world, barely 1.5 cm across.",
    "two_tailed_pasha": "A powerful flier with two tails on each hindwing that loves fermenting fruit.",
    "cherry_blossom": "Found only in Cherry Groves, where its pink wings blend into the falling petals.",
    "azalea_flutter": "Lives in Lush Caves and sips nectar from flowering azalea.",
    "glowberry": "Its spots glow like the glow berries that hang in Lush Caves.",
    "sculk_wisp": "A silent flier of the Deep Dark. Its glowing veins pulse like sculk.",
    "crimson_ember": "Born in the Crimson Forest. Its wings shimmer like embers and it never burns.",
    "warped_wanderer": "Drifts through Warped Forests, unbothered by the Nether's heat.",
    "ender_wing": "A mysterious butterfly of the End, speckled like the night sky.",
    "amethyst_wing": "Its wings sparkle like amethyst crystals. It is rarely seen in mountain meadows.",
    "prismarine_flutter": "Found along beaches, its scales shine like prismarine.",
    "frost_wing": "Survives the coldest snowy biomes, with icy veins that glitter in the sun.",
    "marbled_white": "Despite looking like a white, it is actually a member of the brown butterfly family.",
    "ringlet": "Named for the small rings on its wings. It even flies on cloudy, drizzly days.",
    "meadow_brown": "One of the most common grassland butterflies, flying even in dull weather.",
    "speckled_wood": "Loves dappled sunlight in woods, where its spots match the light on the ground.",
    "wall_brown": "Loves to bask on walls and stony paths, soaking up the warmth.",
    "camberwell_beauty": "A rare visitor with deep maroon wings and a creamy border.",
    "map_butterfly": "The lines on its underside look like a map. Its spring and summer forms look completely different.",
    "chequered_skipper": "A tiny dark skipper covered in golden chequers.",
    "palamedes_swallowtail": "A large swamp swallowtail that lives where red bay trees grow.",
    "banded_orange": "A bright orange longwing with dark bands, common in tropical forests.",
}
assert set(INFO) == {s.id for s in SPECIES}, set(INFO) ^ {s.id for s in SPECIES}

# ---------------------------------------------------------------------------
# The second wave: pattern templates turn a one-line description into a wing
# ---------------------------------------------------------------------------

SHAPE_SCALE = {"classic": 0.42, "pointed": 0.48, "rounded": 0.32, "swallowtail": 0.56, "kite": 0.5,
               "longwing": 0.44, "leaf": 0.5, "scalloped": 0.45, "skipper": 0.27, "birdwing": 0.75,
               "hairstreak": 0.3}
SHAPE_FLAP = {"skipper": 1.7, "rounded": 1.4, "hairstreak": 1.5, "birdwing": 0.7, "swallowtail": 0.85,
              "kite": 0.9, "longwing": 0.8}
RARITY_CODE = {"c": "common", "u": "uncommon", "r": "rare", "l": "legendary"}


def light(c, t=0.35):
    return hexc(mix(c, "#FFFFFF", t))


def dark(c, t=0.45):
    return hexc(shade(c, 1 - t))


def pattern_feats(kind, cols, r):
    a, b, c = cols[0], cols[1], cols[2] if len(cols) > 2 else W
    d = cols[3] if len(cols) > 3 else K
    bw = r.choice([1, 1, 2])
    j = lambda lo, hi: round(r.uniform(lo, hi), 1)
    if kind == "tiger":
        return [fill(a), grad(light(a), 0.45), veins(b, j(0.8, 1.1)), border(b, 2), ring(c, 1),
                spots(c, [(7, 1), (8, 2), (6, 1)][:r.randint(1, 3)])]
    if kind == "eyes":
        f = [fill(a), grad(light(a, 0.25), 0.4),
             eye((j(5, 7), j(2, 3.5)), [(j(1.1, 1.5), c), (j(0.45, 0.6), d)])]
        for _ in range(r.randint(1, 2)):
            f.append(eye((j(3.5, 6.5), j(9, 11)), [(j(0.8, 1.2), c), (0.4, d)]))
        return f + [border(b, bw)]
    if kind == "band":
        f = [fill(a), line(c, (j(4, 6.5), 0), (j(1, 3), j(6, 7.5)), j(0.9, 1.4))]
        if r.random() < 0.6:
            f.append(line(d if len(cols) > 3 else c, (0.5, j(8.5, 10)), (j(5, 7), j(9, 11)), j(0.7, 1.0)))
        f += [border(b, bw), ring(c, 1, "all", r.random() < 0.7)]
        return f
    if kind == "tip":
        f = [fill(a), grad(light(a, 0.3), 0.3), apex(b, j(2.5, 4.2)), border(b, 1, "fore")]
        if r.random() < 0.6:
            f.append(spots(b, [(j(3.5, 5), j(2.5, 3.5))]))
        if c.upper() != a.upper():
            f.append(basal(c, 1, "hind"))
        return f
    if kind == "checker":
        return [fill(a), checker(b), ring(c, 1, "all", True), border(b, bw), basal(dark(a, 0.3), 1)]
    if kind == "stripes":
        return [fill(a), stripes(b, r.choice([3, 4]), r.randint(0, 2), "inner", r.choice([1, -1])),
                border(b, 2), ring(c, 1, "hind", True), fill(b, "tail")]
    if kind == "sheen":
        return [fill(a), grad(c, j(0.35, 0.6)), sheen(c, 0.6), border(b, bw), ring(W, 0)]
    if kind == "basal":
        f = [fill(a), basal(b, r.choice([2, 3])), border(dark(a, 0.6), 1), ring(c, 0)]
        if r.random() < 0.5:
            f.append(spots(c, [(j(4, 6), j(9.5, 11)), (j(6, 8), j(9, 10.5))]))
        return f
    if kind == "spotted":
        pts = [(j(1, 8), j(0.5, 12.5)) for _ in range(r.randint(5, 9))]
        return [fill(a), spots(c, pts), border(b, bw), ring(c, 0, "all", True)]
    if kind == "speckle":
        f = [fill(a), speckle(b, j(0.22, 0.38), r.choice(["all", "inner", "hind"]), r.randint(1, 999)),
             border(c, bw)]
        if r.random() < 0.4:
            f.append(apex(b, 1.8))
        return f
    if kind == "glass":
        reg = r.choice(["all", "fore"])
        return [fill(a), clear(reg), veins(b, 0.7, reg), border(b, 2), apex(c, j(1.5, 2.5)), ring(c, 1, "hind")]
    if kind == "split":
        return [fill(a, "fore"), fill(b, "hind"), grad(light(a), 0.3, "fore"), border(d, 1),
                spots(c, [(j(6, 8), j(1, 3))]), ring(c, 1, "hind", True)]
    if kind == "rays":
        return [fill(a), veins(b, j(1.1, 1.5)), border(b, 2), ring(c, 1, "all", True)]
    if kind == "patch":
        return [fill(a), circle(c, (j(4, 6), j(2, 4)), j(1.4, 2.2), "fore"),
                circle(d if len(cols) > 3 else c, (j(3, 5), j(9, 11)), j(1.2, 1.8), "hind"), border(b, bw)]
    if kind == "longwing":
        f = [fill(a), line(c, (j(3, 4), j(1, 2)), (j(7, 9), j(2, 3.5)), j(1.0, 1.4))]
        hb = d if len(cols) > 3 else b
        if r.random() < 0.5:
            f.append(veins(hb, 1.0, "hind"))
        else:
            f.append(line(hb, (0.5, j(9, 10)), (j(5, 6), j(10, 11.5)), 0.9))
        return f + [border(K if lum(rgb(a)) > 90 else dark(a, 0.5), 1), spots(W, [(8, 1)])]
    if kind == "ocelli":
        f = [fill(a), grad(light(a, 0.25), 0.4), border(b, 1)]
        for k in range(r.randint(3, 5)):
            f.append(eye((2.5 + k * 1.3, 10.5 + (k % 2) * 0.5), [(0.75, c), (0.35, d)]))
        if r.random() < 0.6:
            f.append(eye((j(5.5, 7), j(2, 3)), [(0.9, c), (0.4, d)]))
        return f
    if kind == "marble":
        return [fill(a), speckle(b, j(0.4, 0.55), "hind", r.randint(1, 999)), apex(b, 2.0),
                spots(c, [(j(3.5, 5), 3)]), border(b, 1)]
    if kind == "gradient":
        return [fill(a), grad(b, j(0.6, 0.9)), ring(c, 1, "all", r.random() < 0.6), border(d, 1)]
    if kind == "dusk":
        return [fill(a), grad(b, 0.4), speckle(c, 0.1, "all", r.randint(1, 999)),
                eye((j(5.5, 7), j(2, 3)), [(0.8, c), (0.35, d)]), border(d, 1)]
    if kind == "zebra":
        return [fill(a), stripes(b, 2, r.randint(0, 1), "all", r.choice([1, -1])), border(b, 1),
                ring(c, 1, "hind", True)]
    if kind == "jewel":
        return [fill(a), basal(b, r.choice([2, 3])), grad(c, 0.35), sheen(c, 0.7), border(d, 1), ring(c, 0)]
    if kind == "flame":
        return [fill(a), grad(b, j(0.7, 0.95)), stripes(c, 4, r.randint(0, 3), "inner", -1), border(d, 1)]
    if kind == "crescent":
        return [fill(a), ring(b, 1, "all", False), ring(c, 2, "all", True), border(dark(a, 0.5), 1)]
    if kind == "edge":
        return [fill(a), basal(dark(a, 0.25), 1), border(b, 2), ring(c, 1, "all", True)]
    raise ValueError(kind)


COLOUR_NAMES = [(0, "red"), (18, "orange"), (42, "golden"), (58, "yellow"), (80, "lime"), (150, "green"),
                (175, "teal"), (195, "sky-blue"), (225, "blue"), (260, "violet"), (290, "purple"),
                (320, "pink"), (345, "red")]


def colour_name(c):
    h, s, v = colorsys.rgb_to_hsv(*(x / 255 for x in rgb(c)))
    if v < 0.22:
        return "black"
    if s < 0.12:
        return "white" if v > 0.85 else ("grey" if v > 0.45 else "charcoal")
    if s < 0.45 and v > 0.8 and 20 <= h * 360 <= 70:
        return "cream"
    if 15 <= h * 360 <= 45 and v < 0.6:
        return "brown"
    name = "red"
    for deg, n in COLOUR_NAMES:
        if h * 360 >= deg:
            name = n
    return name


PATTERN_TEXT = {
    "tiger": "{a} wings laced with {b} veins warn birds that it tastes awful",
    "eyes": "{a} wings carry bold {c} eyespots that startle anything trying to eat it",
    "band": "a bright {c} band slashes across its {a} wings",
    "tip": "{a} wings are dipped in {b} at the tips",
    "checker": "{a} wings are tiled with a {b} chequerboard",
    "stripes": "{a} wings are striped with {b}",
    "sheen": "{a} wings flash {c} when the light catches them",
    "basal": "{a} wings glow {b} close to the body",
    "spotted": "{a} wings are dotted with {c} spots",
    "speckle": "{a} wings are dusted with {b} speckles",
    "glass": "its wings are clear as glass, edged with {b}",
    "split": "its forewings are {a} while its hindwings are {b}",
    "rays": "{b} rays run through its {a} wings",
    "patch": "{a} wings carry big {c} patches",
    "longwing": "long {a} wings carry a {c} band",
    "ocelli": "a row of little {c} eyespots lines its {a} hindwings",
    "marble": "{b} marbling covers its {a} underside",
    "gradient": "its wings fade from {a} to {b}",
    "dusk": "its dusky {a} wings are freckled with {c}",
    "zebra": "{a} and {b} stripes make it look like a tiny zebra",
    "jewel": "{a} wings shimmer with {c} like a gemstone",
    "flame": "{a} wings flicker into {b} like a flame",
    "crescent": "{a} wings are edged with {b} crescents",
    "edge": "{a} wings wear a wide {b} border",
}
REALM_TEXT = {
    "The Nether": ["It shrugs off fire and drinks the heat rising from lava.",
                   "Piglins have been seen chasing it, though nobody has seen one caught.",
                   "Its eggs are laid where the ground stays warm, and the caterpillars nibble Nether fungus.",
                   "It never needs to land on water, since there is none to be found where it lives.",
                   "Its scales are said to be fireproof, which is why it can fly through flame unharmed."],
    "The End": ["It seems to blink short distances when startled, much like an Enderman.",
                "Its caterpillars feed on chorus plants and sometimes pop up somewhere unexpected.",
                "It drifts over the void without fear, carried by currents nobody else can feel.",
                "Shulkers ignore it completely, and it often rests on the walls of End cities.",
                "It glows faintly in the dark, so it is easy to spot against the black sky."],
    "": ["Males often gather at damp mud to sip minerals.",
         "It basks in the morning sun to warm up before it can fly.",
         "It folds its wings tight when it lands, hiding its colours from birds.",
         "It is a fast, nervous flier that is hard to follow.",
         "Its caterpillars spin small silk shelters in the leaves.",
         "It patrols the same sunny spot day after day.",
         "It sips nectar from almost any flower it can find.",
         "It flies low and close to the ground.",
         "In cool weather it can rest without moving for days.",
         "Several of them often roost together in the same tree.",
         "It is most active in the hottest hours of the day.",
         "Females test each leaf with their feet before laying an egg on it."],
}


def describe(cat, name, kind, cols, habitat, r):
    names = [colour_name(c) for c in cols] + ["black"]
    first = PATTERN_TEXT[kind].format(a=names[0], b=names[1], c=names[2])
    first = first[0].upper() + first[1:] + "."
    where = HABITAT_LABEL[habitat[0]]
    realm = cat if cat in ("The Nether", "The End") else ""
    second = r.choice(REALM_TEXT[realm])
    lead = r.choice([f"A {where} native. ", f"Found in the {where}. ", "", f"Look for it in the {where}. "])
    return lead + first + " " + second


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower().replace("'", "")).strip("_")


EXTRA_HABITATS = {
    "grove": "Groves", "mega": "Old Growth Taiga", "pale_garden": "Pale Garden",
    "soulsand_valley": "Soul Sand Valley", "basalt_deltas": "Basalt Deltas", "nether_wastes": "Nether Wastes",
}


def second_wave():
    out = []
    for cat, name, shape, habitat, kind, cols, code in species_more.rows():
        sid = slug(name)
        r = random.Random(sid)
        rarity = RARITY_CODE[code]
        scale = SHAPE_SCALE[shape] * r.uniform(0.9, 1.1) * (1.15 if rarity == "legendary" else 1.0)
        flap = SHAPE_FLAP.get(shape, 1.0) * r.uniform(0.9, 1.15)
        body = dark(min(cols, key=lambda c: lum(rgb(c))), 0.2)
        sp = Species(sid, name, shape, habitat, round(scale, 3), round(flap, 2), rarity,
                     pattern_feats(kind, cols, r), body=body, accent=cols[2] if len(cols) > 2 else None,
                     category=cat)
        INFO[sid] = describe(cat, name, kind, cols, habitat, r)
        out.append(sp)
    return out

# ---------------------------------------------------------------------------
# Habitats, life-cycle styles
# ---------------------------------------------------------------------------
UNDERGROUND = {"lush_caves", "deep_dark"}
NETHER = {"crimson_forest", "warped_forest"}
HABITAT_LABEL = {
    "plains": "Plains", "meadow": "Meadow", "flower_forest": "Flower Forest", "savanna": "Savanna",
    "swamp": "Swamp", "river": "River", "desert": "Desert", "forest": "Forest", "birch": "Birch Forest",
    "roofed": "Dark Forest", "taiga": "Taiga", "mountains": "Mountains", "jungle": "Jungle", "bamboo": "Bamboo Jungle",
    "mangrove_swamp": "Mangrove Swamp", "mesa": "Badlands", "beach": "Beach", "cherry_grove": "Cherry Grove",
    "lush_caves": "Lush Caves", "deep_dark": "Deep Dark", "crimson_forest": "Crimson Forest",
    "warped_forest": "Warped Forest", "the_end": "The End", "frozen": "Snowy Biomes",
}
HABITAT_LABEL.update(EXTRA_HABITATS)
NETHER |= {"soulsand_valley", "basalt_deltas", "nether_wastes"}

SPECIES += second_wave()
assert len(SPECIES) == 500, len(SPECIES)
assert len({s.id for s in SPECIES}) == 500, [s.id for s in SPECIES if [t.id for t in SPECIES].count(s.id) > 1]
assert set(INFO) == {s.id for s in SPECIES}
assert all(s.category in CATEGORIES for s in SPECIES)

# Caterpillar look by wing family.
LARVA_STYLE = {
    "pointed": "banded", "swallowtail": "swallow", "kite": "swallow", "birdwing": "tubercle",
    "classic": "spiny", "scalloped": "spiny", "leaf": "spiny", "longwing": "spiny",
    "rounded": "slug", "hairstreak": "slug", "skipper": "skipper",
}
LARVA_GEO = {"banded": "filament", "swallow": "smooth", "tubercle": "tubercle", "spiny": "spiky",
             "slug": "smooth", "skipper": "smooth"}
FOOD = {
    "banded": "Milkweed, Butterfly Bush and leaves",
    "swallow": "leaves, especially from jungle and oak trees",
    "tubercle": "jungle leaves",
    "spiny": "leaves, Coneflowers and Butterfly Bush",
    "slug": "leaves and Coneflowers",
    "skipper": "grass, leaves and Milkweed",
}

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def save_png(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


# ---------------------------------------------------------------------------
# Butterfly textures
# ---------------------------------------------------------------------------
K = rgb("#1A1612")


def paint_wing(sp):
    w = Wing(sp.shape)
    for f in sp.feats:
        f(w)
    r = random.Random(sp.id)
    # Fore/hind wing separation line.
    for p in w.hind:
        c = w.px[p]
        if c[3] and any(n in w.fore for n in ((p[0], p[1] - 1), (p[0] + 1, p[1] - 1), (p[0] - 1, p[1] - 1))):
            w.px[p] = (*shade(c[:3], 0.68), 255)
    # Light from the front, shadow at the body, punchier colour and a touch of grain.
    for p in sorted(w.mask):
        c = w.px[p]
        if not c[3]:
            continue
        f = 1.07 - 0.12 * p[1] / WH
        if p[0] == 0:
            f *= 0.8
        elif p[0] == 1:
            f *= 0.92
        if w.dist[p] == 0 and lum(c) > 60:
            f *= 1.06
        f *= 1 + (r.random() - 0.5) * 0.06
        w.px[p] = (*vivid(shade(c[:3], f)), 255)
    # Dark outline around the whole wing (but not along the body).
    outline = {}
    for u in range(WW):
        for v in range(WH):
            if (u, v) in w.mask:
                continue
            nb = [w.px[n] for n in ((u + du, v + dv) for du in (-1, 0, 1) for dv in (-1, 0, 1))
                  if n in w.mask and w.px[n][3]]
            if nb:
                darkest = min(nb, key=lum)
                outline[(u, v)] = (*mix(shade(darkest[:3], 0.35), K, 0.55), 255)
    w.px.update(outline)
    return w


def dominant_colors(wing, n=3):
    # Group similar colours (the texture is shaded) and rank the groups by area.
    groups = {}
    for p in wing.mask:
        c = wing.px.get(p, (0, 0, 0, 0))
        if c[3]:
            groups.setdefault(tuple(v // 40 for v in c[:3]), []).append(c[:3])
    ranked = sorted(groups.values(), key=len, reverse=True)
    out = [tuple(round(sum(c[i] for c in g) / len(g)) for i in range(3)) for g in ranked[:n]]
    while len(out) < n:
        out.append(out[-1] if out else (128, 128, 128))
    return out


def palette(wing):
    cols = dominant_colors(wing, 5)
    bright = max(cols, key=lambda c: sat(c) * 2 + lum(c) / 255)
    dark = min(cols, key=lum)
    light = max(cols, key=lum)
    return bright, dark, light


def body_colors(sp, wing):
    body = rgb(sp.body)
    accent = rgb(sp.accent) if sp.accent else mix(body, palette(wing)[0], 0.45)
    return body, accent


def put_box(px, uv, size, color_fn):
    """Paint every texel of a box-UV layout. color_fn(face, a, b, fw, fh) -> rgb(a) or None."""
    U, V = uv
    w, h, d = (max(1, math.ceil(s - 1e-6)) if s > 0 else 0 for s in size)
    faces = {
        "up": (U + d, V, w, d), "down": (U + d + w, V, w, d),
        "east": (U, V + d, d, h), "north": (U + d, V + d, w, h),
        "west": (U + d + w, V + d, d, h), "south": (U + 2 * d + w, V + d, w, h),
    }
    for face, (x0, y0, fw, fh) in faces.items():
        for a in range(fw):
            for b in range(fh):
                c = color_fn(face, a, b, fw, fh)
                if c is not None:
                    px[x0 + a, y0 + b] = c if len(c) == 4 else (*c, 255)


def entity_texture(sp, wing):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    px = img.load()
    # Wings use box UV on zero-height cubes, so only the "up" face is painted.
    # Up face: x grows with model +x, y grows towards the head (-z).
    for x in range(WW):
        for y in range(WH):
            v = WH - 1 - y
            left = wing.px.get((WW - 1 - x, v))
            right = wing.px.get((x, v))
            if left and left[3]:
                px[22 + x, y] = left
            if right and right[3]:
                px[22 + x, 22 + y] = right
    body, accent = body_colors(sp, wing)
    r = random.Random(sp.id + "body")

    def grain(c, amt=0.16):
        return shade(c, 1 + (r.random() - 0.5) * amt)

    # Head [2,2,2] at (0,44): dark with big compound eyes.
    eye_c = mix(shade(body, 0.6), (40, 40, 60), 0.5)
    put_box(px, (0, 44), (2, 2, 2), lambda f, a, b, fw, fh:
            eye_c if f in ("east", "west") and b == 0 else grain(shade(body, 0.9)))
    # Thorax [3,3,6] at (10,44): fuzzy.
    put_box(px, (10, 44), (3, 3, 6), lambda f, a, b, fw, fh:
            grain(mix(body, accent, 0.5 if (a + b) % 2 == 0 else 0.2), 0.25))

    # Abdomen [2,2,10] at (30,44): ringed.
    def abdomen(f, a, b, fw, fh):
        k = b if f in ("up", "down") else a
        return grain(mix(body, accent, 0.45) if k % 3 == 1 else body)
    put_box(px, (30, 44), (2, 2, 10), abdomen)
    # Antennae and their clubs.
    ant = shade(body, 0.75)
    for x in range(56, 64):
        for y in range(44, 56):
            px[x, y] = (*(ant if y < 52 else mix(ant, accent, 0.4)), 255)
    return img


def top_view(wing, sp, scale=1):
    """Full butterfly seen from above, for icons and previews."""
    off = 7
    w, h = WW * 2 + 3, WH + off
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for (u, v), c in wing.px.items():
        if c[3]:
            px[WW - 1 - u, v + off] = c
            px[WW + 3 + u, v + off] = c
    body, accent = body_colors(sp, wing)
    cx = WW
    for v in range(0, 18):
        for x in range(cx, cx + 3):
            if v < 2:
                c = shade(body, 0.9) if x == cx + 1 else mix(shade(body, 0.6), (40, 40, 60), 0.5)
            elif v < 8:
                c = mix(body, accent, 0.45 if (x + v) % 2 else 0.2)
            elif x == cx + 1 or v < 15:
                c = mix(body, accent, 0.4) if v % 3 == 1 else body
            else:
                continue
            px[x, v + off] = (*c, 255)
    ant = (*shade(body, 0.75), 255)
    for i in range(7):
        px[cx - (i // 3), off - 1 - i] = ant
        px[cx + 2 + (i // 3), off - 1 - i] = ant
    if scale != 1:
        img = img.resize((w * scale, h * scale), Image.NEAREST)
    return img


# ---------------------------------------------------------------------------
# Life-cycle textures (egg, caterpillar and chrysalis share one texture)
# ---------------------------------------------------------------------------

def larva_palette(sp, wing):
    bright, dark, light = palette(wing)
    style = LARVA_STYLE[sp.shape]
    yellow = rgb("#F2D03A")
    seed = sum(map(ord, sp.id))
    if style == "banded":
        p = {"base": "#F4F2EA", "band": "#141414", "band2": mix(bright, yellow, 0.6), "head": "#141414",
             "spine": "#141414", "pod": "#4FC072", "pod_mark": "#E8C23A", "egg": "#F4EED0"}
    elif style == "swallow":
        green = mix("#6CC04A", bright, 0.15)
        p = {"base": green, "band": shade(green, 0.55), "band2": mix(bright, yellow, 0.4), "head": shade(green, 0.8),
             "spine": "#F28A2A", "pod": mix("#9AC86A", "#A88A5A", 0.5 * (seed % 2)),
             "pod_mark": "#E8E0A0", "egg": "#E8E890"}
    elif style == "tubercle":
        p = {"base": mix(dark, "#5A1A2A", 0.6), "band": "#F2F0E6", "band2": mix(dark, "#3A0E18", 0.5),
             "head": "#1A0A0A", "spine": mix(bright, "#E0302A", 0.6), "pod": "#C88A4A", "pod_mark": "#5A3418",
             "egg": "#F2C870"}
    elif style == "spiny":
        base = mix(dark, bright, 0.25)
        p = {"base": base, "band": mix(bright, "#F2F0E6", 0.3), "band2": shade(base, 0.7),
             "head": shade(dark, 0.8), "spine": mix(bright, "#F2F0E6", 0.2), "pod": mix("#8A7A6A", bright, 0.25),
             "pod_mark": "#E8D8A0", "egg": mix(light, "#C8E0A0", 0.5)}
    elif style == "slug":
        green = mix("#8AC85A", bright, 0.3)
        p = {"base": green, "band": shade(green, 0.7), "band2": mix(green, "#F2F0E6", 0.4), "head": "#2A2A1A",
             "spine": green, "pod": "#A08A6A", "pod_mark": "#5A4A3A", "egg": mix(light, "#F2F2F2", 0.6)}
    else:  # skipper
        base = mix("#A8D06A", light, 0.2)
        p = {"base": base, "band": shade(base, 0.8), "band2": mix(base, "#F2F0E6", 0.4), "head": shade(dark, 0.8),
             "spine": base, "pod": "#B8A888", "pod_mark": "#6A5A48", "egg": "#F2E8C0"}
    if sp.category == "Wonders of the World":
        p.update({"base": mix(bright, dark, 0.35), "band": shade(dark, 0.8), "band2": bright, "spine": bright,
                  "pod": mix(bright, dark, 0.45), "pod_mark": mix(bright, "#FFFFFF", 0.35),
                  "egg": mix(bright, "#FFFFFF", 0.4)})
    return style, {k: rgb(v) for k, v in p.items()}


def larva_texture(sp, wing):
    style, p = larva_palette(sp, wing)
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    px = img.load()
    r = random.Random(sp.id + "larva")

    def g(c, amt=0.1):
        return vivid(shade(c, 1 + (r.random() - 0.5) * amt), 1.1, 1.0)

    def segment(thorax):
        def f(face, a, b, fw, fh):
            z = b if face in ("up", "down") else a
            if face in ("north", "south"):
                return g(p["base"])
            if face == "down":
                return g(shade(p["base"], 0.75))
            side = face in ("east", "west")
            if style == "banded":
                return g([p["band"], p["base"], p["band2"]][z % 3])
            if style == "swallow":
                if thorax and face == "up" and z == 1:
                    return (20, 20, 20) if a in (1, 2) else g(p["band2"])
                if z == 1 and face == "up":
                    return g(p["band"]) if a in (0, 3) else g(p["base"])
                if side and b == fh - 1:
                    return g(mix(p["base"], "#F2F0E6", 0.45))
                return g(p["band2"]) if (side and b == 1 and z == 1) else g(p["base"])
            if style == "tubercle":
                return g(p["band"]) if (not thorax and z == 1 and face == "up") else g(p["base"])
            if style == "spiny":
                if side and b == 2:
                    return g(p["band"])
                return g(p["band2"]) if z == 1 else g(p["base"])
            if style == "slug":
                if face == "up" and a in (1, 2):
                    return g(p["band"])
                return g(p["band2"]) if side and b == fh - 1 else g(p["base"])
            return g(p["band"]) if (face == "up" and a in (1, 2)) else g(p["base"])
        return f

    def head(face, a, b, fw, fh):
        if face == "north":
            if b == 1 and a in (0, 2):
                return (250, 250, 240)
            if style == "banded" and b % 2 == 0:
                return g(p["base"])
        if style == "banded":
            return g(p["band"] if (a + b) % 2 else p["band2"])
        return g(p["head"])

    put_box(px, (0, 0), (3, 3, 2), head)
    put_box(px, (16, 0), (4, 4, 3), segment(True))
    put_box(px, (32, 0), (4, 4, 3), segment(False))
    put_box(px, (48, 0), (3, 3, 3), segment(False))
    for x in range(0, 8):
        for y in range(8, 16):
            px[x, y] = (*g(p["spine"]), 255)
    # Twig the chrysalis hangs from.
    for x in range(16, 32):
        for y in range(8, 24):
            px[x, y] = (*g(rgb("#6B4A2B"), 0.25), 255)
    pod, mark = p["pod"], p["pod_mark"]

    def chrysalis(face, a, b, fw, fh):
        if face in ("up", "down"):
            return g(pod)
        if style == "banded":
            if b == 1:
                return (20, 20, 20) if a % 2 else g(mark)
            if b == 2 and a % 3 == 1:
                return g(mark)
            return g(mix(pod, "#FFFFFF", 0.25)) if a % 5 == 2 else g(pod)
        if style == "spiny":
            if (a + b) % 4 == 0:
                return g(mark)
            return g(shade(pod, 0.8)) if (a * 7 + b * 3) % 5 == 0 else g(pod)
        if style in ("swallow", "tubercle"):
            return g(mark) if a % 5 == 2 else g(pod)
        return g(mark) if r.random() < 0.18 else g(pod)

    put_box(px, (0, 24), (5, 6, 5), chrysalis)
    put_box(px, (20, 24), (3, 1.5, 3), lambda *a: g(shade(pod, 0.9)))
    put_box(px, (32, 24), (2, 1.5, 2), lambda *a: g(shade(pod, 0.75)))
    put_box(px, (40, 24), (1, 2, 1), lambda *a: (236, 232, 220))
    # Leaf with an egg cluster: leaf [8,0.5,8] at (0,40), eggs at (34,40).
    leaf_c = rgb("#5DAA3C")
    for a in range(8):
        for b in range(8):
            if abs(a - 3.5) / 4 + abs(b - 3.5) / 4.2 <= 1.05:
                c = g(rgb("#4A8A30")) if a in (3, 4) else g(leaf_c)
                px[8 + a, 40 + b] = (*c, 255)
                px[16 + a, 40 + b] = (*shade(c, 0.8), 255)
    # Leaf edges stay transparent so only the leaf outline shows.
    for x in range(34, 42):
        for y in range(40, 44):
            px[x, y] = (*g(shade(p["egg"], 0.85 if y == 43 else 1.0), 0.05), 255)
    for x, y in ((36, 40), (37, 41), (38, 42)):
        px[x, y] = (*mix(p["egg"], "#FFFFFF", 0.6), 255)
    return img, style, p


# ---------------------------------------------------------------------------
# Item and block art
# ---------------------------------------------------------------------------
GLASS = (196, 226, 236, 255)
GLASS_DK = (122, 160, 176, 255)
GLASS_HI = (240, 252, 255, 255)
LID = (139, 98, 56, 255)
LID_DK = (98, 66, 38, 255)


def jar_base():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for x in range(5, 11):
        px[x, 1] = LID_DK
        px[x, 2] = LID
    px[5, 2] = LID_DK
    px[10, 2] = LID_DK
    px[5, 3] = GLASS_DK
    px[10, 3] = GLASS_DK
    for x in (4, 11):
        px[x, 4] = GLASS_DK
    for y in range(5, 14):
        px[3, y] = GLASS_DK
        px[12, y] = GLASS
    for x in range(4, 12):
        px[x, 14] = GLASS_DK
    px[4, 13] = GLASS
    px[11, 13] = GLASS_DK
    for y in range(6, 10):
        px[4, y] = GLASS_HI
    px[5, 5] = GLASS_HI
    for x in range(4, 12):
        for y in range(5, 14):
            if px[x, y][3] == 0:
                px[x, y] = (210, 236, 244, 70)
    for x in range(6, 10):
        px[x, 4] = (210, 236, 244, 70)
    return img


def jar_icon(sp, wing):
    img = jar_base()
    px = img.load()
    cols = dominant_colors(wing, 4)
    bright = [c for c in cols if sum(c) > 150] or cols
    a = bright[0]
    b = next((c for c in cols if c != a), shade(a, 0.6))
    body, _ = body_colors(sp, wing)
    sprite = ["XX...XX", "XPXbXPX", "XXXbXXX", ".QQbQQ.", ".QQ.QQ."]
    hind = [wing.px[p][:3] for p in wing.hind if wing.px[p][3] and wing.dist[p] >= 1]
    q = max(set(hind), key=hind.count) if hind else a
    cmap = {"X": a, "P": b, "Q": mix(q, a, 0.3) if q != a else shade(a, 0.85), "b": body}
    for y, row in enumerate(sprite):
        for x, ch in enumerate(row):
            if ch in cmap:
                px[5 + x, 7 + y] = (*cmap[ch], 255)
    return img


def nectar_icon():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([7, 1, 8, 2], fill=LID)
    d.rectangle([7, 3, 8, 5], fill=GLASS_DK)
    d.ellipse([3, 5, 12, 14], fill=GLASS_DK)
    d.ellipse([4, 6, 11, 13], fill=(242, 179, 58, 255))
    d.rectangle([4, 7, 11, 8], fill=(248, 210, 120, 255))
    px = img.load()
    px[5, 9] = GLASS_HI
    px[5, 10] = GLASS_HI
    px[9, 11] = (214, 140, 30, 255)
    px[10, 10] = (214, 140, 30, 255)
    return img


def handbook_icon():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    cover, cover_dk, page = rgb("#2E8A6A"), rgb("#1E5A46"), rgb("#F2EAD0")
    for x in range(2, 14):
        for y in range(1, 15):
            px[x, y] = (*cover, 255)
    for y in range(1, 15):
        px[2, y] = (*cover_dk, 255)
        px[3, y] = (*cover_dk, 255)
        px[13, y] = (*page, 255)
    for x in range(3, 14):
        px[x, 14] = (*page, 255)
        px[x, 1] = (*shade(cover, 1.15), 255)
    gold, orange = rgb("#F2C23A"), rgb("#F07A1E")
    for y, row in enumerate(["O.O.O", "OOOOO", ".OgO.", "OO.OO"]):
        for x, ch in enumerate(row):
            if ch != ".":
                px[6 + x, 5 + y] = (*(gold if ch == "g" else orange), 255)
    for x in range(5, 12):
        px[x, 11] = (*gold, 255)
    return img


def unknown_icon():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    shape = ["..XXX......XXX..", ".XXXXX....XXXXX.", ".XXXXXX..XXXXXX.", ".XXXXXXXXXXXXXX.",
             "..XXXXXXXXXXXX..", "...XXXXXXXXXX...", "....XXXXXXXX....", "...XXXXXXXXXX...",
             "..XXXXX..XXXXX..", "..XXXX....XXXX..", "...XX......XX..."]
    for y, row in enumerate(shape):
        for x, ch in enumerate(row):
            if ch == "X":
                px[x, y + 3] = (70, 74, 82, 255)
    for x, y in ((7, 4), (8, 4), (9, 5), (8, 6), (8, 8)):
        px[x, y] = (210, 214, 222, 255)
    return img


def plant_texture(kind):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    r = random.Random(kind)

    def put(x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            px[x, y] = (*rgb(c), 255)

    if kind == "butterfly_bush":
        for sx, top in ((3, 3), (8, 1), (12, 4)):
            for y in range(top + 5, 16):
                put(sx, y, "#4E7A3A")
            for i in range(6):
                y = top + i
                half = 0 if i == 0 else 1
                for x in range(sx - half, sx + half + 1):
                    put(x, y, r.choice(["#9A4FE0", "#C07AF0", "#7A2FC0", "#B060F0"]))
                if r.random() < 0.5:
                    put(sx + r.choice([-1, 1]), y, "#F8A83A")
        for lx, ly, d in ((2, 11, -1), (9, 12, 1), (6, 13, -1), (13, 10, 1), (10, 8, -1)):
            for i in range(3):
                put(lx + d * i, ly - i // 2, "#6E9A52" if i else "#5E8A4A")
    elif kind == "milkweed":
        for y in range(5, 16):
            put(7, y, "#5A8A3A")
            put(8, y, "#4A7A2E")
        for ly, d in ((8, -1), (10, 1), (12, -1), (13, 1)):
            for i in range(1, 5):
                x = 7 + d * i if d < 0 else 8 + d * i
                put(x, ly - (i // 3), "#6AA048")
                put(x, ly + 1 - (i // 3), "#5A8A3A")
        for cx, cy in ((5, 3), (10, 4), (8, 1)):
            for dx in range(-2, 3):
                for dy in range(-1, 2):
                    if abs(dx) + abs(dy) <= 2:
                        put(cx + dx, cy + dy, r.choice(["#F07AA8", "#FFA6C8", "#D85A90"]))
    elif kind == "coneflower":
        for sx, top in ((4, 4), (11, 2), (8, 7)):
            for y in range(top + 2, 16):
                put(sx, y, "#4E7A3A")
            put(sx, top, "#8A4A1A")
            put(sx, top + 1, "#D8682A")
            put(sx - 1, top, "#A0521E")
            put(sx + 1, top, "#A0521E")
            for dx, dy in ((-2, 1), (2, 1), (-2, 2), (2, 2), (-1, 2), (1, 2), (-3, 2), (3, 2)):
                put(sx + dx, top + dy, r.choice(["#E85AB8", "#F07AC8", "#D04AA8"]))
        for lx, ly in ((3, 12), (12, 11), (6, 14)):
            put(lx, ly, "#6A9A4A")
            put(lx + 1, ly - 1, "#6A9A4A")
    return img


def pack_icon(featured):
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(128):
        c = mix(rgb("#7FC8F2"), rgb("#FFF2C8"), y / 127)
        d.line([(0, y), (127, y)], fill=(*c, 255))
    for x in range(128):
        h = 104 + int(3 * math.sin(x / 7))
        d.line([(x, h), (x, 127)], fill=(*rgb("#5DBA3C"), 255))
        d.line([(x, h + 8), (x, 127)], fill=(*rgb("#4A9A30"), 255))
    view = top_view(featured[0][1], featured[0][0], 3)
    img.alpha_composite(view, ((128 - view.width) // 2, 6))
    for (sp, wing), x in zip(featured[1:3], (4, 89)):
        img.alpha_composite(top_view(wing, sp, 1), (x, 92))
    return img


# ---------------------------------------------------------------------------
# Models & animations
# ---------------------------------------------------------------------------

def geo(identifier, bones, tw=64, th=64, vb=(2, 1.5, 0.5)):
    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {"identifier": identifier, "texture_width": tw, "texture_height": th,
                            "visible_bounds_width": vb[0], "visible_bounds_height": vb[1],
                            "visible_bounds_offset": [0, vb[2], 0]},
            "bones": bones,
        }],
    }


def cube(o, s, uv):
    return {"origin": list(o), "size": list(s), "uv": list(uv)}


ANT, CLUB = (56, 44), (56, 52)
BUTTERFLY_GEO = geo("geometry.butterflies.butterfly", [
    {"name": "root", "pivot": [0, 0, 0]},
    {"name": "body", "parent": "root", "pivot": [0, 2.5, -5], "cubes": [
        cube((-1, 1.5, -10), (2, 2, 2), (0, 44)),
        cube((-1.5, 1, -8), (3, 3, 6), (10, 44)),
        cube((-1, 1.5, -2), (2, 2, 10), (30, 44)),
    ]},
    {"name": "antennae", "parent": "body", "pivot": [0, 3.5, -10], "cubes": [
        cube((-1.0, 3.2, -12.5), (0.5, 0.5, 2.5), ANT), cube((-1.4, 3.8, -15), (0.5, 0.5, 2.5), ANT),
        cube((-1.9, 4.4, -16.5), (1, 1, 1.5), CLUB),
        cube((0.5, 3.2, -12.5), (0.5, 0.5, 2.5), ANT), cube((0.9, 3.8, -15), (0.5, 0.5, 2.5), ANT),
        cube((0.9, 4.4, -16.5), (1, 1, 1.5), CLUB),
    ]},
    {"name": "wing_left", "parent": "body", "pivot": [-1.5, 3.5, -5],
     "cubes": [cube((-17.5, 3.5, -10), (16, 0, 22), (0, 0))]},
    {"name": "wing_right", "parent": "body", "pivot": [1.5, 3.5, -5],
     "cubes": [cube((1.5, 3.5, -10), (16, 0, 22), (0, 22))]},
], vb=(3, 2, 0.5))


def caterpillar_geo(kind):
    segs = [("seg0", -9, (16, 0)), ("seg1", -6, (32, 0)), ("seg2", -3, (32, 0)), ("seg3", 0, (32, 0)),
            ("seg4", 3, (32, 0))]
    spine = (0, 8)
    bones = [{"name": "root", "pivot": [0, 0, 0]},
             {"name": "head", "parent": "root", "pivot": [0, 1.5, -9],
              "cubes": [cube((-1.5, 0, -11), (3, 3, 2), (0, 0))]}]
    for name, z, uv in segs:
        cubes = [cube((-2, 0, z), (4, 4, 3), uv)]
        if kind == "spiky":
            cubes += [cube((-1.6, 4, z + 1.2), (0.5, 2.5, 0.5), spine), cube((1.1, 4, z + 1.2), (0.5, 2.5, 0.5), spine),
                      cube((-3.8, 2.6, z + 1.2), (1.8, 0.5, 0.5), spine), cube((2, 2.6, z + 1.2), (1.8, 0.5, 0.5), spine)]
        elif kind == "tubercle":
            cubes += [cube((-1.8, 4, z + 1), (1, 1.5, 1), spine), cube((0.8, 4, z + 1), (1, 1.5, 1), spine),
                      cube((-2.8, 1.2, z + 1), (1, 1, 1), spine), cube((1.8, 1.2, z + 1), (1, 1, 1), spine)]
        bones.append({"name": name, "parent": "root", "pivot": [0, 0, z + 1.5], "cubes": cubes})
    tail = [cube((-1.5, 0, 6), (3, 3, 3), (48, 0))]
    if kind == "spiky":
        tail.append(cube((-0.25, 3, 7.2), (0.5, 2, 0.5), spine))
    bones.append({"name": "tail", "parent": "root", "pivot": [0, 0, 7.5], "cubes": tail})
    if kind == "filament":
        bones[1]["cubes"] += [cube((-1.4, 2.6, -13), (0.5, 0.5, 2), spine), cube((-1.7, 3.1, -14.5), (0.5, 0.5, 1.5), spine),
                              cube((0.9, 2.6, -13), (0.5, 0.5, 2), spine), cube((1.2, 3.1, -14.5), (0.5, 0.5, 1.5), spine)]
        bones[-1]["cubes"] += [cube((-1.2, 2.6, 9), (0.5, 0.5, 2), spine), cube((0.7, 2.6, 9), (0.5, 0.5, 2), spine)]
    return geo(f"geometry.butterflies.caterpillar_{kind}", bones, vb=(2, 1.2, 0.3))


CHRYSALIS_GEO = geo("geometry.butterflies.chrysalis", [
    {"name": "root", "pivot": [0, 0, 0]},
    {"name": "twig", "parent": "root", "pivot": [4, 0, 0], "cubes": [
        cube((3.5, 0, -0.5), (1, 12, 1), (16, 8)), cube((-0.5, 11, -0.5), (5, 1, 1), (20, 8))]},
    {"name": "pod", "parent": "root", "pivot": [0, 11, 0], "cubes": [
        cube((-0.5, 9, -0.5), (1, 2, 1), (40, 24)),
        cube((-1.5, 7.5, -1.5), (3, 1.5, 3), (20, 24)),
        cube((-2.5, 1.5, -2.5), (5, 6, 5), (0, 24)),
        cube((-1, 0, -1), (2, 1.5, 2), (32, 24))]},
], vb=(1.5, 1.5, 0.5))

EGG_GEO = geo("geometry.butterflies.egg_cluster", [
    {"name": "root", "pivot": [0, 0, 0], "cubes": [cube((-4, 0, -4), (8, 0.5, 8), (0, 40))] + [
        cube((x - 0.75, 0.5, z - 0.75), (1.5, 2, 1.5), (34, 40))
        for x, z in ((-1.4, -1.2), (0.4, -1.8), (1.8, -0.4), (-0.4, 0.4), (1.2, 1.4), (-1.8, 1.4))]},
], vb=(1, 0.5, 0))

FLAP = ("(q.is_on_ground ? math.sin(q.life_time * 90) * 15 : "
        "math.sin(q.life_time * 1500 * v.flap) * (math.sin(q.life_time * 37) > 0.8 ? 12 : 55))")
CRAWL = "math.max(0, math.sin(q.life_time * 320 - {}))  * math.clamp(q.modified_move_speed * 8, 0.15, 1.0) * 1.2"
ANIMATIONS = {
    "format_version": "1.8.0",
    "animations": {
        "animation.butterflies.butterfly.fly": {
            "loop": True,
            "bones": {
                "wing_left": {"rotation": [0, 0, FLAP]},
                "wing_right": {"rotation": [0, 0, "-" + FLAP]},
                "root": {"position": [0, "q.is_on_ground ? 0 : math.sin(q.life_time * 400 * v.flap) * 0.8", 0]},
                "antennae": {"rotation": ["math.sin(q.life_time * 150) * 4", 0, 0]},
            },
        },
        "animation.butterflies.caterpillar.crawl": {
            "loop": True,
            "bones": {
                **{b: {"position": [0, CRAWL.format(i * 55), 0]}
                   for i, b in enumerate(["seg0", "seg1", "seg2", "seg3", "seg4", "tail"], 1)},
                "head": {"position": [0, CRAWL.format(0), 0],
                         "rotation": ["math.sin(q.life_time * 160) * 6", "math.sin(q.life_time * 70) * 10", 0]},
            },
        },
        "animation.butterflies.chrysalis.sway": {
            "loop": True,
            "bones": {"pod": {"rotation": [
                "math.sin(q.life_time * 33) * 2", 0,
                "math.sin(q.life_time * 45) * 4 + (math.sin(q.life_time * 7) > 0.97 ? math.sin(q.life_time * 900) * 6 : 0)"]}},
        },
    },
}

RENDER_CONTROLLER = {
    "format_version": "1.8.0",
    "render_controllers": {
        "controller.render.butterflies.default": {
            "geometry": "Geometry.default",
            "materials": [{"*": "Material.default"}],
            "textures": ["Texture.default"],
        }
    },
}

CROSS_GEO = {
    "format_version": "1.12.0",
    "minecraft:geometry": [{
        "description": {"identifier": "geometry.butterflies.cross", "texture_width": 16, "texture_height": 16},
        "bones": [{"name": "plant", "pivot": [0, 0, 0], "cubes": [
            {"origin": [-8, 0, 0], "size": [16, 16, 0], "pivot": [0, 0, 0], "rotation": [0, 45, 0],
             "uv": {"north": {"uv": [0, 0], "uv_size": [16, 16]}}},
            {"origin": [-8, 0, 0], "size": [16, 16, 0], "pivot": [0, 0, 0], "rotation": [0, -45, 0],
             "uv": {"north": {"uv": [0, 0], "uv_size": [16, 16]}}},
        ]}],
    }],
}

# ---------------------------------------------------------------------------
# Behaviour
# ---------------------------------------------------------------------------
FLOWER_BLOCKS = ["butterfly_bush", "milkweed", "coneflower"]
VANILLA_FLOWERS = [
    "minecraft:poppy", "minecraft:dandelion", "minecraft:blue_orchid", "minecraft:allium", "minecraft:azure_bluet",
    "minecraft:red_tulip", "minecraft:orange_tulip", "minecraft:white_tulip", "minecraft:pink_tulip",
    "minecraft:oxeye_daisy", "minecraft:cornflower", "minecraft:lily_of_the_valley", "minecraft:sunflower",
    "minecraft:lilac", "minecraft:rose_bush", "minecraft:peony", "minecraft:pink_petals", "minecraft:torchflower",
    "minecraft:flowering_azalea",
]
LEAVES = ["minecraft:oak_leaves", "minecraft:birch_leaves", "minecraft:jungle_leaves", "minecraft:spruce_leaves",
          "minecraft:acacia_leaves", "minecraft:dark_oak_leaves", "minecraft:mangrove_leaves",
          "minecraft:cherry_leaves", "minecraft:azalea_leaves"]
SEEDS = ["minecraft:wheat_seeds", "minecraft:melon_seeds", "minecraft:pumpkin_seeds", "minecraft:beetroot_seeds",
         "minecraft:torchflower_seeds", "minecraft:pitcher_pod"]
CATERPILLAR_FOOD = LEAVES + [f"{NS}:{b}" for b in FLOWER_BLOCKS] + ["minecraft:short_grass", "minecraft:fern"]
NETHER_FOOD = ["minecraft:nether_wart", "minecraft:crimson_fungus", "minecraft:warped_fungus",
               "minecraft:crimson_roots", "minecraft:warped_roots", "minecraft:weeping_vines",
               "minecraft:twisting_vines"]
END_FOOD = ["minecraft:chorus_fruit", "minecraft:popped_chorus_fruit", "minecraft:chorus_flower"]
# Seeds are the best food: each one is worth far more growth than a leaf.
SEED_GROWTH, FOOD_GROWTH = 0.08, 0.03
GROW_SECONDS = 2400


def realm(sp):
    if "the_end" in sp.habitat:
        return "end"
    return "nether" if any(h in NETHER for h in sp.habitat) else "overworld"


def larva_food(sp):
    return {"overworld": CATERPILLAR_FOOD, "nether": NETHER_FOOD, "end": END_FOOD}[realm(sp)]
SOIL = ["minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt", "minecraft:podzol",
        "minecraft:rooted_dirt", "minecraft:moss_block", "minecraft:mycelium", "minecraft:farmland"]


def player_holding(item_id):
    return {"all_of": [
        {"test": "is_family", "subject": "other", "value": "player"},
        {"test": "has_equipment", "domain": "hand", "subject": "other", "value": item_id},
    ]}


def base_components(sp, family, health):
    comps = {
        "minecraft:type_family": {"family": family + ["butterfly_lifecycle", "arthropod", "mob"]},
        "minecraft:health": {"value": health, "max": health},
        "minecraft:breathable": {"total_supply": 15, "suffocate_time": 0},
        "minecraft:damage_sensor": {"triggers": [{"cause": "fall", "deals_damage": "no"}]},
        "minecraft:nameable": {},
        "minecraft:physics": {},
        "minecraft:conditional_bandwidth_optimization": {},
    }
    if any(h in NETHER for h in sp.habitat):
        comps["minecraft:fire_immune"] = {}
    return comps


def adult_behavior(sp):
    comps = base_components(sp, ["butterfly"], 3)
    comps.update({
        "minecraft:collision_box": {"width": 0.9, "height": 0.6},
        "minecraft:scale": {"value": sp.scale},
        "minecraft:pushable": {"is_pushable": True, "is_pushable_by_piston": True},
        "minecraft:despawn": {"despawn_from_distance": {}},
        "minecraft:can_fly": {},
        "minecraft:movement": {"value": 0.25},
        "minecraft:flying_speed": {"value": round(0.09 + 0.03 * sp.flap, 3)},
        "minecraft:movement.hover": {},
        "minecraft:jump.static": {},
        "minecraft:navigation.hover": {
            "can_path_over_water": True, "can_sink": False, "can_pass_doors": False,
            "can_path_from_air": True, "avoid_water": True, "avoid_damage_blocks": True, "avoid_sun": False,
        },
        "minecraft:game_event_movement_tracking": {"emit_flap": True},
        "minecraft:behavior.panic": {"priority": 1, "speed_multiplier": 1.6},
        "minecraft:behavior.tempt": {
            "priority": 4, "speed_multiplier": 1.2, "within_radius": 10, "can_tempt_vertically": True,
            "items": [f"{NS}:nectar_bottle"],
        },
        "minecraft:behavior.move_to_block": {
            "priority": 8, "tick_interval": 20, "start_chance": 0.4, "search_range": 10, "search_height": 4,
            "goal_radius": 1.2, "stay_duration": 60,
            "target_blocks": VANILLA_FLOWERS + [f"{NS}:{b}" for b in FLOWER_BLOCKS] + [
                "minecraft:crimson_fungus", "minecraft:warped_fungus", "minecraft:crimson_roots",
                "minecraft:warped_roots", "minecraft:shroomlight", "minecraft:chorus_flower"],
        },
        "minecraft:behavior.random_hover": {
            "priority": 12, "xz_dist": 8, "y_dist": 6, "y_offset": -1, "interval": 1, "hover_height": [1, 4],
        },
        "minecraft:interact": {"interactions": [
            {
                "on_interact": {"filters": player_holding(f"{NS}:butterfly_jar"), "event": f"{NS}:caught", "target": "self"},
                "use_item": True, "transform_to_item": f"{NS}:jar_{sp.id}", "swing": True,
                "interact_text": "action.interact.butterflies.catch",
            },
            {
                "on_interact": {"filters": player_holding(f"{NS}:nectar_bottle"), "event": f"{NS}:lay_egg", "target": "self"},
                "use_item": True, "transform_to_item": "minecraft:glass_bottle", "swing": True, "cooldown": 30,
                "interact_text": "action.interact.butterflies.feed",
            },
        ]},
    })
    return {
        "format_version": "1.21.0",
        "minecraft:entity": {
            "description": {"identifier": f"{NS}:{sp.id}", "is_spawnable": True, "is_summonable": True},
            "component_groups": {
                f"{NS}:caught": {"minecraft:instant_despawn": {}},
                f"{NS}:laying": {
                    "minecraft:spawn_entity": {"entities": [{
                        "min_wait_time": 1, "max_wait_time": 3, "spawn_entity": f"{NS}:{sp.id}_egg",
                        "single_use": True, "num_to_spawn": 1, "spawn_sound": "plop"}]},
                    "minecraft:timer": {"time": 5, "looping": False,
                                        "time_down_event": {"event": f"{NS}:laid", "target": "self"}},
                },
            },
            "components": comps,
            "events": {
                f"{NS}:caught": {"add": {"component_groups": [f"{NS}:caught"]}},
                f"{NS}:lay_egg": {"add": {"component_groups": [f"{NS}:laying"]}},
                f"{NS}:laid": {"remove": {"component_groups": [f"{NS}:laying"]}},
            },
        },
    }


def stage_entity(identifier, comps, next_id, event, spawnable=False):
    return {
        "format_version": "1.21.0",
        "minecraft:entity": {
            "description": {"identifier": identifier, "is_spawnable": spawnable, "is_summonable": True},
            "component_groups": {f"{NS}:transform": {"minecraft:transformation": {"into": next_id}}},
            "components": comps,
            "events": {event: {"add": {"component_groups": [f"{NS}:transform"]}}},
        },
    }


def larva_scale(sp):
    return round(0.32 + 0.25 * sp.scale, 3)


def egg_behavior(sp):
    comps = base_components(sp, ["butterfly_egg"], 1)
    comps.update({
        "minecraft:collision_box": {"width": 0.4, "height": 0.15},
        "minecraft:scale": {"value": 0.7},
        "minecraft:knockback_resistance": {"value": 1.0},
        "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": True},
        "minecraft:timer": {"time": [240, 360], "looping": False,
                            "time_down_event": {"event": f"{NS}:hatch", "target": "self"}},
    })
    return stage_entity(f"{NS}:{sp.id}_egg", comps, f"{NS}:{sp.id}_caterpillar", f"{NS}:hatch")


def caterpillar_behavior(sp):
    comps = base_components(sp, ["caterpillar"], 4)
    comps.update({
        "minecraft:collision_box": {"width": 0.5, "height": 0.3},
        "minecraft:scale": {"value": larva_scale(sp)},
        "minecraft:pushable": {"is_pushable": True, "is_pushable_by_piston": True},
        "minecraft:movement": {"value": 0.08},
        "minecraft:movement.basic": {},
        "minecraft:jump.static": {},
        "minecraft:navigation.walk": {"avoid_water": True, "avoid_damage_blocks": True, "can_walk": True},
        "minecraft:behavior.float": {"priority": 0},
        "minecraft:behavior.tempt": {"priority": 3, "speed_multiplier": 1.3, "within_radius": 6,
                                     "items": SEEDS + larva_food(sp)},
        "minecraft:behavior.random_stroll": {"priority": 6, "speed_multiplier": 1.0, "xz_dist": 4, "y_dist": 2},
        "minecraft:behavior.look_at_player": {"priority": 8, "look_distance": 4, "probability": 0.05},
        "minecraft:behavior.random_look_around": {"priority": 9},
        "minecraft:ageable": {
            "duration": GROW_SECONDS,
            "feed_items": [{"item": i, "growth": SEED_GROWTH} for i in SEEDS]
                          + [{"item": i, "growth": FOOD_GROWTH} for i in larva_food(sp)],
            "grow_up": {"event": f"{NS}:pupate", "target": "self"},
        },
        # Fallback in case feeding progress is ever lost: pupate on a timer that is longer than growing up.
        "minecraft:timer": {"time": [GROW_SECONDS + 600, GROW_SECONDS + 1200], "looping": False,
                            "time_down_event": {"event": f"{NS}:pupate", "target": "self"}},
    })
    return stage_entity(f"{NS}:{sp.id}_caterpillar", comps, f"{NS}:{sp.id}_chrysalis", f"{NS}:pupate", True)


def chrysalis_behavior(sp):
    comps = base_components(sp, ["chrysalis"], 6)
    comps.update({
        "minecraft:collision_box": {"width": 0.4, "height": 0.6},
        "minecraft:scale": {"value": round(larva_scale(sp) * 1.25, 3)},
        "minecraft:knockback_resistance": {"value": 1.0},
        "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": True},
        "minecraft:timer": {"time": [480, 720], "looping": False,
                            "time_down_event": {"event": f"{NS}:emerge", "target": "self"}},
    })
    return stage_entity(f"{NS}:{sp.id}_chrysalis", comps, f"{NS}:{sp.id}", f"{NS}:emerge")


def spawn_rules(identifier, sp, weight_scale=1.0, herd=None):
    tags = sp.habitat
    biome = {"any_of": [{"test": "has_biome_tag", "operator": "==", "value": t} for t in tags]}
    weight = max(1, round(RARITY[sp.rarity] * weight_scale))
    cond = {"minecraft:weight": {"default": weight},
            "minecraft:herd": {"min_size": 1, "max_size": herd or (2 if sp.rarity in ("common", "uncommon") else 1)},
            "minecraft:biome_filter": biome}
    if any(t in UNDERGROUND for t in tags):
        cond["minecraft:spawns_underground"] = {}
        cond["minecraft:density_limit"] = {"underground": 3}
    elif any(t in NETHER for t in tags):
        cond["minecraft:spawns_on_surface"] = {}
        cond["minecraft:spawns_underground"] = {}
        cond["minecraft:density_limit"] = {"surface": 3, "underground": 3}
    elif "the_end" in tags:
        cond["minecraft:spawns_on_surface"] = {}
        cond["minecraft:density_limit"] = {"surface": 3}
    else:
        cond["minecraft:spawns_on_surface"] = {}
        cond["minecraft:brightness_filter"] = {"min": 10, "max": 15, "adjust_for_weather": True}
        cond["minecraft:density_limit"] = {"surface": 3}
    return {
        "format_version": "1.8.0",
        "minecraft:spawn_rules": {
            "description": {"identifier": identifier, "population_control": "ambient"},
            "conditions": [cond],
        },
    }


def client_entity(identifier, texture, geometry, anim, egg=None, init=None):
    desc = {
        "identifier": identifier,
        "materials": {"default": "entity_alphatest"},
        "textures": {"default": texture},
        "geometry": {"default": geometry},
        "render_controllers": ["controller.render.butterflies.default"],
    }
    if anim:
        desc["animations"] = {"main": anim}
        desc["scripts"] = {"animate": ["main"]}
        if init:
            desc["scripts"]["initialize"] = init
    if egg:
        desc["spawn_egg"] = {"base_color": hexc(egg[0]), "overlay_color": hexc(egg[1])}
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": desc}}


def item(identifier, icon, lang_key, comps=None, category="items"):
    c = {"minecraft:icon": icon, "minecraft:display_name": {"value": lang_key}}
    c.update(comps or {})
    return {
        "format_version": "1.21.40",
        "minecraft:item": {"description": {"identifier": identifier, "menu_category": {"category": category}},
                           "components": c},
    }


def plant_block(name, height):
    return {
        "format_version": "1.21.40",
        "minecraft:block": {
            "description": {"identifier": f"{NS}:{name}", "menu_category": {"category": "nature"}},
            "components": {
                "minecraft:geometry": "geometry.butterflies.cross",
                "minecraft:material_instances": {"*": {
                    "texture": f"{NS}_{name}", "render_method": "alpha_test",
                    "ambient_occlusion": False, "face_dimming": False}},
                "minecraft:collision_box": False,
                "minecraft:selection_box": {"origin": [-5, 0, -5], "size": [10, height, 10]},
                "minecraft:destructible_by_mining": {"seconds_to_destroy": 0},
                "minecraft:destructible_by_explosion": {"explosion_resistance": 0},
                "minecraft:flammable": {"catch_chance_modifier": 60, "destroy_chance_modifier": 100},
                "minecraft:light_dampening": 0,
                "minecraft:map_color": {"butterfly_bush": "#8E4FC8", "milkweed": "#E07AA0", "coneflower": "#D65AA8"}[name],
                "minecraft:placement_filter": {"conditions": [{"allowed_faces": ["up"], "block_filter": SOIL}]},
            },
        },
    }


def recipes():
    out = {"butterfly_jar": {
        "format_version": "1.20.10",
        "minecraft:recipe_shaped": {
            "description": {"identifier": f"{NS}:butterfly_jar"},
            "tags": ["crafting_table"],
            "pattern": [" W ", "G G", "GGG"],
            "key": {"W": {"tag": "minecraft:planks"}, "G": {"item": "minecraft:glass"}},
            "unlock": [{"item": "minecraft:glass"}],
            "result": {"item": f"{NS}:butterfly_jar", "count": 3},
        },
    }}

    def shapeless(name, ingredients, result, count=1, unlock="minecraft:sugar"):
        out[name] = {
            "format_version": "1.20.10",
            "minecraft:recipe_shapeless": {
                "description": {"identifier": f"{NS}:{name}"},
                "tags": ["crafting_table"],
                "ingredients": [{"item": i} for i in ingredients],
                "unlock": [{"item": unlock}],
                "result": {"item": result, "count": count},
            },
        }

    shapeless("handbook", ["minecraft:book", f"{NS}:butterfly_jar"], f"{NS}:handbook", 1, "minecraft:book")
    shapeless("nectar_bottle_from_dandelion", ["minecraft:glass_bottle", "minecraft:sugar", "minecraft:dandelion"],
              f"{NS}:nectar_bottle")
    shapeless("nectar_bottle_from_bush", ["minecraft:glass_bottle", "minecraft:sugar", f"{NS}:butterfly_bush"],
              f"{NS}:nectar_bottle")
    shapeless("nectar_bottle_from_milkweed", ["minecraft:glass_bottle", "minecraft:sugar", f"{NS}:milkweed"],
              f"{NS}:nectar_bottle")
    shapeless("butterfly_bush", ["minecraft:oak_sapling", "minecraft:purple_dye", "minecraft:purple_dye"],
              f"{NS}:butterfly_bush", 1, "minecraft:purple_dye")
    shapeless("milkweed", ["minecraft:wheat_seeds", "minecraft:pink_dye", "minecraft:white_dye"],
              f"{NS}:milkweed", 1, "minecraft:pink_dye")
    shapeless("coneflower", ["minecraft:wheat_seeds", "minecraft:magenta_dye", "minecraft:brown_dye"],
              f"{NS}:coneflower", 1, "minecraft:magenta_dye")
    shapeless("purple_dye_from_bush", [f"{NS}:butterfly_bush"], "minecraft:purple_dye", 2, f"{NS}:butterfly_bush")
    shapeless("pink_dye_from_milkweed", [f"{NS}:milkweed"], "minecraft:pink_dye", 2, f"{NS}:milkweed")
    shapeless("magenta_dye_from_coneflower", [f"{NS}:coneflower"], "minecraft:magenta_dye", 2, f"{NS}:coneflower")
    return out


FLOWER_SPAWNS = {
    "butterfly_bush": (["plains", "meadow", "flower_forest", "cherry_grove"], 6),
    "milkweed": (["plains", "savanna", "meadow"], 6),
    "coneflower": (["flower_forest", "forest", "birch", "plains"], 8),
}


def features():
    out = {}
    for name, (tags, chance) in FLOWER_SPAWNS.items():
        out[f"features/{name}_feature.json"] = {
            "format_version": "1.13.0",
            "minecraft:single_block_feature": {
                "description": {"identifier": f"{NS}:{name}_feature"},
                "places_block": f"{NS}:{name}",
                "enforce_placement_rules": True,
                "enforce_survival_rules": True,
                "may_attach_to": {"bottom": ["minecraft:grass_block", "minecraft:dirt", "minecraft:podzol"]},
            },
        }
        out[f"feature_rules/{name}_rule.json"] = {
            "format_version": "1.13.0",
            "minecraft:feature_rules": {
                "description": {"identifier": f"{NS}:{name}_rule", "places_feature": f"{NS}:{name}_feature"},
                "conditions": {
                    "placement_pass": "surface_pass",
                    "minecraft:biome_filter": [{"any_of": [
                        {"test": "has_biome_tag", "operator": "==", "value": t} for t in tags]}],
                },
                "distribution": {
                    "iterations": 4,
                    "scatter_chance": {"numerator": 1, "denominator": chance},
                    "x": {"distribution": "uniform", "extent": [0, 16]},
                    "y": "q.heightmap(v.worldx, v.worldz)",
                    "z": {"distribution": "uniform", "extent": [0, 16]},
                },
            },
        }
    return out


def manifest(kind):
    is_bp = kind == "bp"
    own, other = ("bp", "rp") if is_bp else ("rp", "bp")
    modules = [{"type": "data" if is_bp else "resources", "uuid": uid(f"{own}-module"), "version": VERSION}]
    deps = [{"uuid": uid(f"{other}-header"), "version": VERSION}]
    if is_bp:
        modules.append({"type": "script", "language": "javascript", "uuid": uid("bp-script"),
                        "version": VERSION, "entry": "scripts/main.js"})
        deps += [{"module_name": "@minecraft/server", "version": "2.0.0"},
                 {"module_name": "@minecraft/server-ui", "version": "2.0.0"}]
    return {
        "format_version": 2,
        "header": {"name": "pack.name", "description": "pack.description", "uuid": uid(f"{own}-header"),
                   "version": VERSION, "min_engine_version": MIN_ENGINE},
        "modules": modules,
        "dependencies": deps,
        "metadata": {"authors": ["Butterflies Galore"]},
    }


def handbook_data(painted):
    rows = []
    for sp, _ in painted:
        rows.append({
            "id": sp.id, "name": sp.name, "category": sp.category, "rarity": sp.rarity.title(),
            "habitat": ", ".join(HABITAT_LABEL[h] for h in sp.habitat),
            "wingspan": f"{35 * sp.scale / 16:.1f} blocks",
            "food": {"overworld": FOOD[LARVA_STYLE[sp.shape]] + ", but seeds work best",
                     "nether": "Nether Wart, crimson and warped fungus and roots, but seeds work best",
                     "end": "Chorus Fruit and Chorus Flowers, but seeds work best"}[realm(sp)],
            "info": INFO[sp.id],
            "icon": f"textures/items/jars/jar_{sp.id}",
        })
    cats = []
    for c in CATEGORIES:
        first = next(sp for sp, _ in painted if sp.category == c)
        cats.append({"name": c, "icon": f"textures/items/jars/jar_{first.id}"})
    return ("// Generated by tools/generate.py from the species table. Do not edit by hand.\n"
            f"export const SPECIES = {json.dumps(rows, indent=1)};\n\n"
            f"export const CATEGORIES = {json.dumps(cats, indent=1)};\n")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build():
    for p in (BP, RP):
        if os.path.isdir(p):
            shutil.rmtree(p)
    painted = [(sp, paint_wing(sp)) for sp in SPECIES]
    by_id = {sp.id: (sp, w) for sp, w in painted}

    write_json(os.path.join(BP, "manifest.json"), manifest("bp"))
    write_json(os.path.join(RP, "manifest.json"), manifest("rp"))
    icon = pack_icon([by_id["monarch"], by_id["blue_morpho"], by_id["peacock"]])
    save_png(icon, os.path.join(BP, "pack_icon.png"))
    save_png(icon, os.path.join(RP, "pack_icon.png"))
    desc = f"{len(SPECIES)} butterflies to discover, raise from egg to wing, catch and record in your handbook."
    for p, label in ((BP, "Behavior Pack"), (RP, "Resource Pack")):
        write_json(os.path.join(p, "texts", "languages.json"), ["en_US"])
        write_text(os.path.join(p, "texts", "en_US.lang"),
                   f"pack.name=Butterflies Galore {label}\npack.description={desc}\n")

    models = os.path.join(RP, "models", "entity")
    write_json(os.path.join(models, "butterfly.geo.json"), BUTTERFLY_GEO)
    for kind in ("smooth", "filament", "spiky", "tubercle"):
        write_json(os.path.join(models, f"caterpillar_{kind}.geo.json"), caterpillar_geo(kind))
    write_json(os.path.join(models, "chrysalis.geo.json"), CHRYSALIS_GEO)
    write_json(os.path.join(models, "egg_cluster.geo.json"), EGG_GEO)
    write_json(os.path.join(RP, "models", "blocks", "cross.geo.json"), CROSS_GEO)
    write_json(os.path.join(RP, "animations", "butterflies.animation.json"), ANIMATIONS)
    write_json(os.path.join(RP, "render_controllers", "butterflies.render_controllers.json"), RENDER_CONTROLLER)

    lang = ["pack.name=Butterflies Galore Resource Pack", f"pack.description={desc}", ""]
    item_tex = {}
    for sp, wing in painted:
        tex = f"textures/entity/butterflies/{sp.id}"
        ltex = f"textures/entity/butterflies/larva/{sp.id}"
        save_png(entity_texture(sp, wing), os.path.join(RP, tex + ".png"))
        limg, style, lp = larva_texture(sp, wing)
        save_png(limg, os.path.join(RP, ltex + ".png"))
        write_json(os.path.join(RP, "entity", f"{sp.id}.entity.json"), client_entity(
            f"{NS}:{sp.id}", tex, "geometry.butterflies.butterfly", "animation.butterflies.butterfly.fly",
            dominant_colors(wing, 2), [f"v.flap = {sp.flap};"]))
        write_json(os.path.join(RP, "entity", "larva", f"{sp.id}_egg.entity.json"), client_entity(
            f"{NS}:{sp.id}_egg", ltex, "geometry.butterflies.egg_cluster", None))
        write_json(os.path.join(RP, "entity", "larva", f"{sp.id}_caterpillar.entity.json"), client_entity(
            f"{NS}:{sp.id}_caterpillar", ltex, f"geometry.butterflies.caterpillar_{LARVA_GEO[style]}",
            "animation.butterflies.caterpillar.crawl", (lp["base"], lp["band2"] if style == "banded" else lp["band"])))
        write_json(os.path.join(RP, "entity", "larva", f"{sp.id}_chrysalis.entity.json"), client_entity(
            f"{NS}:{sp.id}_chrysalis", ltex, "geometry.butterflies.chrysalis", "animation.butterflies.chrysalis.sway"))

        write_json(os.path.join(BP, "entities", f"{sp.id}.json"), adult_behavior(sp))
        write_json(os.path.join(BP, "entities", "larva", f"{sp.id}_egg.json"), egg_behavior(sp))
        write_json(os.path.join(BP, "entities", "larva", f"{sp.id}_caterpillar.json"), caterpillar_behavior(sp))
        write_json(os.path.join(BP, "entities", "larva", f"{sp.id}_chrysalis.json"), chrysalis_behavior(sp))
        write_json(os.path.join(BP, "spawn_rules", f"{sp.id}.json"), spawn_rules(f"{NS}:{sp.id}", sp))
        write_json(os.path.join(BP, "spawn_rules", "larva", f"{sp.id}_caterpillar.json"),
                   spawn_rules(f"{NS}:{sp.id}_caterpillar", sp, 0.5, 1))

        save_png(jar_icon(sp, wing), os.path.join(RP, "textures", "items", "jars", f"jar_{sp.id}.png"))
        item_tex[f"{NS}_jar_{sp.id}"] = {"textures": f"textures/items/jars/jar_{sp.id}"}
        write_json(os.path.join(BP, "items", "jars", f"jar_{sp.id}.json"),
                   item(f"{NS}:jar_{sp.id}", f"{NS}_jar_{sp.id}", f"item.{NS}.jar_{sp.id}.name", {
                       "minecraft:max_stack_size": 16,
                       "minecraft:entity_placer": {"entity": f"{NS}:{sp.id}"},
                   }))
        lang += [f"entity.{NS}:{sp.id}.name={sp.name}",
                 f"entity.{NS}:{sp.id}_egg.name={sp.name} Eggs",
                 f"entity.{NS}:{sp.id}_caterpillar.name={sp.name} Caterpillar",
                 f"entity.{NS}:{sp.id}_chrysalis.name={sp.name} Chrysalis",
                 f"item.spawn_egg.entity.{NS}:{sp.id}.name=Spawn {sp.name}",
                 f"item.spawn_egg.entity.{NS}:{sp.id}_caterpillar.name=Spawn {sp.name} Caterpillar",
                 f"item.{NS}.jar_{sp.id}.name={sp.name} in a Jar"]

    for name, img in (("butterfly_jar", jar_base()), ("nectar_bottle", nectar_icon()), ("handbook", handbook_icon())):
        save_png(img, os.path.join(RP, "textures", "items", f"{name}.png"))
        item_tex[f"{NS}_{name}"] = {"textures": f"textures/items/{name}"}
    save_png(unknown_icon(), os.path.join(RP, "textures", "ui", "butterflies", "unknown.png"))
    write_json(os.path.join(BP, "items", "butterfly_jar.json"),
               item(f"{NS}:butterfly_jar", f"{NS}_butterfly_jar", f"item.{NS}.butterfly_jar.name",
                    {"minecraft:max_stack_size": 64}, "equipment"))
    write_json(os.path.join(BP, "items", "handbook.json"),
               item(f"{NS}:handbook", f"{NS}_handbook", f"item.{NS}.handbook.name", {
                   "minecraft:max_stack_size": 1,
                   "minecraft:cooldown": {"category": f"{NS}_handbook", "duration": 0.5},
               }, "equipment"))
    write_json(os.path.join(BP, "items", "nectar_bottle.json"),
               item(f"{NS}:nectar_bottle", f"{NS}_nectar_bottle", f"item.{NS}.nectar_bottle.name", {
                   "minecraft:max_stack_size": 16,
                   "minecraft:use_animation": "drink",
                   "minecraft:use_modifiers": {"use_duration": 1.6, "movement_modifier": 0.35},
                   "minecraft:food": {"nutrition": 3, "saturation_modifier": 0.6, "can_always_eat": True,
                                      "using_converts_to": "minecraft:glass_bottle"},
               }))
    write_json(os.path.join(RP, "textures", "item_texture.json"),
               {"resource_pack_name": "butterflies_galore", "texture_name": "atlas.items", "texture_data": item_tex})

    terrain = {}
    blocks_json = {"format_version": "1.21.40"}
    for name, height in (("butterfly_bush", 15), ("milkweed", 14), ("coneflower", 12)):
        save_png(plant_texture(name), os.path.join(RP, "textures", "blocks", f"{name}.png"))
        terrain[f"{NS}_{name}"] = {"textures": f"textures/blocks/{name}"}
        write_json(os.path.join(BP, "blocks", f"{name}.json"), plant_block(name, height))
        blocks_json[f"{NS}:{name}"] = {"sound": "grass"}
    write_json(os.path.join(RP, "textures", "terrain_texture.json"),
               {"resource_pack_name": "butterflies_galore", "texture_name": "atlas.terrain", "padding": 8,
                "num_mip_levels": 4, "texture_data": terrain})
    write_json(os.path.join(RP, "blocks.json"), blocks_json)

    lang += ["",
             f"item.{NS}.butterfly_jar.name=Butterfly Jar",
             f"item.{NS}.nectar_bottle.name=Bottle of Nectar",
             f"item.{NS}.handbook.name=Butterfly Handbook",
             f"tile.{NS}:butterfly_bush.name=Butterfly Bush",
             f"tile.{NS}:milkweed.name=Milkweed",
             f"tile.{NS}:coneflower.name=Coneflower",
             "action.interact.butterflies.catch=Catch",
             "action.interact.butterflies.feed=Feed Nectar", ""]
    write_text(os.path.join(RP, "texts", "en_US.lang"), "\n".join(lang))

    for name, data in recipes().items():
        write_json(os.path.join(BP, "recipes", f"{name}.json"), data)
    for rel, data in features().items():
        write_json(os.path.join(BP, rel), data)
    write_text(os.path.join(BP, "scripts", "species.js"), handbook_data(painted))
    shutil.copy(os.path.join(ROOT, "tools", "handbook.js"), os.path.join(BP, "scripts", "main.js"))

    build_preview(painted)
    build_lifecycle(by_id)
    build_field_guide(painted)
    build_mcaddon()


# ---------------------------------------------------------------------------
# Docs: previews rendered straight from the pack's models and textures
# ---------------------------------------------------------------------------

def box_texel_quads(cube_def, tex):
    """Yield (corners, colour, face) for every opaque texel of a box-UV cube."""
    (x0, y0, z0), (w, h, d), (U, V) = cube_def["origin"], cube_def["size"], cube_def["uv"]
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    tw, th, td = (max(1, math.ceil(s - 1e-6)) if s > 0 else 0 for s in (w, h, d))
    px = tex.load()

    def col(x, y):
        if 0 <= x < tex.width and 0 <= y < tex.height:
            c = px[x, y]
            return c if c[3] else None
        return None

    def lerp(a, b, t):
        return a + (b - a) * t

    faces = []
    if tw and td:
        for i in range(tw):
            for j in range(td):
                xa, xb = lerp(x0, x1, i / tw), lerp(x0, x1, (i + 1) / tw)
                za, zb = lerp(z1, z0, j / td), lerp(z1, z0, (j + 1) / td)
                faces.append(("up", col(U + td + i, V + j), [(xa, y1, za), (xb, y1, za), (xb, y1, zb), (xa, y1, zb)]))
                if th:
                    faces.append(("down", col(U + td + tw + i, V + j),
                                  [(xa, y0, za), (xb, y0, za), (xb, y0, zb), (xa, y0, zb)]))
    if th:
        for j in range(th):
            ya, yb = lerp(y1, y0, j / th), lerp(y1, y0, (j + 1) / th)
            for i in range(td):
                za, zb = lerp(z1, z0, i / td), lerp(z1, z0, (i + 1) / td)
                faces.append(("side", col(U + i, V + td + j), [(x0, ya, za), (x0, ya, zb), (x0, yb, zb), (x0, yb, za)]))
                za, zb = lerp(z0, z1, i / td), lerp(z0, z1, (i + 1) / td)
                faces.append(("side", col(U + td + tw + i, V + td + j),
                              [(x1, ya, za), (x1, ya, zb), (x1, yb, zb), (x1, yb, za)]))
            for i in range(tw):
                xa, xb = lerp(x0, x1, i / tw), lerp(x0, x1, (i + 1) / tw)
                faces.append(("end", col(U + td + i, V + td + j), [(xa, ya, z0), (xb, ya, z0), (xb, yb, z0), (xa, yb, z0)]))
                xa, xb = lerp(x1, x0, i / tw), lerp(x1, x0, (i + 1) / tw)
                faces.append(("end", col(U + 2 * td + tw + i, V + td + j),
                              [(xa, ya, z1), (xb, ya, z1), (xb, yb, z1), (xa, yb, z1)]))
    for face, c, pts in faces:
        if c is not None:
            yield pts, c, face


def render_model(geometry, tex, pose=None, yaw=200, pitch=30, size=240):
    pose = pose or {}
    bones = {b["name"]: b for b in geometry["minecraft:geometry"][0]["bones"]}

    def transform(name, p):
        b = bones[name]
        rz = math.radians(pose.get(name, 0))
        if rz:
            px_, py_ = b["pivot"][0], b["pivot"][1]
            dx, dy = p[0] - px_, p[1] - py_
            p = (px_ + dx * math.cos(rz) - dy * math.sin(rz), py_ + dx * math.sin(rz) + dy * math.cos(rz), p[2])
        return transform(b["parent"], p) if b.get("parent") else p

    polys = []
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, spp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    light = {"up": 1.0, "down": 0.55, "side": 0.78, "end": 0.88}
    for name, b in bones.items():
        for c in b.get("cubes", []):
            for pts, col, face in box_texel_quads(c, tex):
                out = []
                for p in pts:
                    x, y, z = transform(name, p)
                    x, z = x * cy - z * sy, x * sy + z * cy
                    y, z = y * cp + z * spp, -y * spp + z * cp
                    out.append((x, y, z))
                polys.append((sum(q[2] for q in out) / 4, out, shade(col[:3], light[face])))
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    if not polys:
        return img
    xs = [q[0] for _, o, _ in polys for q in o]
    ys = [q[1] for _, o, _ in polys for q in o]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    zoom = size * 0.82 / span
    ox, oy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    d = ImageDraw.Draw(img)
    for _, o, c in sorted(polys, key=lambda q: -q[0]):
        pts = [(size / 2 + (q[0] - ox) * zoom, size / 2 - (q[1] - oy) * zoom) for q in o]
        d.polygon(pts, fill=(*c, 255), outline=(*c, 255))
    return img


def build_preview(painted):
    cols, cell_w, cell_h = 20, 96, 92
    head = 22
    rows = sum((sum(1 for sp, _ in painted if sp.category == c) + cols - 1) // cols for c in CATEGORIES)
    img = Image.new("RGBA", (cols * cell_w, rows * cell_h + head * len(CATEGORIES)), (*rgb("#EAF4E4"), 255))
    d = ImageDraw.Draw(img)
    y = 0
    for cat in CATEGORIES:
        group = [(sp, w) for sp, w in painted if sp.category == cat]
        d.rectangle([0, y, img.width, y + head - 1], fill=(*rgb("#3A5A3A"), 255))
        d.text((8, y + 5), f"{cat} ({len(group)})", fill=(240, 248, 236, 255))
        y += head
        for i, (sp, wing) in enumerate(group):
            x0, y0 = (i % cols) * cell_w, y + (i // cols) * cell_h
            if (i // cols + i % cols) % 2:
                d.rectangle([x0, y0, x0 + cell_w - 1, y0 + cell_h - 1], fill=(*rgb("#DDEBD6"), 255))
            v = top_view(wing, sp, 2)
            img.alpha_composite(v, (x0 + (cell_w - v.width) // 2, y0 + 4))
            label = sp.name if len(sp.name) <= 15 else sp.name[:14] + "."
            d.text((x0 + (cell_w - d.textlength(label)) / 2, y0 + cell_h - 15), label, fill=(40, 48, 36, 255))
        y += (len(group) + cols - 1) // cols * cell_h
    os.makedirs(DOCS, exist_ok=True)
    img.convert("RGB").save(os.path.join(DOCS, "preview.png"))


def build_lifecycle(by_id):
    picks = ["monarch", "tiger_swallowtail", "blue_morpho", "blaze_monarch", "ender_dragon_wing"]
    cell = 220
    img = Image.new("RGBA", (cell * 4, 30 + cell * len(picks)), (*rgb("#E4F2FA"), 255))
    d = ImageDraw.Draw(img)
    for i, lab in enumerate(["Eggs", "Caterpillar", "Chrysalis", "Butterfly"]):
        d.text((i * cell + cell / 2 - d.textlength(lab) / 2, 10), lab, fill=(30, 40, 50, 255))
    for r, sid in enumerate(picks):
        sp, _ = by_id[sid]
        ltex = Image.open(os.path.join(RP, "textures", "entity", "butterflies", "larva", f"{sid}.png")).convert("RGBA")
        atex = Image.open(os.path.join(RP, "textures", "entity", "butterflies", f"{sid}.png")).convert("RGBA")
        cat = caterpillar_geo(LARVA_GEO[LARVA_STYLE[sp.shape]])
        shots = [
            render_model(EGG_GEO, ltex, yaw=210, pitch=40, size=cell),
            render_model(cat, ltex, yaw=235, pitch=25, size=cell),
            render_model(CHRYSALIS_GEO, ltex, yaw=215, pitch=15, size=cell),
            render_model(BUTTERFLY_GEO, atex, {"wing_left": -28, "wing_right": 28}, yaw=200, pitch=35, size=cell),
        ]
        for c, shot in enumerate(shots):
            img.alpha_composite(shot, (c * cell, 30 + r * cell))
        d.text((6, 30 + r * cell + 4), sp.name, fill=(30, 40, 50, 255))
    img.convert("RGB").save(os.path.join(DOCS, "lifecycle.png"))


def build_field_guide(painted):
    lines = ["| # | Butterfly | Group | Where to find it | Rarity |", "|---|---|---|---|---|"]
    for i, (sp, _) in enumerate(painted, 1):
        where = ", ".join(HABITAT_LABEL[h] for h in sp.habitat)
        lines.append(f"| {i} | {sp.name} | {sp.category} | {where} | {sp.rarity.title()} |")
    write_text(os.path.join(DOCS, "species.md"), "# Butterfly Field Guide\n\n" + "\n".join(lines) + "\n")


def build_mcaddon():
    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, "ButterfliesGalore.mcaddon")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for pack in (BP, RP):
            base = os.path.basename(pack)
            for dirpath, _, files in os.walk(pack):
                for fn in sorted(files):
                    full = os.path.join(dirpath, fn)
                    z.write(full, os.path.join(base, os.path.relpath(full, pack)))


if __name__ == "__main__":
    build()
    print(f"Built {len(SPECIES)} butterflies with full life cycles.")
