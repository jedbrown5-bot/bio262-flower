"""
ovary_section.py
----------------
A transverse (cross) section of the ovary for the BIO262 dissection game.

The inside of the ovary is where placentation lives, and it cannot be seen on
the whole flower. This module draws a clean cut-through showing the ovary wall,
the locules (chambers), the septa, the placenta and the ovules, driven by the
flower's carpel number, carpel fusion and placentation type.

    from flower_core import make_flower
    from ovary_section import cross_section
    fig, hotspots, answer, explain, names = cross_section(make_flower())
"""

import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Ellipse, Polygon

WALL = "#bfe0a8"
WALL_DK = "#5f9146"
CAVITY = "#f5faef"
SEPTUM = "#7db35f"
PLAC = "#e6a63f"
PLAC_DK = "#b5791f"
OVULE = "#f6f2d4"
OVULE_DK = "#b7a55f"
INK = "#22463d"

RW = 1.0                      # ovary wall radius
RI = 0.86                     # inner cavity radius


def _ovule(ax, x, y, r=0.075, z=6):
    ax.add_patch(Ellipse((x, y), r * 2, r * 2.5, facecolor=OVULE,
                 edgecolor=OVULE_DK, linewidth=1.0, zorder=z))


_NAMED = False    # when True, cross_section labels with part names instead of numbers


def _leader(ax, anchor, angle_deg, num, hotspots, name, rlab=1.42):
    """Draw a marker at rlab and a leader line back to the anchor."""
    rl = 1.62 if _NAMED else rlab
    lx = rl * math.cos(math.radians(angle_deg))
    ly = rl * math.sin(math.radians(angle_deg))
    ax.plot([anchor[0], lx], [anchor[1], ly], color="#3a4a42", linewidth=1.1,
            zorder=8)
    ax.add_patch(Circle(anchor, 0.02, facecolor="#3a4a42", edgecolor="none", zorder=8))
    if _NAMED:
        ax.text(lx, ly, name, ha="center", va="center", color=INK, fontsize=12,
                fontweight="bold", zorder=10,
                bbox=dict(boxstyle="round,pad=0.28", fc="white", ec=INK, lw=1.3))
    else:
        ax.add_patch(Circle((lx, ly), 0.14, facecolor=INK, edgecolor="white",
                     linewidth=1.5, zorder=9))
        ax.text(lx, ly, str(num), ha="center", va="center", color="white",
                fontsize=11, fontweight="bold", zorder=10)
    hotspots.append({"num": num, "name": name})


