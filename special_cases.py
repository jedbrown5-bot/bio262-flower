"""
special_cases.py
----------------
Special-case flowers for the BIO262 dissection tool.

Some flowers break the generic-flower rules in instructive ways. This module
draws a simple schematic for each, gives the key facts, and asks a short quiz.
Taxa: Eucalyptus, Asteraceae (daisy), Banksia, Callistemon (bottlebrush), Acacia.

Taxonomy checked against the Atlas of Living Australia. All five are accepted.
Callistemon is kept as its own genus by ALA and APC, though some sources place
it in Melaleuca.
"""

import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Ellipse, Wedge, FancyBboxPatch

INK = "#22463d"
GREEN = "#6f9a54"
LEAF = "#cde0b8"
BG = "#f4f8f1"


def _new_ax(title):
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.text(0.2, 6.7, title, fontsize=15, fontweight="bold", color=INK, va="top")
    return fig, ax


def _label(ax, text, xy, xytext):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=9.5, color=INK, ha="center",
                va="center", zorder=20,
                arrowprops=dict(arrowstyle="-", color=INK, lw=1.1),
                bbox=dict(boxstyle="round,pad=0.28", fc="white", ec=INK, lw=1.1))


def _caption(ax, x, text):
    ax.text(x, 0.35, text, fontsize=10, color=INK, ha="center", fontstyle="italic")


# ----------------------------------------------------------------------
def _draw_eucalyptus(ax):
    def hypanthium(cx, base, w, h, color=LEAF, ec=GREEN):
        pts = [(cx - w * 0.42, base), (cx + w * 0.42, base),
               (cx + w * 0.6, base + h), (cx - w * 0.6, base + h)]
        ax.add_patch(Polygon(pts, closed=True, facecolor=color, edgecolor=ec, lw=2,
                     zorder=3))
        ax.add_patch(Ellipse((cx, base + h), w * 1.2, h * 0.22, facecolor=color,
                     edgecolor=ec, lw=2, zorder=3))

    # --- bud with operculum ---
    hypanthium(2.0, 1.3, 1.3, 1.2)
    ax.add_patch(Polygon([(2.0 - 0.82, 2.55), (2.0 + 0.82, 2.55), (2.0, 3.9)],
                 closed=True, facecolor="#b7cf97", edgecolor=GREEN, lw=2, zorder=4))
    _label(ax, "Operculum\n(fused sepals + petals)", (2.0, 3.3), (2.1, 5.6))
    _caption(ax, 2.0, "bud")

    # --- open flower: showy stamens ---
    cx = 5.2
    hypanthium(cx, 1.3, 1.3, 1.1)
    for a in np.linspace(-72, 72, 15):
        r = math.radians(a)
        x2 = cx + 1.9 * math.sin(r)
        y2 = 2.5 + 1.9 * math.cos(r)
        ax.plot([cx, x2], [2.45, y2], color="#efe6c0", lw=2, zorder=2,
                solid_capstyle="round")
        ax.add_patch(Circle((x2, y2), 0.11, facecolor="#e8c14a", edgecolor="#9c7d1c",
                     lw=0.8, zorder=5))
    ax.plot([cx, cx], [2.45, 4.1], color="#9fce86", lw=2.4, zorder=3)
    _label(ax, "Showy stamens", (cx + 1.4, 3.4), (7.0, 5.7))
    _caption(ax, cx, "flower, operculum shed")

    # --- woody capsule (gumnut) ---
    cx = 8.3
    hypanthium(cx, 1.3, 1.15, 1.0, color="#b39169", ec="#7c5f38")
    for dx in (-0.35, 0, 0.35):
        ax.add_patch(Polygon([(cx + dx - 0.16, 2.3), (cx + dx + 0.16, 2.3),
                     (cx + dx, 2.75)], closed=True, facecolor="#7c5f38",
                     edgecolor="#7c5f38", zorder=4))
    _label(ax, "Woody capsule\n(gumnut)", (cx, 2.5), (cx, 4.4))
    _caption(ax, cx, "fruit")


