"""
flower_core.py
--------------
Model, randomiser and matplotlib renderer for the BIO262 flower dissection game.

This module has NO Streamlit dependency, so it can be imported and test-rendered
on its own:

    from flower_core import make_flower, draw_flower
    fig, hotspots = draw_flower(make_flower())
    fig.savefig("test.png")

The flower is drawn as a side / cutaway elevation. The reproductive parts sit in
the centre with the ovary at the base and the stigma on top, and the sepals,
petals and stamens fan out to the sides so their number is still countable.
"""

import math
import random

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon, Ellipse, Circle, FancyBboxPatch

# ----------------------------------------------------------------------
# Palettes
# ----------------------------------------------------------------------
PETAL_COLORS = [
    ("pink",   "#e97ba8", "#c85f8b", "#f6b8d0"),
    ("purple", "#a86fd0", "#8850b3", "#c9aae6"),
    ("yellow", "#f2cf4d", "#d3ac2a", "#fae89a"),
    ("white",  "#f4f4ee", "#b9bcac", "#ffffff"),
    ("red",    "#d9533f", "#b23a29", "#f0a493"),
    ("orange", "#ef9b45", "#cf7c28", "#f8c78f"),
    ("blue",   "#6f8fe0", "#4f6ec2", "#a9bef0"),
    ("cream",  "#f0e4bf", "#c9b784", "#f7efd6"),
]
SEPAL_COLORS = [
    ("#7aae5c", "#4f7d3a"),
    ("#8bbf6e", "#5f9146"),
    ("#6fa552", "#4a7534"),
]
STEM = "#5f8f4e"
STEM_DK = "#436b37"
FILAMENT = "#e7e0bf"
FILAMENT_DK = "#c9bf90"

# ----------------------------------------------------------------------
# Model + randomiser
# ----------------------------------------------------------------------
def make_flower(rng=None):
    """Return a dict describing a random generic flower."""
    r = rng or random
    merosity = r.choice([3, 3, 4, 5, 5, 5, 6])
    symmetry = r.choice(["radial", "radial", "bilateral"])
    petal_fusion = r.choice(["free", "free", "fused"])
    carpel_fusion = r.choice(["free", "fused", "fused"])

    sepals = merosity
    petals = merosity
    stamens = r.choice([merosity, merosity, 2 * merosity])
    if carpel_fusion == "fused":
        carpels = r.choice([1, 2, 3, 3, merosity])
    else:
        carpels = r.choice([merosity, 2, 3, 3])

    # placentation: how the ovules are arranged inside the ovary
    if carpel_fusion == "free":
        placentation = "marginal"          # a simple carpel, ovules on the suture
    elif carpels == 1:
        placentation = r.choice(["parietal", "free-central"])
    else:
        placentation = r.choice(["axile", "axile", "parietal", "free-central"])

    pc = r.choice(PETAL_COLORS)
    sc = r.choice(SEPAL_COLORS)
    return {
        "merosity": merosity,
        "symmetry": symmetry,
        "petal_fusion": petal_fusion,
        "carpel_fusion": carpel_fusion,
        "sepals": sepals,
        "petals": petals,
        "stamens": stamens,
        "carpels": carpels,
        "placentation": placentation,
        "petal_name": pc[0],
        "petal_fill": pc[1],
        "petal_edge": pc[2],
        "petal_hi": pc[3],
        "sepal_fill": sc[0],
        "sepal_edge": sc[1],
        "anther": r.choice(["#e8c14a", "#eaa73f", "#d8b32e"]),
        "stigma": r.choice(["#c257c9", "#b13fbe", "#a24fce"]),
        "scale": r.uniform(0.9, 1.1),
    }


def floral_formula(f):
    sym = "⊕" if f["symmetry"] == "radial" else "↓"  # radial / bilateral glyph
    C = f"({f['petals']})" if f["petal_fusion"] == "fused" else f"{f['petals']}"
    G = f"({f['carpels']})" if f["carpel_fusion"] == "fused" else f"{f['carpels']}"
    return f"{sym}  K{f['sepals']}  C{C}  A{f['stamens']}  G{G}"