def cross_section(f, figsize=(5.6, 5.6), named=False):
    """Return (fig, hotspots, answer, explain, names).

    named=True labels the parts with their names (for the glossary) instead of
    numbers (for the game).
    """
    global _NAMED
    _NAMED = named
    plac = f.get("placentation", "axile")
    carpels = max(1, f["carpels"])

    lim = 2.35 if named else 1.75
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("#f4f8f1")
    ax.set_facecolor("#f4f8f1")

    # ovary wall (pericarp) and inner cavity
    ax.add_patch(Circle((0, 0), RW, facecolor=WALL, edgecolor=WALL_DK,
                 linewidth=3, zorder=1))
    ax.add_patch(Circle((0, 0), RI, facecolor=CAVITY, edgecolor="none", zorder=2))

    hotspots = []
    num = [0]

    def nxt():
        num[0] += 1
        return num[0]

    # ---- placentation specific interior ----
    if plac == "axile":
        locules = carpels
        # septa radiating from the centre
        sep_anchor = None
        for i in range(carpels):
            ang = 90 + i * 360.0 / carpels
            ex, ey = RI * math.cos(math.radians(ang)), RI * math.sin(math.radians(ang))
            ax.plot([0, ex], [0, ey], color=SEPTUM, linewidth=4, zorder=3,
                    solid_capstyle="round")
            if i == 0:
                mid = math.radians(ang)
                sep_anchor = (0.5 * math.cos(mid), 0.5 * math.sin(mid))
        # central placenta column
        ax.add_patch(Circle((0, 0), 0.14, facecolor=PLAC, edgecolor=PLAC_DK,
                     linewidth=1.5, zorder=5))
        # ovules: two per locule, attached to the central axis
        ov_anchor = None
        loc_anchor = None
        for i in range(carpels):
            mid = math.radians(90 + (i + 0.5) * 360.0 / carpels)
            for s in (-1, 1):
                a = mid + s * 0.28
                ox, oy = 0.32 * math.cos(a), 0.32 * math.sin(a)
                ax.plot([0.05 * math.cos(a), ox], [0.05 * math.sin(a), oy],
                        color=PLAC_DK, linewidth=0.8, zorder=5)
                _ovule(ax, ox, oy)
                if ov_anchor is None:
                    ov_anchor = (ox, oy)
            if loc_anchor is None:
                loc_anchor = (0.62 * math.cos(mid), 0.62 * math.sin(mid))
        _leader(ax, (0, RW), 90, nxt(), hotspots, "Ovary wall")
        _leader(ax, sep_anchor, 150, nxt(), hotspots, "Septum")
        _leader(ax, loc_anchor, 25, nxt(), hotspots, "Locule")
        _leader(ax, (0, 0), 300, nxt(), hotspots, "Placenta")
        _leader(ax, ov_anchor, 210, nxt(), hotspots, "Ovule")
        names = ["Ovary wall", "Septum", "Locule", "Placenta", "Ovule"]
        explain = (f"Axile placentation. The septa meet in the centre and the ovules "
                   f"attach to the central axis. One locule per carpel, so "
                   f"{carpels} locules.")

    elif plac == "parietal":
        locules = 1
        n = max(2, carpels)
        ov_anchor = plac_anchor = None
        for i in range(n):
            ang = math.radians(90 + i * 360.0 / n)
            px, py = RI * math.cos(ang), RI * math.sin(ang)
            ax.add_patch(Circle((px, py), 0.09, facecolor=PLAC, edgecolor=PLAC_DK,
                         linewidth=1.2, zorder=5))
            for s in (-1, 1):
                a = ang + s * 0.22
                ox, oy = (RI - 0.16) * math.cos(a), (RI - 0.16) * math.sin(a)
                _ovule(ax, ox, oy)
                if ov_anchor is None:
                    ov_anchor = (ox, oy)
            if plac_anchor is None:
                plac_anchor = (px, py)
        _leader(ax, (0, RW), 90, nxt(), hotspots, "Ovary wall")
        _leader(ax, (0, 0), 150, nxt(), hotspots, "Locule")
        _leader(ax, plac_anchor, 30, nxt(), hotspots, "Placenta")
        _leader(ax, ov_anchor, 250, nxt(), hotspots, "Ovule")
        names = ["Ovary wall", "Locule", "Placenta", "Ovule"]
        explain = ("Parietal placentation. The carpel margins fuse to the ovary "
                   "wall, so the ovules sit on the wall in a single locule.")

    elif plac == "free-central":
        locules = 1
        ax.add_patch(Circle((0, 0), 0.2, facecolor=PLAC, edgecolor=PLAC_DK,
                     linewidth=1.5, zorder=5))
        ov_anchor = None
        for i in range(max(6, carpels * 2)):
            a = i * 2 * math.pi / max(6, carpels * 2)
            ox, oy = 0.42 * math.cos(a), 0.42 * math.sin(a)
            ax.plot([0.2 * math.cos(a), ox], [0.2 * math.sin(a), oy],
                    color=PLAC_DK, linewidth=0.8, zorder=5)
            _ovule(ax, ox, oy)
            if ov_anchor is None:
                ov_anchor = (ox, oy)
        _leader(ax, (0, RW), 90, nxt(), hotspots, "Ovary wall")
        _leader(ax, (0.62, 0.62), 40, nxt(), hotspots, "Locule")
        _leader(ax, (0, 0), 270, nxt(), hotspots, "Central column")
        _leader(ax, ov_anchor, 200, nxt(), hotspots, "Ovule")
        names = ["Ovary wall", "Locule", "Central column", "Ovule"]
        explain = ("Free-central placentation. Ovules sit on a central column in a "
                   "single locule, with no septa.")

    else:  # marginal, one carpel of an apocarpous gynoecium
        locules = 1
        # ventral suture on the right where the margins meet
        sx, sy = RI, 0.0
        ax.add_patch(Circle((sx, sy), 0.1, facecolor=PLAC, edgecolor=PLAC_DK,
                     linewidth=1.3, zorder=5))
        ov_anchor = None
        for oy in np.linspace(-0.45, 0.45, 4):
            ox = 0.55
            ax.plot([RI - 0.02, ox], [oy * 0.6, oy], color=PLAC_DK,
                    linewidth=0.8, zorder=5)
            _ovule(ax, ox, oy)
            if ov_anchor is None:
                ov_anchor = (ox, oy)
        _leader(ax, (0, RW), 110, nxt(), hotspots, "Carpel wall")
        _leader(ax, (-0.4, 0.0), 180, nxt(), hotspots, "Locule")
        _leader(ax, (sx, sy), 340, nxt(), hotspots, "Placenta")
        _leader(ax, ov_anchor, 285, nxt(), hotspots, "Ovule")
        names = ["Carpel wall", "Locule", "Placenta", "Ovule"]
        explain = (f"Marginal placentation. A single carpel with ovules along the "
                   f"fused margins (the ventral suture). This gynoecium has "
                   f"{carpels} separate carpels (apocarpous).")

    answer = {"locules": locules, "placentation": plac,
              "compound": f["carpel_fusion"] == "fused"}
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    return fig, hotspots, answer, explain, names


PLACENTATION_CHOICES = ["axile", "parietal", "free-central", "marginal"]