def _draw_asteraceae(ax):
    # --- top view of the head ---
    hx, hy = 2.7, 3.6
    for a in np.linspace(0, 360, 15, endpoint=False):
        r = math.radians(a)
        ax.add_patch(Ellipse((hx + 1.55 * math.cos(r), hy + 1.55 * math.sin(r)),
                     1.5, 0.55, angle=a, facecolor="#f4f1e8", edgecolor="#d9d3bf",
                     lw=1.2, zorder=2))
    ax.add_patch(Circle((hx, hy), 1.05, facecolor="#e6b93a", edgecolor="#b98f1e",
                 lw=1.5, zorder=3))
    for a in np.linspace(0, 360, 18, endpoint=False):
        r = math.radians(a)
        rr = 0.55
        ax.add_patch(Circle((hx + rr * math.cos(r), hy + rr * math.sin(r)), 0.11,
                     facecolor="#b98f1e", edgecolor="none", zorder=4))
    _label(ax, "Ray floret", (hx + 2.9, hy), (hx + 0.2, 6.2))
    _label(ax, "Disc florets", (hx, hy), (0.9, 1.1))

    # --- longitudinal section ---
    sx = 7.4
    ax.add_patch(Wedge((sx, 1.7), 1.4, 0, 180, facecolor="#cde0b8", edgecolor=GREEN,
                 lw=2, zorder=2))
    for a in np.linspace(-60, 60, 9):
        r = math.radians(a)
        bx = sx + 1.25 * math.sin(r)
        by = 1.7 + 1.25 * math.cos(r)
        tx = sx + 2.2 * math.sin(r)
        ty = 1.7 + 2.2 * math.cos(r)
        ax.plot([bx, tx], [by, ty], color="#e6b93a", lw=3, zorder=3,
                solid_capstyle="round")
        ax.add_patch(Circle((tx, ty), 0.12, facecolor="#f0d76a", edgecolor="#b98f1e",
                     lw=0.7, zorder=4))
    for s in (-1, 1):
        ax.add_patch(Polygon([(sx + s * 1.35, 1.7), (sx + s * 1.7, 1.4),
                     (sx + s * 1.5, 2.2)], closed=True, facecolor="#7aa758",
                     edgecolor=GREEN, lw=1, zorder=1))
    _label(ax, "Each is a tiny\nflower (floret)", (sx + 1.2, 3.1), (sx + 1.2, 5.4))
    _label(ax, "Involucral bracts", (sx - 1.5, 1.9), (sx - 1.9, 3.9))
    _label(ax, "Receptacle", (sx, 1.4), (sx - 0.2, 0.9))


