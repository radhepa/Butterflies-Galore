#!/usr/bin/env python3
"""Builds the Butterflies Galore behavior pack, resource pack and .mcaddon.

Every butterfly texture, item icon, block texture, model, spawn rule and
language entry is generated from the species table below, so adding or
tweaking a species is a one-line change followed by:

    python3 tools/generate.py
"""
import json
import math
import os
import random
import shutil
import uuid
import zipfile
from collections import Counter, deque

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "ButterfliesGalore_BP")
RP = os.path.join(ROOT, "ButterfliesGalore_RP")
DIST = os.path.join(ROOT, "dist")
DOCS = os.path.join(ROOT, "docs")
NS = "butterflies"
VERSION = [1, 0, 0]
MIN_ENGINE = [1, 21, 40]
UUID_NS = uuid.UUID("6f1d2c4e-8a8b-4f0e-9a51-0b7e0c1d2a33")


def uid(name):
    return str(uuid.uuid5(UUID_NS, name))


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, f):
    return tuple(max(0, min(255, round(v * f))) for v in c)


def hexc(c):
    return "#%02X%02X%02X" % c


# ---------------------------------------------------------------------------
# Wing painter
# ---------------------------------------------------------------------------
# A wing is painted on a 10 x 14 grid. u runs from the body (0) to the wing
# tip (9); v runs from the leading edge (0) to the rear (13). Rows 0-6 are the
# forewing and rows 7-13 the hindwing.

WW, WH = 10, 14

SHAPES = {
    "classic":     [(0, 6), (0, 8), (0, 9), (0, 9), (0, 8), (0, 7), (0, 6), (0, 7), (0, 8), (0, 8), (0, 7), (0, 6), (1, 4), None],
    "pointed":     [(0, 7), (0, 9), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5), (0, 7), (0, 7), (0, 7), (0, 6), (0, 5), (1, 3), None],
    "rounded":     [(0, 5), (0, 7), (0, 8), (0, 8), (0, 8), (0, 7), (0, 6), (0, 7), (0, 7), (0, 7), (0, 6), (0, 5), (1, 3), None],
    "swallowtail": [(0, 7), (0, 9), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5), (0, 6), (0, 7), (0, 7), (1, 6), (2, 5), (4, 5), (5, 5)],
    "kite":        [(0, 7), (0, 9), (0, 9), (0, 8), (0, 7), (0, 6), (0, 5), (0, 6), (0, 6), (0, 6), (1, 5), (2, 4), (4, 4), (4, 4)],
    "longwing":    [(0, 7), (0, 9), (0, 9), (0, 9), (0, 8), (0, 6), (0, 4), (0, 5), (0, 6), (0, 5), (0, 5), (0, 4), (1, 2), None],
    "leaf":        [(0, 8), (0, 9), (0, 8), (0, 8), (0, 8), (0, 7), (0, 7), (0, 7), (0, 7), (0, 7), (0, 6), (0, 5), (1, 4), (2, 3)],
    "scalloped":   [(0, 6), (0, 8), (0, 9), (0, 7), (0, 9), (0, 7), (0, 5), (0, 7), (0, 8), (0, 6), (0, 7), (0, 5), (1, 4), (2, 2)],
    "skipper":     [(0, 5), (0, 7), (0, 8), (0, 8), (0, 7), (0, 6), (0, 5), (0, 5), (0, 6), (0, 6), (0, 5), (0, 4), (1, 2), None],
    "birdwing":    [(0, 8), (0, 9), (0, 9), (0, 9), (0, 8), (0, 7), (0, 6), (0, 6), (0, 7), (0, 7), (0, 7), (0, 6), (0, 4), (1, 2)],
    "hairstreak":  [(0, 5), (0, 7), (0, 8), (0, 8), (0, 7), (0, 6), (0, 5), (0, 6), (0, 7), (0, 7), (0, 6), (1, 5), (3, 4), (4, 4)],
}

VEIN_BASE = (0.0, 5.0)
VEIN_TIPS = [(9, 1), (9, 3), (8, 5), (5, 6), (7, 8), (7, 10), (5, 12), (2, 12)]


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0 if l2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / l2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


class Wing:
    def __init__(self, shape):
        self.mask = set()
        for v, row in enumerate(SHAPES[shape]):
            if row:
                for u in range(row[0], row[1] + 1):
                    self.mask.add((u, v))
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
        self.apex = max((p for p in self.mask if p[1] <= 4), key=lambda p: p[0] - 0.3 * p[1])

    def region(self, name):
        if name == "all":
            return set(self.mask)
        if name == "fore":
            return {p for p in self.mask if p[1] <= 6}
        if name == "hind":
            return {p for p in self.mask if p[1] >= 7}
        if name == "tail":
            return {p for p in self.mask if p[1] >= 11 and p[0] >= 3}
        if name == "inner":
            return {p for p in self.mask if self.dist[p] >= 1}
        raise ValueError(name)

    def put(self, p, c, t=1.0):
        if p not in self.mask:
            return
        old = self.px[p]
        if old[3] == 0 or t >= 1:
            self.px[p] = (*c, 255)
        else:
            self.px[p] = (*mix(old[:3], c, t), 255)


