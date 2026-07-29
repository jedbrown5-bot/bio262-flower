"""
fruits.py
---------
Fruit types for the BIO262 dissection tool (Week 3).

Shows how each flower part becomes each fruit part, then steps through the main
fruit types with a labelled cross-section, the key facts, a Wikipedia link and a
short quiz. Colours are matched to the ovary section so students can trace the
ovary wall to the pericarp and the ovule to the seed.

Facts follow standard botany. Australian examples are used where they fit.
"""

import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Ellipse, Wedge, FancyBboxPatch, FancyArrow

INK = "#22463d"
BG = "#f4f8f1"
# colours matched to ovary_section for the flower-to-fruit correspondence
WALL = "#bfe0a8"        # ovary wall  ->  pericarp
WALL_DK = "#5f9146"
SEED = "#f6f2d4"        # ovule  ->  seed
SEED_DK = "#b7a55f"
EMBRYO = "#bcd98f"
PLAC = "#e6a63f"
RECEPT = "#8fae6a"      # receptacle (accessory flesh)
RECEPT_DK = "#5f8f4e"
STYLE = "#8a5aa8"
DRY = "#d3ba86"         # dry pericarp
DRY_DK = "#9c8354"
STONE = "#b6a07a"       # stony endocarp
STONE_DK = "#7c6642"


def _new_ax(title, figsize=(7.2, 5.0), xlim=(0, 10), ylim=(0, 7)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.text(0.2, ylim[1] - 0.3, title, fontsize=15, fontweight="bold", color=INK,
            va="top")
    return fig, ax


def _label(ax, text, xy, xytext, fs=9.5):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, color=INK, ha="center",
                va="center", zorder=25,
                arrowprops=dict(arrowstyle="-", color=INK, lw=1.0),
                bbox=dict(boxstyle="round,pad=0.26", fc="white", ec=INK, lw=1.0))


def _seed(ax, cx, cy, rx=0.5, ry=0.7, z=6, embryo=True):
    ax.add_patch(Ellipse((cx, cy), rx * 2, ry * 2, facecolor=SEED, edgecolor=SEED_DK,
                 linewidth=1.6, zorder=z))
    if embryo:
        ax.add_patch(Ellipse((cx, cy), rx * 1.1, ry * 1.3, facecolor=EMBRYO,
                     edgecolor="#8fae5a", linewidth=1.0, zorder=z + 0.1))


# ----------------------------------------------------------------------
def draw_overview():
    fig, ax = _new_ax("How flower parts become fruit parts", figsize=(8.4, 4.8),
                      xlim=(0, 14), ylim=(0, 7))
    # --- left: ovary (long section) ---
    ax.text(2.4, 6.0, "Ovary", fontsize=12, fontweight="bold", color=INK, ha="center")
    ax.add_patch(Ellipse((2.4, 3.1), 2.6, 3.4, facecolor=WALL, edgecolor=WALL_DK,
                 linewidth=3, zorder=2))
    ax.add_patch(Ellipse((2.4, 3.1), 1.7, 2.5, facecolor="#eef7e6", edgecolor="none",
                 zorder=3))
    _seed(ax, 2.4, 3.1, 0.42, 0.62, z=4, embryo=False)
    _label(ax, "Ovary wall", (1.15, 3.6), (0.9, 5.6))
    _label(ax, "Ovule", (2.4, 3.1), (4.1, 4.7))

    # --- arrow ---
    ax.add_patch(FancyArrow(5.4, 3.1, 1.5, 0, width=0.12, head_width=0.5,
                 head_length=0.5, facecolor=INK, edgecolor="none", zorder=5))
    ax.text(6.15, 3.7, "ripens into", fontsize=9, color=INK, ha="center",
            fontstyle="italic")

    # --- right: fruit (long section) with pericarp layers ---
    ax.text(10.4, 6.4, "Fruit", fontsize=12, fontweight="bold", color=INK, ha="center")
    ax.add_patch(Ellipse((10.4, 3.1), 4.2, 4.6, facecolor="#e7b98f",
                 edgecolor="#c0532f", linewidth=1.2, zorder=2))          # exocarp skin
    ax.add_patch(Ellipse((10.4, 3.1), 3.8, 4.2, facecolor=WALL, edgecolor="none",
                 zorder=2.1))                                            # mesocarp
    ax.add_patch(Ellipse((10.4, 3.1), 1.9, 2.6, facecolor=STONE, edgecolor=STONE_DK,
                 linewidth=1.4, zorder=2.2))                             # endocarp
    _seed(ax, 10.4, 3.1, 0.6, 0.95, z=4, embryo=False)
    # persistent style point
    ax.plot([10.4, 10.4], [5.35, 6.0], color=STYLE, lw=2.4, zorder=3)
    _label(ax, "Exocarp (skin)", (12.3, 4.2), (12.7, 6.0))
    _label(ax, "Mesocarp (flesh)", (11.9, 3.1), (13.3, 3.1))
    _label(ax, "Endocarp", (9.55, 3.9), (8.3, 5.7))
    _label(ax, "Seed", (10.4, 3.1), (8.0, 3.0))
    _label(ax, "Style remnant", (10.4, 5.7), (12.2, 6.5))
    ax.text(7.0, 0.3, "A simplified view. Some structures, including the seed's "
            "internal parts, are not shown.", fontsize=9.5, color=INK,
            ha="center", fontstyle="italic")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    return fig