def _draw_banksia(ax):
    # --- flower spike ---
    sx = 2.2
    ax.add_patch(FancyBboxPatch((sx - 0.9, 1.0), 1.8, 4.2,
                 boxstyle="round,pad=0.02,rounding_size=0.6", facecolor="#d9a441",
                 edgecolor="#a9781f", lw=2, zorder=2))
    for yy in np.linspace(1.3, 5.0, 12):
        for s in (-1, 1):
            ax.plot([sx, sx + s * 0.8], [yy, yy + 0.18], color="#a9781f", lw=1.2,
                    zorder=3)
    ax.add_patch(FancyBboxPatch((sx - 0.35, -0.2), 0.7, 1.4,
                 boxstyle="round,pad=0.02,rounding_size=0.2", facecolor=GREEN,
                 edgecolor="#436b37", lw=1.5, zorder=1))
    _label(ax, "Flower spike\n(hundreds of flowers)", (sx + 0.9, 3.4), (sx + 1.1, 5.8))

    # --- single flower detail ---
    fx = 7.2
    ax.plot([fx, fx], [1.2, 3.4], color="#cbb26a", lw=5, zorder=2,
            solid_capstyle="round")   # perianth tube
    for a in (-40, -14, 14, 40):
        r = math.radians(a)
        ax.plot([fx, fx + 0.9 * math.sin(r)], [3.4, 3.4 + 0.9 * math.cos(r)],
                color="#cbb26a", lw=4, zorder=2, solid_capstyle="round")
    # long wiry style with pollen presenter
    stylex = [fx, fx - 0.2, fx + 0.15, fx]
    styley = [1.4, 3.0, 4.4, 5.4]
    ax.plot(stylex, styley, color="#8a6d3b", lw=2, zorder=4)
    ax.add_patch(Circle((fx, 5.5), 0.16, facecolor="#8a6d3b", edgecolor="#5f4a24",
                 zorder=5))
    _label(ax, "4 tepals", (fx + 0.6, 3.7), (fx + 1.9, 4.6))
    _label(ax, "Long style", (fx - 0.05, 3.0), (fx - 1.7, 3.2))
    _label(ax, "Pollen presenter", (fx, 5.5), (fx + 1.2, 6.2))
    _caption(ax, fx, "one flower")


def _draw_callistemon(ax):
    sx = 4.2
    # stem, continuing into a leafy shoot above the brush
    ax.add_patch(FancyBboxPatch((sx - 0.18, -0.2), 0.36, 6.4,
                 boxstyle="round,pad=0.02,rounding_size=0.15", facecolor=GREEN,
                 edgecolor="#436b37", lw=1.5, zorder=1))
    # brush of long stamens
    for yy in np.linspace(1.6, 4.2, 11):
        for s in (-1, 1):
            tx = sx + s * 2.1
            ax.plot([sx, tx], [yy, yy + 0.12], color="#d24b3a", lw=2.2, zorder=3,
                    solid_capstyle="round")
            ax.add_patch(Circle((tx, yy + 0.12), 0.1, facecolor="#e8c14a",
                         edgecolor="#9c7d1c", lw=0.6, zorder=4))
        ax.add_patch(Circle((sx, yy), 0.12, facecolor="#cde0b8", edgecolor=GREEN,
                     lw=0.8, zorder=3))
    # leafy shoot above
    for s, yy in [(-1, 5.1), (1, 5.4), (-1, 5.7)]:
        ax.add_patch(Ellipse((sx + s * 0.5, yy), 1.1, 0.34, angle=s * 25,
                     facecolor="#7aa758", edgecolor=GREEN, lw=1, zorder=2))
    # woody fruits below the brush
    for yy in (0.7, 1.05):
        for s in (-1, 1):
            ax.add_patch(Circle((sx + s * 0.32, yy), 0.16, facecolor="#8a6d3b",
                         edgecolor="#5f4a24", lw=1, zorder=3))
    _label(ax, "Showy part is\nthe stamens", (sx + 2.0, 3.0), (7.7, 4.4))
    _label(ax, "Spike axis grows on\ninto a leafy shoot", (sx + 0.4, 5.4), (7.2, 6.2))
    _label(ax, "Woody fruits", (sx - 0.32, 0.9), (1.6, 1.3))