# Feature builders. Each returns a function that paints onto a Wing.

def fill(c, region="all"):
    c = rgb(c)
    return lambda w: [w.put(p, c) for p in w.region(region)]


def grad(c, s=0.6, region="all"):
    c = rgb(c)
    return lambda w: [w.put(p, c, s * p[0] / max(1, w.rowmax[p[1]])) for p in w.region(region)]


def basal(c, n=2, region="all"):
    c = rgb(c)

    def f(w):
        for p in w.region(region):
            if p[0] < n - 1:
                w.put(p, c)
            elif p[0] == n - 1:
                w.put(p, c, 0.55)
    return f


def border(c, width=1, region="all"):
    c = rgb(c)
    return lambda w: [w.put(p, c) for p in w.region(region) if w.dist[p] < width]


def ring(c, k=1, region="all", spaced=True):
    c = rgb(c)
    return lambda w: [w.put(p, c) for p in w.region(region)
                      if w.dist[p] == k and (not spaced or (p[0] + p[1]) % 2 == 0)]


def veins(c, width=0.9, region="all"):
    c = rgb(c)

    def f(w):
        reg = w.region(region)
        for p in reg:
            for tip in VEIN_TIPS:
                if seg_dist(p, VEIN_BASE, tip) <= width / 2:
                    w.put(p, c)
                    break
    return f


def apex(c, r=2.0):
    c = rgb(c)

    def f(w):
        ax, ay = w.apex
        for p in w.region("fore"):
            if math.hypot(p[0] - ax, p[1] - ay) <= r:
                w.put(p, c)
    return f


def line(c, a, b, width=1.0, region="all"):
    c = rgb(c)
    return lambda w: [w.put(p, c) for p in w.region(region) if seg_dist(p, a, b) <= width * 0.6]


def circle(c, pos, r=1.0, region="all"):
    c = rgb(c)
    return lambda w: [w.put(p, c) for p in w.region(region) if math.hypot(p[0] - pos[0], p[1] - pos[1]) <= r]


def eye(pos, layers):
    """layers: [(radius, colour), ...] from the outside in."""
    return lambda w: [circle(col, pos, r)(w) for r, col in layers]


def spots(c, pts):
    c = rgb(c)
    return lambda w: [w.put(p, c) for p in pts]


def checker(c, region="all"):
    c = rgb(c)
    return lambda w: [w.put(p, c) for p in w.region(region)
                      if w.dist[p] >= 1 and (p[0] + 2 * p[1]) % 4 == 0]


def stripes(c, period=3, phase=0, region="all", slope=1):
    c = rgb(c)
    return lambda w: [w.put(p, c) for p in w.region(region)
                      if (p[0] + slope * p[1]) % period == phase]


def clear(region="all"):
    def f(w):
        for p in w.region(region):
            if w.dist[p] >= 1:
                w.px[p] = (0, 0, 0, 0)
    return f


def sheen(c, s=0.6, region="all"):
    c = rgb(c)
    return lambda w: [w.put(p, c, s) for p in w.region(region)
                      if w.dist[p] >= 1 and p[0] >= 2 and (p[0] * 3 + p[1] * 5) % 7 in (0, 3)]


def speckle(c, density=0.2, region="all", seed=7):
    c = rgb(c)

    def f(w):
        r = random.Random(seed)
        for p in sorted(w.region(region)):
            if r.random() < density:
                w.put(p, c)
    return f


# ---------------------------------------------------------------------------
# Species table
# ---------------------------------------------------------------------------

K = "#1A1612"   # soot black
W = "#F4F2EA"   # wing white
RARITY = {"common": 10, "uncommon": 6, "rare": 3, "legendary": 1}


class Species:
    def __init__(self, id, name, shape, habitat, scale, flap, rarity, feats,
                 body="#1E1A16", accent=None):
        self.id, self.name, self.shape = id, name, shape
        self.habitat, self.scale, self.flap = habitat, scale, flap
        self.rarity, self.feats = rarity, feats
        self.body, self.accent = rgb(body), rgb(accent) if accent else None