# ----------------------------------------------------------------------
def _draw_drupe(ax):
    cx, cy = 5.0, 3.4
    ax.add_patch(Ellipse((cx, cy), 5.2, 5.0, facecolor="#e7b98f", edgecolor="#c0532f",
                 linewidth=2, zorder=2))
    ax.add_patch(Ellipse((cx, cy), 4.7, 4.5, facecolor="#f2c98f", edgecolor="none",
                 zorder=2.1))
    ax.add_patch(Ellipse((cx, cy), 2.3, 2.7, facecolor=STONE, edgecolor=STONE_DK,
                 linewidth=2, zorder=2.2))
    _seed(ax, cx, cy, 0.6, 0.95, embryo=False)
    _label(ax, "Exocarp (skin)", (cx + 2.4, cy + 1.0), (8.4, 6.0))
    _label(ax, "Mesocarp (flesh)", (cx + 1.6, cy), (8.6, 3.4))
    _label(ax, "Endocarp (stone)", (cx, cy + 1.3), (1.9, 6.1))
    _label(ax, "Seed", (cx, cy), (1.4, 2.4))


def _draw_berry(ax):
    cx, cy = 5.0, 3.3
    ax.add_patch(Circle((cx, cy), 2.5, facecolor="#d34b3a", edgecolor="#a5331f",
                 linewidth=2, zorder=2))
    ax.add_patch(Circle((cx, cy), 2.3, facecolor="#e86a55", edgecolor="none",
                 zorder=2.1))
    for a in np.linspace(0, 360, 8, endpoint=False):
        r = math.radians(a)
        _seed(ax, cx + 1.15 * math.cos(r), cy + 1.15 * math.sin(r), 0.22, 0.3,
              embryo=False)
    _label(ax, "Skin (exocarp)", (cx + 2.4, cy + 0.7), (8.6, 5.7))
    _label(ax, "Fleshy pericarp\n(all soft)", (cx + 1.7, cy - 0.6), (8.7, 2.6))
    _label(ax, "Seeds", (cx + 1.15, cy + 1.15), (2.0, 6.0))


def _draw_pome(ax):
    cx, cy = 5.0, 3.4
    ax.add_patch(Circle((cx, cy), 2.6, facecolor=RECEPT, edgecolor=RECEPT_DK,
                 linewidth=2, zorder=2))                    # receptacle flesh
    ax.add_patch(Circle((cx, cy), 2.4, facecolor="#b7d69a", edgecolor="none",
                 zorder=2.1))
    ax.add_patch(Ellipse((cx, cy), 1.7, 2.2, facecolor="#f4f9ee", edgecolor="#cbb98a",
                 linewidth=1.6, zorder=3))                  # core (ovary), papery
    for s in (-1, 1):
        _seed(ax, cx + s * 0.4, cy, 0.22, 0.4, embryo=False)
    for s in (-1, 1):
        ax.add_patch(Polygon([(cx + s * 0.4, 0.9), (cx + s * 0.8, 0.6),
                     (cx + s * 0.5, 1.3)], closed=True, facecolor="#7aae5c",
                     edgecolor=RECEPT_DK, lw=1, zorder=3))
    _label(ax, "Flesh = receptacle\n/ floral tube", (cx + 2.2, cy + 0.6), (8.7, 5.6))
    _label(ax, "Core = ovary", (cx, cy + 1.0), (1.7, 6.0))
    _label(ax, "Pips (seeds)", (cx + 0.4, cy), (8.7, 2.6))
    _label(ax, "Old sepals", (cx + 0.6, 1.0), (1.5, 1.2))