def _draw_acacia(ax):
    # globular head
    gx, gy = 2.8, 3.4
    ax.add_patch(Circle((gx, gy), 0.95, facecolor="#f0d24a", edgecolor="#c7a51f",
                 lw=1.5, zorder=3))
    for a in np.linspace(0, 360, 40, endpoint=False):
        r = math.radians(a)
        ax.plot([gx + 0.9 * math.cos(r), gx + 1.35 * math.cos(r)],
                [gy + 0.9 * math.sin(r), gy + 1.35 * math.sin(r)],
                color="#e0be2e", lw=1.4, zorder=2)
    ax.plot([gx, gx - 0.6], [gy - 0.95, gy - 2.2], color=GREEN, lw=3, zorder=1)
    _label(ax, "Globular head", (gx, gy + 1.2), (gx, 6.1))

    # cylindrical spike
    cxx = 6.8
    ax.add_patch(FancyBboxPatch((cxx - 0.55, 2.2), 1.1, 2.6,
                 boxstyle="round,pad=0.02,rounding_size=0.5", facecolor="#f0d24a",
                 edgecolor="#c7a51f", lw=1.5, zorder=3))
    for yy in np.linspace(2.4, 4.6, 9):
        for s in (-1, 1):
            ax.plot([cxx + s * 0.55, cxx + s * 0.95], [yy, yy], color="#e0be2e",
                    lw=1.4, zorder=2)
    ax.plot([cxx, cxx + 0.5], [2.2, 1.0], color=GREEN, lw=3, zorder=1)
    _label(ax, "Cylindrical spike", (cxx, 4.7), (cxx, 6.1))
    _label(ax, "Showy fluff is\nthe stamens", (cxx + 0.95, 3.5), (cxx + 1.4, 2.0))


_DRAW = {
    "eucalyptus": _draw_eucalyptus,
    "asteraceae": _draw_asteraceae,
    "banksia": _draw_banksia,
    "callistemon": _draw_callistemon,
    "acacia": _draw_acacia,
}


def draw_special(key):
    entry = SPECIALS_BY_KEY[key]
    fig, ax = _new_ax(entry["title"])
    _DRAW[key](ax)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    return fig


# ----------------------------------------------------------------------
SPECIALS = [
    {"key": "eucalyptus", "name": "Eucalyptus", "italic": True, "family": "Myrtaceae",
     "title": "Eucalyptus  ·  Myrtaceae",
     "wiki": "https://en.wikipedia.org/wiki/Eucalyptus",
     "special": "A eucalypt bud is capped by an operculum. This cap forms from fused "
                "sepals and petals. It is shed when the flower opens. The showy part "
                "of the flower is the many stamens, not petals. The ovary is inferior "
                "and the fruit is a woody capsule, the gumnut.",
     "quiz": [
         {"q": "In a eucalypt flower, the showy part is the",
          "options": ["Petals", "Stamens", "Sepals", "Bracts"], "answer": "Stamens"},
         {"q": "The operculum is",
          "options": ["The woody fruit", "A cap of fused sepals and petals",
                      "The stigma", "A single leaf"],
          "answer": "A cap of fused sepals and petals"},
     ]},
    {"key": "asteraceae", "name": "Asteraceae", "italic": False, "family": "daisy family",
     "title": "Asteraceae  ·  the daisy family",
     "wiki": "https://en.wikipedia.org/wiki/Asteraceae",
     "special": "A daisy is not one flower. It is a head called a capitulum. The head "
                "packs many tiny flowers, the florets, onto a shared receptacle. "
                "Involucral bracts wrap the base. Strap-shaped ray florets sit around "
                "the edge. Tubular disc florets fill the centre. Some heads have only "
                "ray florets or only disc florets.",
     "quiz": [
         {"q": "A daisy 'flower' is really",
          "options": ["One large flower", "A head of many tiny florets",
                      "Two fused flowers", "A modified leaf"],
          "answer": "A head of many tiny florets"},
         {"q": "The strap-shaped outer florets are",
          "options": ["Disc florets", "Ray florets", "Bracts", "Sepals"],
          "answer": "Ray florets"},
     ]},
    {"key": "banksia", "name": "Banksia", "italic": True, "family": "Proteaceae",
     "title": "Banksia  ·  Proteaceae",
     "wiki": "https://en.wikipedia.org/wiki/Banksia",
     "special": "A banksia spike is an inflorescence. It carries hundreds to thousands "
                "of flowers arranged in pairs. Each flower has 4 tepals and one long "
                "wiry style. The style tip works as a pollen presenter. It offers "
                "pollen to birds and mammals.",
     "quiz": [
         {"q": "A banksia flower spike is",
          "options": ["A single flower", "An inflorescence of many flowers",
                      "One fused flower", "A cone of leaves"],
          "answer": "An inflorescence of many flowers"},
         {"q": "Each banksia flower has how many tepals",
          "options": ["3", "4", "5", "6"], "answer": "4"},
     ]},
    {"key": "callistemon", "name": "Callistemon", "italic": True,
     "family": "bottlebrush, Myrtaceae",
     "title": "Callistemon  ·  bottlebrush, Myrtaceae",
     "wiki": "https://en.wikipedia.org/wiki/Callistemon",
     "special": "A bottlebrush is a spike of many flowers. The colourful brush is made "
                "of long stamens, not petals. The petals are small. The spike axis "
                "often grows on into a leafy shoot above the brush. Woody fruits sit "
                "along the stem. Some sources place Callistemon in Melaleuca, but the "
                "Atlas of Living Australia keeps it as Callistemon.",
     "quiz": [
         {"q": "The colourful brush of a bottlebrush is made of",
          "options": ["Petals", "Stamens", "Styles", "Bracts"], "answer": "Stamens"},
         {"q": "Above the brush, the spike axis often",
          "options": ["Ends in one flower", "Grows on into a leafy shoot",
                      "Forms a single fruit", "Dies back"],
          "answer": "Grows on into a leafy shoot"},
     ]},
    {"key": "acacia", "name": "Acacia", "italic": True, "family": "wattle, Fabaceae",
     "title": "Acacia  ·  wattle, Fabaceae",
     "wiki": "https://en.wikipedia.org/wiki/Acacia",
     "special": "A wattle flower is tiny. Many are grouped into heads. The heads are "
                "globular balls or short cylindrical spikes. The showy fluffy part is "
                "the stamens. The true petals are small and hard to see.",
     "quiz": [
         {"q": "In a wattle head, the showy fluffy part is the",
          "options": ["Petals", "Stamens", "Sepals", "Bracts"], "answer": "Stamens"},
         {"q": "Wattle flowers are grouped into",
          "options": ["Single large flowers", "Globular or cylindrical heads",
                      "Flat daisy heads", "Long tubes"],
          "answer": "Globular or cylindrical heads"},
     ]},
]