S = Species
SPECIES = [
    # --- Meadows, plains & flower fields -----------------------------------
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
    # --- Swallowtails -------------------------------------------------------
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
    # --- Woodland brush-foots ----------------------------------------------
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
    # --- Blues, coppers & hairstreaks --------------------------------------
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
    # --- Skippers -----------------------------------------------------------
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
    # --- Rainforest giants ---------------------------------------------------
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
    # --- Savanna, desert & badlands -----------------------------------------
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
    # --- Minecraft-world specialties ---------------------------------------
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
       ring(W, 0)]),
    S("ringlet", "Ringlet", "rounded", ["forest", "meadow"], 0.38, 1.2, "common",
      [fill("#3A2E28"), eye((5, 3), [(1.0, "#E8C87A"), (0.5, K)]), eye((4, 9), [(1.0, "#E8C87A"), (0.5, K)]),
       eye((5, 11), [(0.9, "#E8C87A"), (0.4, K)]), ring("#C8B8A0", 0)]),
    S("meadow_brown", "Meadow Brown", "classic", ["plains", "meadow"], 0.42, 1.2, "common",
      [fill("#6A5040"), circle("#E8A04A", (5, 3), 1.6), eye((6, 2), [(0.8, K), (0.3, W)]), border("#4A3828", 1)]),
    S("speckled_wood", "Speckled Wood", "classic", ["forest", "roofed", "taiga"], 0.4, 1.1, "common",
      [fill("#4A3A2A"), speckle("#E8D07A", 0.35, "inner", 31), eye((7, 2), [(0.8, K), (0.3, W)]),
       eye((5, 10), [(0.9, K), (0.3, W)]), border("#2A2018", 1)]),
    S("wall_brown", "Wall Brown", "classic", ["mountains", "mesa"], 0.4, 1.2, "common",
      [fill("#D8902A"), stripes("#5A3A18", 3, 0, "inner", 1), eye((7, 2), [(1.0, K), (0.4, W)]),
       eye((5, 10), [(0.8, K), (0.3, W)]), border("#4A2A10", 1)]),
    S("camberwell_beauty", "Camberwell Beauty", "scalloped", ["taiga", "birch"], 0.55, 0.9, "rare",
      [fill("#3A1A20"), border("#F2E2A0", 2), ring("#4A7AD8", 2, "all", True), spots("#F2E2A0", [(6, 0), (7, 1)])]),
    S("map_butterfly", "Map Butterfly", "classic", ["forest", "taiga"], 0.38, 1.2, "uncommon",
      [fill("#1E1612"), line("#F2EEE0", (4, 1), (2, 6), 0.8), line("#F2EEE0", (2, 7), (4, 11), 0.9),
       line("#E8822A", (1, 9), (6, 9), 0.6), spots(W, [(7, 1), (8, 2)]), border("#120E0A", 1)]),
    S("chequered_skipper", "Chequered Skipper", "skipper", ["birch", "taiga"], 0.27, 1.8, "uncommon",
      [fill("#3A2A1A"), checker("#E8B84A"), stripes("#E8B84A", 4, 2, "inner", 2), ring("#E8B84A", 0)], body="#3A2A1A"),
    S("palamedes_swallowtail", "Palamedes Swallowtail", "swallowtail", ["swamp", "mangrove_swamp"], 0.6, 0.8, "uncommon",
      [fill("#1A1610"), line("#F2D84A", (1, 2), (1, 12), 1.1), ring("#F2D84A", 1, "all", False),
       ring("#5A7AD0", 2, "hind", True), fill(K, "tail")]),
    S("banded_orange", "Banded Orange Heliconian", "longwing", ["jungle", "savanna"], 0.44, 1.0, "common",
      [fill("#F08A2A"), line(K, (2, 1), (8, 1), 0.7), line(K, (3, 3), (8, 3), 0.7), line(K, (1, 9), (5, 9), 0.7),
       border("#3A1A0A", 1)]),
]

assert len(SPECIES) == 100, len(SPECIES)
assert len({s.id for s in SPECIES}) == 100

# ---------------------------------------------------------------------------
# Habitat -> spawn conditions
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

def paint_wing(sp):
    w = Wing(sp.shape)
    for f in sp.feats:
        f(w)
    r = random.Random(sp.id)
    for p in sorted(w.mask):
        c = w.px[p]
        if c[3]:
            f = 1 + (r.random() - 0.5) * 0.12
            if p[0] == 0:
                f *= 0.86  # soft shadow where the wing meets the body
            w.px[p] = (*shade(c[:3], f), 255)
    return w


def body_colors(sp, wing):
    body = sp.body
    accent = sp.accent or mix(body, dominant_colors(wing)[0], 0.35)
    return body, accent