_DRAW = {
    "drupe": _draw_drupe, "berry": _draw_berry, "pome": _draw_pome,
}


def draw_fruit(key):
    entry = FRUITS_BY_KEY[key]
    fig, ax = _new_ax(entry["title"])
    _DRAW[key](ax)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    return fig


# ----------------------------------------------------------------------
OVERVIEW_TEXT = """
After fertilisation most of the flower withers, but a few parts persist and ripen
into the fruit.

**Ovary wall becomes the pericarp**, the fruit wall. It can form three layers. The
outer **exocarp** is the skin. The middle **mesocarp** is often the flesh we eat.
The inner **endocarp** lines the seed chamber. In a peach these layers are clear.
Skin, flesh, then a stony endocarp around the seed.

**Each ovule becomes a seed.** Its integuments become the seed coat (the testa).
The fertilised egg becomes the embryo. The fertilised central cell becomes the
endosperm, the seed's food store.

**Petals, stamens, style and stigma usually dry and fall.** The dried style often
leaves a small point at the tip. The sepals often persist, like the papery star on
a tomato or the crown on an apple.

**True versus accessory.** In a true fruit the flesh is all ovary. In an accessory
fruit another part, often the receptacle, swells to make the flesh. An apple and a
strawberry are accessory fruits.
"""

WIKI = "https://en.wikipedia.org/wiki/"

FRUITS = [
    {"key": "drupe", "name": "Drupe", "group": "Fleshy", "title": "Drupe  ·  a stone fruit",
     "wiki": WIKI + "Drupe",
     "text": "A drupe is a fleshy fruit with a single stony seed inside. The ovary "
             "wall becomes the pericarp in three layers. The skin is the exocarp. The "
             "juicy flesh is the mesocarp. A hard stony endocarp forms a stone around "
             "the seed. Peaches, plums, olives and mangoes are drupes. The native "
             "quandong (*Santalum acuminatum*) is a drupe.",
     "quiz": [
         {"q": "In a drupe, the hard stone around the seed is the",
          "options": ["Exocarp", "Mesocarp", "Endocarp", "Testa"], "answer": "Endocarp"},
         {"q": "The juicy flesh of a peach is the",
          "options": ["Exocarp", "Mesocarp", "Endocarp", "Receptacle"],
          "answer": "Mesocarp"}]},
    {"key": "berry", "name": "Berry", "group": "Fleshy", "title": "Berry  ·  fleshy throughout",
     "wiki": WIKI + "Berry_(botany)",
     "text": "A berry is a fleshy fruit where the whole pericarp stays soft. There is "
             "no stone. One or many seeds sit in the flesh. Tomatoes, grapes, "
             "kiwifruit and bananas are berries. The native lilly pilly (*Syzygium*) "
             "makes berries.",
     "quiz": [
         {"q": "A tomato is a",
          "options": ["Drupe", "Berry", "Pome", "Capsule"], "answer": "Berry"},
         {"q": "In a berry the pericarp is",
          "options": ["Dry", "Fleshy throughout", "Stony inside", "Winged"],
          "answer": "Fleshy throughout"}]},
    {"key": "pome", "name": "Pome", "group": "Fleshy (accessory)", "title": "Pome  ·  an accessory fruit",
     "wiki": WIKI + "Pome",
     "text": "A pome is an accessory fruit. Most of the flesh is not the ovary. It is "
             "the swollen receptacle or floral tube growing around the ovary. The true "
             "ovary is the papery core around the pips. Apples and pears are pomes. The "
             "crown at the base of an apple is the old sepals and stamens.",
     "quiz": [
         {"q": "The flesh you eat in an apple is mostly the",
          "options": ["Ovary wall", "Receptacle / floral tube", "Seed", "Endocarp"],
          "answer": "Receptacle / floral tube"},
         {"q": "The papery core of an apple is the",
          "options": ["Receptacle", "Ovary", "Calyx", "Style"], "answer": "Ovary"}]},
]

FRUITS_BY_KEY = {fr["key"]: fr for fr in FRUITS}