SPECIALS_BY_KEY = {s["key"]: s for s in SPECIALS}


WHY_BRUSH = """
Many Australian flowers advertise with a brush of stamens rather than with
petals. *Eucalyptus*, *Callistemon*, *Melaleuca* and the wattles all do this.
Three forces push in the same direction.

**Pollinators.** Australia has many nectar-feeding birds, such as honeyeaters
and lorikeets. Some plants are even pollinated by possums and gliders. These
visitors are large and strong and not very precise. A sturdy brush of exposed
stamens holds up to a probing bird and dusts pollen onto feathers or fur. It
serves many kinds of insects at the same time. So a brush flower is a robust,
generalist device.

**Poor soils.** Australian soils are ancient and leached. They are low in
phosphorus and nitrogen. Showy petals are costly tissue that the plant grows
and then drops. Stamens do two jobs at once. They are the display and they make
the pollen. Advertising with stamens gives the plant its billboard and its
reproduction from one structure. Packing many small flowers into a spike or a
head does the same trick at a larger scale. One big signal is built from many
cheap parts, with a large pooled reward.

**History.** Myrtaceae and Proteaceae are old, dominant families. They radiated
across the continent as it dried and became fire-prone. The brush plan is close
to ancestral in these groups. Once it was in place it diversified into thousands
of species. So the pattern is partly adaptation and partly which families were
there to adapt.

It is a strong tendency, not a rule. Pea flowers are zygomorphic with showy
petals. Orchids are highly specialised. The showy-stamen habit is the signature
of the sclerophyll families on poor soils with bird and insect pollinators.
"""