def dominant_colors(wing, n=3):
    # Group similar colours (the texture is dithered) and rank the groups by area.
    groups = {}
    for c in (c[:3] for c in wing.px.values() if c[3]):
        key = tuple(v // 40 for v in c)
        groups.setdefault(key, []).append(c)
    ranked = sorted(groups.values(), key=len, reverse=True)
    out = [tuple(round(sum(c[i] for c in g) / len(g)) for i in range(3)) for g in ranked[:n]]
    while len(out) < n:
        out.append(out[-1] if out else (128, 128, 128))
    return out


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
                px[14 + x, 0 + y] = left
            if right and right[3]:
                px[14 + x, 14 + y] = right
    # Body: box UV [2, 2, 10] at (0, 28).
    body, accent = body_colors(sp, wing)
    r = random.Random(sp.id + "body")
    for x in range(24):
        for y in range(28, 40):
            if (y < 38 and 10 <= x < 14) or (y >= 38):
                c = shade(body, 1 + (r.random() - 0.5) * 0.18)
                px[x, y] = (*c, 255)
    # Fuzzy thorax on the back and a dotted abdomen.
    for y in range(28, 38):
        for x in (10, 11):
            if y >= 34:
                px[x, y] = (*mix(body, accent, 0.55), 255)
            elif (x + y) % 3 == 0:
                px[x, y] = (*mix(body, accent, 0.4), 255)
    for x in list(range(0, 10)) + list(range(12, 22)):
        for y in (38, 39):
            if (x + y) % 3 == 0:
                px[x, y] = (*mix(body, accent, 0.5), 255)
    for x in range(24):
        if x not in range(10, 14):
            for y in range(28, 38):
                px[x, y] = (0, 0, 0, 0)
    # Antennae: solid patch used by every antenna cube.
    ant = shade(body, 0.8)
    for x in range(40, 56):
        for y in range(40, 50):
            px[x, y] = (*ant, 255)
    return img


def top_view(wing, sp, scale=1):
    """Full butterfly seen from above, for icons and previews."""
    w, h = WW * 2 + 2, WH
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for (u, v), c in wing.px.items():
        if c[3]:
            px[WW - 1 - u, v] = c
            px[WW + 2 + u, v] = c
    body, accent = body_colors(sp, wing)
    for v in range(0, 11):
        for x in (WW, WW + 1):
            px[x, v] = (*(mix(body, accent, 0.4) if v < 4 else body), 255)
    if scale != 1:
        img = img.resize((w * scale, h * scale), Image.NEAREST)
    return img


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
    for y in (3,):
        px[5, y] = GLASS_DK
        px[10, y] = GLASS_DK
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
    # faint glass tint inside
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
    sprite = [
        "XX...XX",
        "XPXbXPX",
        "XXXbXXX",
        ".QQbQQ.",
        ".QQ.QQ.",
    ]
    hind_cols = [wing.px[p][:3] for p in wing.mask if p[1] >= 9 and wing.px[p][3]]
    q = Counter(hind_cols).most_common(1)[0][0] if hind_cols else a
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
                half = 0 if i == 0 else (1 if i < 4 else 1)
                for x in range(sx - half, sx + half + 1):
                    put(x, y, r.choice(["#8E4FC8", "#B47AE0", "#6A2FA0", "#A060D8"]))
                if r.random() < 0.5:
                    put(sx + r.choice([-1, 1]), y, "#F2A33A")
        for lx, ly, d in ((2, 11, -1), (9, 12, 1), (6, 13, -1), (13, 10, 1), (10, 8, -1)):
            for i in range(3):
                put(lx + d * i, ly - i // 2, "#6E9A52" if i else "#5E8A4A")
    elif kind == "milkweed":
        for y in range(5, 16):
            put(7, y, "#5A8A3A")
            put(8, y, "#4A7A2E")
        for ly, d in ((8, -1), (10, 1), (12, -1), (13, 1)):
            for i in range(1, 5):
                put(7 + d * i if d < 0 else 8 + d * i, ly - (i // 3), "#6AA048")
                put(7 + d * i if d < 0 else 8 + d * i, ly + 1 - (i // 3), "#5A8A3A")
        for cx, cy in ((5, 3), (10, 4), (8, 1)):
            for dx in range(-2, 3):
                for dy in range(-1, 2):
                    if abs(dx) + abs(dy) <= 2:
                        put(cx + dx, cy + dy, r.choice(["#E07AA0", "#F2A6C2", "#C85A88"]))
    elif kind == "coneflower":
        for sx, top in ((4, 4), (11, 2), (8, 7)):
            for y in range(top + 2, 16):
                put(sx, y, "#4E7A3A")
            put(sx, top, "#8A4A1A")
            put(sx, top + 1, "#C8602A")
            put(sx - 1, top, "#A0521E")
            put(sx + 1, top, "#A0521E")
            for dx, dy in ((-2, 1), (2, 1), (-2, 2), (2, 2), (-1, 2), (1, 2), (-3, 2), (3, 2)):
                put(sx + dx, top + dy, r.choice(["#D65AA8", "#E07AB8", "#C04A98"]))
        for lx, ly in ((3, 12), (12, 11), (6, 14)):
            put(lx, ly, "#6A9A4A")
            put(lx + 1, ly - 1, "#6A9A4A")
    return img


def chrysalis_texture():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    r = random.Random("chrysalis")
    for x in range(16):
        for y in range(16):
            px[x, y] = (*shade(rgb("#4FB86A"), 1 + (r.random() - 0.5) * 0.15), 255)
    # gold dots and a dark band near the top of each side face
    for x in range(0, 16, 2):
        px[x, 5] = (*rgb("#E8C23A"), 255)
        px[x + 1 if x + 1 < 16 else x, 6] = (*rgb("#1A2A1A"), 255)
    for x in range(1, 16, 4):
        px[x, 8] = (*rgb("#E8C23A"), 255)
        px[x, 12] = (*rgb("#8ADC9A"), 255)
    # stalk region
    for x in range(0, 4):
        for y in range(10, 14):
            px[x, y] = (*rgb("#2A2A1E"), 255)
    return img


def pack_icon(featured):
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(128):
        c = mix(rgb("#8FD0F2"), rgb("#D8F0FA"), y / 127)
        d.line([(0, y), (127, y)], fill=(*c, 255))
    for x in range(128):
        h = 104 + int(3 * math.sin(x / 7))
        d.line([(x, h), (x, 127)], fill=(*rgb("#5DAA3C"), 255))
        d.line([(x, h + 8), (x, 127)], fill=(*rgb("#4A8A30"), 255))
    big = featured[0]
    view = top_view(big[1], big[0], 4)
    img.alpha_composite(view, ((128 - view.width) // 2, 22))
    for i, (sp, wing) in enumerate(featured[1:3]):
        v = top_view(wing, sp, 2)
        img.alpha_composite(v, (6 + i * 74, 84))
    return img


# ---------------------------------------------------------------------------
# Pack content
# ---------------------------------------------------------------------------
FLOWER_BLOCKS = ["butterfly_bush", "milkweed", "coneflower"]
VANILLA_FLOWERS = [
    "minecraft:poppy", "minecraft:dandelion", "minecraft:blue_orchid", "minecraft:allium", "minecraft:azure_bluet",
    "minecraft:red_tulip", "minecraft:orange_tulip", "minecraft:white_tulip", "minecraft:pink_tulip",
    "minecraft:oxeye_daisy", "minecraft:cornflower", "minecraft:lily_of_the_valley", "minecraft:sunflower",
    "minecraft:lilac", "minecraft:rose_bush", "minecraft:peony", "minecraft:pink_petals", "minecraft:torchflower",
    "minecraft:flowering_azalea",
]
SOIL = ["minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt", "minecraft:podzol",
        "minecraft:rooted_dirt", "minecraft:moss_block", "minecraft:mycelium", "minecraft:farmland"]


def entity_behavior(sp):
    fire = any(h in NETHER for h in sp.habitat)
    comps = {
        "minecraft:type_family": {"family": ["butterfly", "arthropod", "mob"]},
        "minecraft:collision_box": {"width": 0.6, "height": 0.5},
        "minecraft:scale": {"value": sp.scale},
        "minecraft:health": {"value": 3, "max": 3},
        "minecraft:breathable": {"total_supply": 15, "suffocate_time": 0},
        "minecraft:damage_sensor": {"triggers": [{"cause": "fall", "deals_damage": "no"}]},
        "minecraft:nameable": {},
        "minecraft:physics": {},
        "minecraft:pushable": {"is_pushable": True, "is_pushable_by_piston": True},
        "minecraft:despawn": {"despawn_from_distance": {}},
        "minecraft:conditional_bandwidth_optimization": {},
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
            "target_blocks": VANILLA_FLOWERS + [f"{NS}:{b}" for b in FLOWER_BLOCKS],
        },
        "minecraft:behavior.random_hover": {
            "priority": 12, "xz_dist": 8, "y_dist": 6, "y_offset": -1, "interval": 1, "hover_height": [1, 4],
        },
        "minecraft:interact": {"interactions": [{
            "on_interact": {
                "filters": {"all_of": [
                    {"test": "is_family", "subject": "other", "value": "player"},
                    {"test": "has_equipment", "domain": "hand", "subject": "other", "value": f"{NS}:butterfly_jar"},
                ]},
                "event": f"{NS}:caught", "target": "self",
            },
            "use_item": True,
            "transform_to_item": f"{NS}:jar_{sp.id}",
            "swing": True,
            "interact_text": "action.interact.butterflies.catch",
        }]},
    }
    if fire:
        comps["minecraft:fire_immune"] = {}
    return {
        "format_version": "1.21.0",
        "minecraft:entity": {
            "description": {"identifier": f"{NS}:{sp.id}", "is_spawnable": True, "is_summonable": True},
            "component_groups": {f"{NS}:caught": {"minecraft:instant_despawn": {}}},
            "components": comps,
            "events": {f"{NS}:caught": {"add": {"component_groups": [f"{NS}:caught"]}}},
        },
    }



def spawn_rules(sp):
    tags = sp.habitat
    biome = {"any_of": [{"test": "has_biome_tag", "operator": "==", "value": t} for t in tags]}
    cond = {"minecraft:weight": {"default": RARITY[sp.rarity]},
            "minecraft:herd": {"min_size": 1, "max_size": 2 if sp.rarity in ("common", "uncommon") else 1},
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
            "description": {"identifier": f"{NS}:{sp.id}", "population_control": "ambient"},
            "conditions": [cond],
        },
    }


def client_entity(sp, egg):
    return {
        "format_version": "1.10.0",
        "minecraft:client_entity": {
            "description": {
                "identifier": f"{NS}:{sp.id}",
                "materials": {"default": "entity_alphatest"},
                "textures": {"default": f"textures/entity/butterflies/{sp.id}"},
                "geometry": {"default": "geometry.butterflies.butterfly"},
                "animations": {"fly": "animation.butterflies.butterfly.fly"},
                "scripts": {"initialize": [f"v.flap = {sp.flap};"], "animate": ["fly"]},
                "render_controllers": ["controller.render.butterflies.butterfly"],
                "spawn_egg": {"base_color": hexc(egg[0]), "overlay_color": hexc(egg[1])},
            }
        },
    }


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


def chrysalis_block():
    return {
        "format_version": "1.21.40",
        "minecraft:block": {
            "description": {"identifier": f"{NS}:chrysalis", "menu_category": {"category": "nature"}},
            "components": {
                "minecraft:geometry": "geometry.butterflies.chrysalis",
                "minecraft:material_instances": {"*": {
                    "texture": f"{NS}_chrysalis", "render_method": "alpha_test", "ambient_occlusion": False}},
                "minecraft:collision_box": False,
                "minecraft:selection_box": {"origin": [-3, 5, -3], "size": [6, 11, 6]},
                "minecraft:destructible_by_mining": {"seconds_to_destroy": 0.2},
                "minecraft:light_dampening": 0,
                "minecraft:map_color": "#4FB86A",
            },
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

CHRYSALIS_GEO = {
    "format_version": "1.12.0",
    "minecraft:geometry": [{
        "description": {"identifier": "geometry.butterflies.chrysalis", "texture_width": 16, "texture_height": 16},
        "bones": [{"name": "chrysalis", "pivot": [0, 16, 0], "cubes": [
            {"origin": [-0.5, 13, -0.5], "size": [1, 3, 1], "uv": [0, 10]},
            {"origin": [-2, 7, -2], "size": [4, 6, 4], "uv": [0, 0]},
            {"origin": [-1, 5, -1], "size": [2, 2, 2], "uv": [4, 10]},
        ]}],
    }],
}

BUTTERFLY_GEO = {
    "format_version": "1.12.0",
    "minecraft:geometry": [{
        "description": {
            "identifier": "geometry.butterflies.butterfly", "texture_width": 64, "texture_height": 64,
            "visible_bounds_width": 2, "visible_bounds_height": 1.5, "visible_bounds_offset": [0, 0.25, 0],
        },
        "bones": [
            {"name": "root", "pivot": [0, 0, 0]},
            {"name": "body", "parent": "root", "pivot": [0, 2, 0],
             "cubes": [{"origin": [-1, 1, -5], "size": [2, 2, 10], "uv": [0, 28]}]},
            {"name": "antennae", "parent": "body", "pivot": [0, 3, -5], "cubes": [
                {"origin": [-0.9, 3, -7], "size": [0.5, 0.5, 2], "uv": [40, 40]},
                {"origin": [-1.1, 3.5, -9], "size": [0.5, 0.5, 2], "uv": [40, 40]},
                {"origin": [-1.5, 4, -10], "size": [1, 1, 1], "uv": [40, 40]},
                {"origin": [0.4, 3, -7], "size": [0.5, 0.5, 2], "uv": [40, 40]},
                {"origin": [0.6, 3.5, -9], "size": [0.5, 0.5, 2], "uv": [40, 40]},
                {"origin": [0.5, 4, -10], "size": [1, 1, 1], "uv": [40, 40]},
            ]},
            {"name": "wing_left", "parent": "body", "pivot": [-1, 2.5, 0],
             "cubes": [{"origin": [-11, 2.5, -5.5], "size": [10, 0, 14], "uv": [0, 0]}]},
            {"name": "wing_right", "parent": "body", "pivot": [1, 2.5, 0],
             "cubes": [{"origin": [1, 2.5, -5.5], "size": [10, 0, 14], "uv": [0, 14]}]},
        ],
    }],
}

FLAP = ("(q.is_on_ground ? math.sin(q.life_time * 90) * 15 : "
        "math.sin(q.life_time * 1500 * v.flap) * (math.sin(q.life_time * 37) > 0.8 ? 12 : 55))")
ANIMATION = {
    "format_version": "1.8.0",
    "animations": {
        "animation.butterflies.butterfly.fly": {
            "loop": True,
            "bones": {
                "wing_left": {"rotation": [0, 0, FLAP]},
                "wing_right": {"rotation": [0, 0, "-" + FLAP]},
                "root": {"position": [0, "q.is_on_ground ? 0 : math.sin(q.life_time * 400 * v.flap) * 0.6", 0]},
                "antennae": {"rotation": ["math.sin(q.life_time * 150) * 4", 0, 0]},
            },
        }
    },
}

RENDER_CONTROLLER = {
    "format_version": "1.8.0",
    "render_controllers": {
        "controller.render.butterflies.butterfly": {
            "geometry": "Geometry.default",
            "materials": [{"*": "Material.default"}],
            "textures": ["Texture.default"],
        }
    },
}


def recipes():
    out = {}
    out["butterfly_jar"] = {
        "format_version": "1.20.10",
        "minecraft:recipe_shaped": {
            "description": {"identifier": f"{NS}:butterfly_jar"},
            "tags": ["crafting_table"],
            "pattern": [" W ", "G G", "GGG"],
            "key": {"W": {"tag": "minecraft:planks"}, "G": {"item": "minecraft:glass"}},
            "unlock": [{"item": "minecraft:glass"}],
            "result": {"item": f"{NS}:butterfly_jar", "count": 3},
        },
    }

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
    shapeless("chrysalis", ["minecraft:string", "minecraft:green_dye", "minecraft:gold_nugget"],
              f"{NS}:chrysalis", 1, "minecraft:string")
    # Purple and pink dye from the new flowers.
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
    own = "bp" if is_bp else "rp"
    other = "rp" if is_bp else "bp"
    return {
        "format_version": 2,
        "header": {
            "name": "pack.name",
            "description": "pack.description",
            "uuid": uid(f"{own}-header"),
            "version": VERSION,
            "min_engine_version": MIN_ENGINE,
        },
        "modules": [{
            "type": "data" if is_bp else "resources",
            "uuid": uid(f"{own}-module"),
            "version": VERSION,
        }],
        "dependencies": [{"uuid": uid(f"{other}-header"), "version": VERSION}],
        "metadata": {"authors": ["Butterflies Galore"]},
    }


def clean(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


def build():
    for p in (BP, RP):
        clean(p)
    painted = [(sp, paint_wing(sp)) for sp in SPECIES]

    # --- Manifests, icons & pack language ---------------------------------
    write_json(os.path.join(BP, "manifest.json"), manifest("bp"))
    write_json(os.path.join(RP, "manifest.json"), manifest("rp"))
    by_id = dict((sp.id, (sp, w)) for sp, w in painted)
    icon = pack_icon([by_id["monarch"], by_id["blue_morpho"], by_id["peacock"]])
    save_png(icon, os.path.join(BP, "pack_icon.png"))
    save_png(icon, os.path.join(RP, "pack_icon.png"))
    desc = "100 hand-crafted butterflies to discover, catch and collect."
    for p, label in ((BP, "Behavior Pack"), (RP, "Resource Pack")):
        write_json(os.path.join(p, "texts", "languages.json"), ["en_US"])
        write_text(os.path.join(p, "texts", "en_US.lang"),
                   f"pack.name=Butterflies Galore {label}\npack.description={desc}\n")

    # --- Shared client assets ---------------------------------------------
    write_json(os.path.join(RP, "models", "entity", "butterfly.geo.json"), BUTTERFLY_GEO)
    write_json(os.path.join(RP, "models", "blocks", "cross.geo.json"), CROSS_GEO)
    write_json(os.path.join(RP, "models", "blocks", "chrysalis.geo.json"), CHRYSALIS_GEO)
    write_json(os.path.join(RP, "animations", "butterfly.animation.json"), ANIMATION)
    write_json(os.path.join(RP, "render_controllers", "butterfly.render_controllers.json"), RENDER_CONTROLLER)

    lang = [f"pack.name=Butterflies Galore Resource Pack", f"pack.description={desc}", "",
            "## Butterflies"]
    item_tex = {}
    for sp, wing in painted:
        save_png(entity_texture(sp, wing), os.path.join(RP, "textures", "entity", "butterflies", f"{sp.id}.png"))
        egg = dominant_colors(wing, 2)
        write_json(os.path.join(RP, "entity", f"{sp.id}.entity.json"), client_entity(sp, egg))
        write_json(os.path.join(BP, "entities", f"{sp.id}.json"), entity_behavior(sp))
        write_json(os.path.join(BP, "spawn_rules", f"{sp.id}.json"), spawn_rules(sp))
        # Jar item
        save_png(jar_icon(sp, wing), os.path.join(RP, "textures", "items", "jars", f"jar_{sp.id}.png"))
        item_tex[f"{NS}_jar_{sp.id}"] = {"textures": f"textures/items/jars/jar_{sp.id}"}
        write_json(os.path.join(BP, "items", "jars", f"jar_{sp.id}.json"),
                   item(f"{NS}:jar_{sp.id}", f"{NS}_jar_{sp.id}", f"item.{NS}.jar_{sp.id}.name", {
                       "minecraft:max_stack_size": 16,
                       "minecraft:entity_placer": {"entity": f"{NS}:{sp.id}"},
                   }))
        lang += [f"entity.{NS}:{sp.id}.name={sp.name}",
                 f"item.spawn_egg.entity.{NS}:{sp.id}.name=Spawn {sp.name}",
                 f"item.{NS}.jar_{sp.id}.name={sp.name} in a Jar"]

    # --- Utility items -----------------------------------------------------
    save_png(jar_base(), os.path.join(RP, "textures", "items", "butterfly_jar.png"))
    save_png(nectar_icon(), os.path.join(RP, "textures", "items", "nectar_bottle.png"))
    item_tex[f"{NS}_butterfly_jar"] = {"textures": "textures/items/butterfly_jar"}
    item_tex[f"{NS}_nectar_bottle"] = {"textures": "textures/items/nectar_bottle"}
    write_json(os.path.join(BP, "items", "butterfly_jar.json"),
               item(f"{NS}:butterfly_jar", f"{NS}_butterfly_jar", f"item.{NS}.butterfly_jar.name",
                    {"minecraft:max_stack_size": 64}, "equipment"))
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

    # --- Blocks -------------------------------------------------------------
    terrain = {}
    blocks_json = {"format_version": "1.21.40"}
    for name, height in (("butterfly_bush", 15), ("milkweed", 14), ("coneflower", 12)):
        save_png(plant_texture(name), os.path.join(RP, "textures", "blocks", f"{name}.png"))
        terrain[f"{NS}_{name}"] = {"textures": f"textures/blocks/{name}"}
        write_json(os.path.join(BP, "blocks", f"{name}.json"), plant_block(name, height))
        blocks_json[f"{NS}:{name}"] = {"sound": "grass"}
    save_png(chrysalis_texture(), os.path.join(RP, "textures", "blocks", "chrysalis.png"))
    terrain[f"{NS}_chrysalis"] = {"textures": "textures/blocks/chrysalis"}
    write_json(os.path.join(BP, "blocks", "chrysalis.json"), chrysalis_block())
    blocks_json[f"{NS}:chrysalis"] = {"sound": "grass"}
    write_json(os.path.join(RP, "textures", "terrain_texture.json"),
               {"resource_pack_name": "butterflies_galore", "texture_name": "atlas.terrain", "padding": 8,
                "num_mip_levels": 4, "texture_data": terrain})
    write_json(os.path.join(RP, "blocks.json"), blocks_json)

    lang += ["", "## Items & blocks",
             f"item.{NS}.butterfly_jar.name=Butterfly Jar",
             f"item.{NS}.nectar_bottle.name=Bottle of Nectar",
             f"tile.{NS}:butterfly_bush.name=Butterfly Bush",
             f"tile.{NS}:milkweed.name=Milkweed",
             f"tile.{NS}:coneflower.name=Coneflower",
             f"tile.{NS}:chrysalis.name=Chrysalis",
             f"action.interact.butterflies.catch=Catch", ""]
    write_text(os.path.join(RP, "texts", "en_US.lang"), "\n".join(lang))

    for name, data in recipes().items():
        write_json(os.path.join(BP, "recipes", f"{name}.json"), data)
    for rel, data in features().items():
        write_json(os.path.join(BP, rel), data)

    build_preview(painted)
    build_readme_table(painted)
    build_mcaddon()


def build_preview(painted):
    cols, cell_w, cell_h = 10, 112, 84
    rows = (len(painted) + cols - 1) // cols
    img = Image.new("RGBA", (cols * cell_w, rows * cell_h), (*rgb("#EAF4E4"), 255))
    d = ImageDraw.Draw(img)
    for i, (sp, wing) in enumerate(painted):
        x0, y0 = (i % cols) * cell_w, (i // cols) * cell_h
        if (i // cols + i % cols) % 2:
            d.rectangle([x0, y0, x0 + cell_w - 1, y0 + cell_h - 1], fill=(*rgb("#DDEBD6"), 255))
        v = top_view(wing, sp, 4)
        img.alpha_composite(v, (x0 + (cell_w - v.width) // 2, y0 + 6))
        label = sp.name if len(sp.name) <= 18 else sp.name[:17] + "."
        tw = d.textlength(label)
        d.text((x0 + (cell_w - tw) / 2, y0 + cell_h - 16), label, fill=(40, 48, 36, 255))
    os.makedirs(DOCS, exist_ok=True)
    img.convert("RGB").save(os.path.join(DOCS, "preview.png"))


def build_readme_table(painted):
    lines = ["| # | Butterfly | Where to find it | Rarity |", "|---|---|---|---|"]
    for i, (sp, _) in enumerate(painted, 1):
        where = ", ".join(HABITAT_LABEL[h] for h in sp.habitat)
        lines.append(f"| {i} | {sp.name} | {where} | {sp.rarity.title()} |")
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
    print(f"Built {len(SPECIES)} butterflies.")