def traits_text(f):
    sym = "actinomorphic (radial)" if f["symmetry"] == "radial" else "zygomorphic (bilateral)"
    cor = "sympetalous (fused petals)" if f["petal_fusion"] == "fused" else "free petals"
    gyn = "syncarpous (fused carpels)" if f["carpel_fusion"] == "fused" else "apocarpous (free carpels)"
    return (f"Symmetry {sym}. Merosity {f['merosity']}-merous. "
            f"Corolla {cor}. Gynoecium {gyn}.")


# ----------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------
def _cubic(p0, p1, p2, p3, n=24):
    t = np.linspace(0, 1, n).reshape(-1, 1)
    p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 \
        + 3 * (1 - t) * t ** 2 * p2 + (t ** 3) * p3


def _petal_outline(length, width, tip=0.22, waist=0.62):
    """Curved, tapered petal pointing up (+y), base at origin, symmetric about x=0."""
    tw = width * tip           # half tip width (0 -> pointed)
    left = _cubic((0, 0),
                  (-width, length * 0.18),
                  (-width * waist, length * 0.82),
                  (-tw, length))
    top = _cubic((-tw, length),
                 (-tw * 0.6, length * 1.05),
                 (tw * 0.6, length * 1.05),
                 (tw, length), n=10)
    right = _cubic((tw, length),
                   (width * waist, length * 0.82),
                   (width, length * 0.18),
                   (0, 0))
    return np.vstack([left, top, right])


def _rotate_translate(pts, phi_deg, ox, oy):
    """Rotate a shape pointing +y by phi degrees (positive -> tilt right), then move base to (ox,oy)."""
    a = math.radians(phi_deg)
    ca, sa = math.cos(a), math.sin(a)
    x = pts[:, 0] * ca + pts[:, 1] * sa
    y = -pts[:, 0] * sa + pts[:, 1] * ca
    return np.column_stack([x + ox, y + oy])


def _fan_angles(n, spread):
    if n == 1:
        return [0.0]
    return list(np.linspace(-spread / 2, spread / 2, n))


def _fill_shape(ax, verts, fill, edge, z, lw=1.6, hi=None, alpha=1.0):
    poly = Polygon(verts, closed=True, facecolor=fill, edgecolor=edge,
                   linewidth=lw, zorder=z, joinstyle="round", alpha=alpha)
    ax.add_patch(poly)
    if hi is not None:
        # soft inner highlight for a little depth
        c = verts.mean(axis=0)
        inner = (verts - c) * 0.55 + c
        ax.add_patch(Polygon(inner, closed=True, facecolor=hi, edgecolor="none",
                             zorder=z + 0.1, alpha=0.45))
    return poly


# ----------------------------------------------------------------------
# Renderer
# ----------------------------------------------------------------------
WHORL_ORDER = ["calyx", "corolla", "androecium", "gynoecium"]
WHORL_LABEL = {
    "calyx": "Calyx (sepals)",
    "corolla": "Corolla (petals)",
    "androecium": "Androecium (stamens)",
    "gynoecium": "Gynoecium (carpels)",
}


def _project(P, cE, sE, YC):
    x, y, z = P
    return x, z * cE - y * sE + YC, y * cE + z * sE     # screen_x, screen_y, depth


def draw_flower(f, removed=None, highlight=None, show_numbers=False,
                cutaway=True, figsize=(6.4, 7.0), spin=0.0):
    """
    Draw the flower as a pseudo-3D bloom that can be spun around the stem.

    spin      : degrees to rotate the flower about the vertical stem axis.
                Rotating brings hidden sepals (and back parts) into view.
    removed   : set of whorl names not to draw (peel mode)
    highlight : whorl name to keep vivid while others dim (peel mode)
    show_numbers : place numbered markers on one of each part kind (label mode)

    Returns (fig, hotspots). hotspots: {part, name, x, y, num} in data coords.
    """
    removed = removed or set()
    S = f["scale"]
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(-9, 9)
    ax.set_ylim(-7, 10.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("#f4f8f1")
    ax.set_facecolor("#f4f8f1")

    E = math.radians(22.0)          # camera looks down by this angle
    cE, sE = math.cos(E), math.sin(E)
    Z0 = 0.6                         # height on the stem where whorls attach
    YC = 0.4                         # screen vertical offset of the receptacle
    spin_r = math.radians(spin)

    def proj(P):
        return _project(P, cE, sE, YC)

    def mdir(phi_deg, psi_deg):
        phi = math.radians(phi_deg) + spin_r
        psi = math.radians(psi_deg)
        return (math.cos(psi) * math.cos(phi),
                math.cos(psi) * math.sin(phi),
                math.sin(psi))

    elements = []                    # (depth, draw_fn) collected then z-sorted
    hotspots = []
    seen = set()
    cnt = [0]

    def add_hotspot(part, name, x, y):
        if part in seen:
            return
        seen.add(part)
        cnt[0] += 1
        hotspots.append({"part": part, "name": name, "x": x, "y": y, "num": cnt[0]})

    def dimf(w):
        return 0.22 if (highlight and w != highlight and w != "stem") else 1.0

    # ---- stem + receptacle (behind everything, fixed) ----
    a = dimf("stem")
    scx, scy, _ = proj((0, 0, Z0))
    elements.append((-99, lambda z, a=a: ax.add_patch(FancyBboxPatch(
        (-0.55, -7), 1.1, 7 + scy,
        boxstyle="round,pad=0.02,rounding_size=0.4", facecolor=STEM,
        edgecolor=STEM_DK, linewidth=1.4, zorder=z, alpha=a))))
    elements.append((-98, lambda z, a=a: ax.add_patch(Ellipse(
        (scx, scy), 3.4 * S, 1.7 * S, facecolor=STEM, edgecolor=STEM_DK,
        linewidth=1.4, zorder=z, alpha=a))))
    add_hotspot("receptacle", "Receptacle", scx, scy)

    # ---- a blade (sepal / petal): 2D outline placed and foreshortened in 3D ----
    def add_blade(phi, psi, length, width, fill, edge, whorl, hi=None):
        d = mdir(phi, psi)
        bsx, bsy, bd = proj((0, 0, Z0))
        tsx, tsy, td = proj((d[0] * length, d[1] * length, Z0 + d[2] * length))
        dx, dy = tsx - bsx, tsy - bsy
        slen = max(1e-3, math.hypot(dx, dy))
        phi_s = math.degrees(math.atan2(dx, dy))
        scale = slen / length
        w = width * (0.5 + 0.5 * scale)
        verts = _petal_outline(slen, w,
                               tip=0.30 if whorl == "corolla" else 0.05,
                               waist=0.6 if whorl == "corolla" else 0.5)
        verts = _rotate_translate(verts, phi_s, bsx, bsy)
        a = dimf(whorl)
        elements.append((td, lambda z, v=verts, fl=fill, ed=edge, a=a, hi=hi:
                         _fill_shape(ax, v, fl, ed, z=z, lw=1.6, hi=hi, alpha=a)))
        return bsx, bsy, tsx, tsy, td, scale

    halfstep = 180.0 / max(1, f["petals"])

    # ---- calyx (sepals) : nearly horizontal, offset between the petals ----
    if "calyx" not in removed:
        best = None
        for i in range(f["sepals"]):
            phi = i * 360.0 / f["sepals"] + halfstep
            r = add_blade(phi, 10, 5.9 * S, 2.0 * S,
                          f["sepal_fill"], f["sepal_edge"], "calyx")
            # remember the sepal facing most toward the viewer for the hotspot
            if best is None or r[4] > best[0]:
                best = (r[4], r[2], r[3])
        if best:
            add_hotspot("sepal", "Sepal", best[1], best[2])

    # ---- corolla (petals) ----
    if "corolla" not in removed:
        # fused corolla: a filled disc at the centre that unites the petal bases
        if f["petal_fusion"] == "fused":
            cx0, cy0, _ = proj((0, 0, Z0 + 1.0))
            elements.append((-5, lambda z, a=dimf("corolla"): ax.add_patch(Ellipse(
                (cx0, cy0 + 1.2 * S), 6.2 * S, (6.2 * S) * (cE + 0.15),
                facecolor=f["petal_fill"], edgecolor=f["petal_edge"],
                linewidth=1.6, zorder=z, alpha=a))))
        best = None
        for i in range(f["petals"]):
            phi = i * 360.0 / f["petals"]
            psi = 34
            if f["symmetry"] == "bilateral":
                psi = 34 + 14 * math.cos(math.radians(phi))
            r = add_blade(phi, psi, 7.3 * S, 2.85 * S,
                          f["petal_fill"], f["petal_edge"], "corolla",
                          hi=f["petal_hi"])
            if best is None or r[4] > best[0]:
                mx = (r[0] + r[2]) / 2
                my = (r[1] + r[3]) / 2
                best = (r[4], mx, my)
        if best:
            add_hotspot("petal", "Petal", best[1], best[2])

    # ---- androecium (stamens) : filament + anther ----
    if "androecium" not in removed:
        a = dimf("androecium")
        best_fil = best_ant = None
        for i in range(f["stamens"]):
            phi = i * 360.0 / f["stamens"] + halfstep / 2
            psi = 60
            d = mdir(phi, psi)
            length = 5.2 * S
            bsx, bsy, bd = proj((0, 0, Z0 + 0.3))
            tsx, tsy, td = proj((d[0] * length, d[1] * length, Z0 + 0.3 + d[2] * length))
            ang = math.degrees(math.atan2(tsx - bsx, tsy - bsy))
            elements.append(((bd + td) / 2, lambda z, x1=bsx, y1=bsy, x2=tsx, y2=tsy, a=a:
                             ax.plot([x1, x2], [y1, y2], color=FILAMENT,
                                     linewidth=3.0 * S, solid_capstyle="round",
                                     zorder=z, alpha=a)))
            elements.append((td + 0.01, lambda z, xx=tsx, yy=tsy, ang=ang, a=a:
                             ax.add_patch(Ellipse((xx, yy), 1.0 * S, 1.7 * S,
                                          angle=-ang, facecolor=f["anther"],
                                          edgecolor="#9c7d1c", linewidth=1.1,
                                          zorder=z, alpha=a))))
            if best_fil is None or (bd + td) / 2 > best_fil[0]:
                best_fil = ((bd + td) / 2, (bsx + tsx) / 2, (bsy + tsy) / 2)
            if best_ant is None or td > best_ant[0]:
                best_ant = (td, tsx, tsy)
        if best_fil:
            add_hotspot("filament", "Filament", best_fil[1], best_fil[2])
        if best_ant:
            add_hotspot("anther", "Anther", best_ant[1], best_ant[2])

    # ---- gynoecium (pistil) ----
    if "gynoecium" not in removed:
        a = dimf("gynoecium")
        stig, stig_edge, stig_hi = f["stigma"], "#5f2f78", "#f2d3f7"

        def draw_one_pistil(cx3, cy3, ov_w, ov_h, lobes, locules=1, sc=1.0, depth=0.0):
            ocx, ocy, od = proj((cx3, cy3, Z0 + 1.6 * sc))
            def body(z, a=a):
                ax.add_patch(Ellipse((ocx, ocy), ov_w, ov_h, facecolor="#cdeabd",
                             edgecolor="#5f9146", linewidth=2.0, zorder=z, alpha=a))
                if cutaway and locules > 1:
                    edges = np.linspace(-ov_w / 2, ov_w / 2, locules + 1)
                    for xd in edges[1:-1]:
                        yy = ov_h / 2 * math.sqrt(max(0.0, 1 - (xd / (ov_w / 2)) ** 2))
                        ax.plot([ocx + xd, ocx + xd], [ocy - yy * 0.9, ocy + yy * 0.9],
                                color="#5f9146", linewidth=1.4, zorder=z + 0.01, alpha=a)
                    for ci in range(locules):
                        xc = ocx + (edges[ci] + edges[ci + 1]) / 2
                        ax.add_patch(Circle((xc, ocy), 0.24 * S, facecolor="#f6f2d4",
                                     edgecolor="#b7a55f", linewidth=0.8,
                                     zorder=z + 0.02, alpha=a))
                elif cutaway:
                    for oy in np.linspace(ocy - ov_h * 0.26, ocy + ov_h * 0.26, 2):
                        for ox2 in (-ov_w * 0.2, ov_w * 0.2):
                            ax.add_patch(Circle((ocx + ox2, oy), 0.2 * S * sc,
                                         facecolor="#f6f2d4", edgecolor="#b7a55f",
                                         linewidth=0.8, zorder=z + 0.02, alpha=a))
            elements.append((depth, body))
            # style + stigma rise vertically from the ovary top
            styc_x, styc_y, _ = proj((cx3, cy3, Z0 + 1.6 * sc + ov_h * 0.02))
            top_x, top_y, _ = proj((cx3, cy3, Z0 + 1.6 * sc + (3.4) * S * sc))
            head_y = top_y + 0.35 * S * sc
            if lobes == 1:
                lw_e, lh_e = 1.9 * S * sc, 1.5 * S * sc
                centers = [(top_x, head_y)]
            else:
                step = 0.78 * S
                lw_e, lh_e = 1.28 * S, 1.2 * S
                centers = [(top_x + (lb - (lobes - 1) / 2) * step, head_y)
                           for lb in range(lobes)]
            def stylefn(z, a=a):
                ax.plot([ocx, top_x], [ocy + ov_h * 0.42, head_y], color="#9fce86",
                        linewidth=3.4 * S * sc, solid_capstyle="round", zorder=z, alpha=a)
                for (cxp, cyp) in centers:
                    ax.add_patch(Ellipse((cxp, cyp), lw_e, lh_e, facecolor=stig,
                                 edgecolor=stig_edge, linewidth=1.8, zorder=z + 0.02, alpha=a))
                    ax.add_patch(Ellipse((cxp - lw_e * 0.12, cyp + lh_e * 0.12),
                                 lw_e * 0.45, lh_e * 0.4, facecolor=stig_hi,
                                 edgecolor="none", zorder=z + 0.03, alpha=a * 0.6))
                    for ang in range(20, 360, 60):
                        dxx, dyy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                        ax.plot([cxp + dxx * lw_e * 0.4, cxp + dxx * lw_e * 0.62],
                                [cyp + dyy * lh_e * 0.42, cyp + dyy * lh_e * 0.66],
                                color=stig_edge, linewidth=0.8, zorder=z + 0.04, alpha=a * 0.7)
            elements.append((depth + 5.0, stylefn))     # style/stigma always in front of its ovary
            return ocx, ocy, head_y, lh_e

        if f["carpel_fusion"] == "fused":
            lobes = min(max(1, f["carpels"]), 5)
            ov_w = (1.9 + 0.45 * (f["carpels"] - 1)) * S
            ov_h = 2.4 * S
            ocx, ocy, head_y, lh_e = draw_one_pistil(0, 0, ov_w, ov_h, lobes,
                                                     locules=f["carpels"], depth=0.5)
            add_hotspot("ovary", "Ovary", ocx, ocy)
            add_hotspot("style", "Style", ocx, (ocy + head_y) / 2)
            add_hotspot("stigma", "Stigma", ocx, head_y + lh_e * 0.35)
        else:
            n = max(1, f["carpels"])
            sc = 1.0 if n <= 2 else (0.82 if n <= 4 else 0.68)
            rc = 0.0 if n == 1 else 0.7 * S
            reps = []
            for i in range(n):
                phi = math.radians(i * 360.0 / n) + spin_r
                cx3, cy3 = rc * math.cos(phi), rc * math.sin(phi)
                depth = cy3 * cE
                res = draw_one_pistil(cx3, cy3, 1.15 * S * sc, 1.7 * S * sc, 1,
                                      sc=sc, depth=depth)
                reps.append((depth,) + res)
            reps.sort()
            ocx, ocy, head_y, lh_e = reps[len(reps) // 2][1:]
            add_hotspot("ovary", "Ovary", ocx, ocy)
            add_hotspot("style", "Style", ocx, (ocy + head_y) / 2)
            add_hotspot("stigma", "Stigma", ocx, head_y + lh_e * 0.35)

    # ---- paint everything back to front ----
    elements.sort(key=lambda e: e[0])
    for idx, (_, fn) in enumerate(elements):
        fn(1 + idx * 0.05)

    # ---- numbered markers for label mode ----
    if show_numbers:
        zt = 5 + len(elements) * 0.05
        for h in hotspots:
            ax.add_patch(Circle((h["x"], h["y"]), 0.62, facecolor="#22463d",
                         edgecolor="white", linewidth=1.4, zorder=zt + 5))
            ax.text(h["x"], h["y"], str(h["num"]), ha="center", va="center",
                    color="white", fontsize=11, fontweight="bold", zorder=zt + 5.1)

    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    return fig, hotspots
