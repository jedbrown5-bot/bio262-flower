"""
flower3d.py
-----------
A real 3D flower for the BIO262 dissection game, built with Plotly.

Because it is rendered in the browser with WebGL, the student drags with the
mouse to orbit the flower smoothly, and scrolls to zoom. Nothing re-runs while
rotating. The flower model (part counts, symmetry, fusion, colours) comes from
flower_core.make_flower, so the 2D and 3D versions describe the same flower.

    from flower3d import build_flower
    fig, hotspots = build_flower(make_flower())
    fig.write_html("flower.html")
"""

import math
import numpy as np
import plotly.graph_objects as go

from flower_core import WHORL_ORDER, WHORL_LABEL   # shared vocabulary

Z0 = 0.0           # height on the stem where the whorls attach
STEM = "#5f8f4e"
STEM_DK = "#436b37"
FILAMENT = "#e7e0bf"
OVARY = "#cdeabd"
OVARY_DK = "#5f9146"
OVULE = "#f6f2d4"
STYLE_COL = "#9fce86"

LIGHT = dict(ambient=0.72, diffuse=0.6, specular=0.1, roughness=0.95, fresnel=0.05)
LIGHTPOS = dict(x=60, y=120, z=200)


# ----------------------------------------------------------------------
# mesh helpers
# ----------------------------------------------------------------------
def _grid_mesh(X, Y, Z, color, opacity=1.0):
    """Triangulate an (nu x nv) parametric surface into a Mesh3d."""
    nu, nv = X.shape
    x, y, z = X.ravel(), Y.ravel(), Z.ravel()
    I, J, K = [], [], []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a = i * nv + j
            b = a + 1
            c = a + nv
            d = c + 1
            I += [a, a]
            J += [b, d]
            K += [d, c]
    return go.Mesh3d(x=x, y=y, z=z, i=I, j=J, k=K, color=color, opacity=opacity,
                     flatshading=False, lighting=LIGHT, lightposition=LIGHTPOS,
                     hoverinfo="skip", showscale=False)


def _ellipsoid(cx, cy, cz, rx, ry, rz, color, opacity=1.0, n=16):
    u = np.linspace(0, 2 * np.pi, n)
    v = np.linspace(0, np.pi, n)
    X = cx + rx * np.outer(np.cos(u), np.sin(v))
    Y = cy + ry * np.outer(np.sin(u), np.sin(v))
    Z = cz + rz * np.outer(np.ones_like(u), np.cos(v))
    return _grid_mesh(X, Y, Z, color, opacity)


def _cylinder(cx, cy, z0, z1, r, color, n=20):
    th = np.linspace(0, 2 * np.pi, n)
    zz = np.array([z0, z1])
    TH, ZZ = np.meshgrid(th, zz)
    X = cx + r * np.cos(TH)
    Y = cy + r * np.sin(TH)
    return _grid_mesh(X, Y, ZZ, color, 1.0)


def _petal_mesh(phi_deg, psi_deg, length, halfwidth, color,
                cup=0.28, taper=0.12, nu=16, nv=9, opacity=1.0):
    """A tapered, gently cupped petal/sepal lamina pointing out and up."""
    phi = math.radians(phi_deg)
    psi = math.radians(psi_deg)
    axis = np.array([math.cos(psi) * math.cos(phi),
                     math.cos(psi) * math.sin(phi),
                     math.sin(psi)])
    tang = np.array([-math.sin(phi), math.cos(phi), 0.0])
    normal = np.cross(axis, tang)
    normal /= np.linalg.norm(normal)
    base = np.array([0.0, 0.0, Z0])

    us = np.linspace(0, 1, nu)
    vs = np.linspace(-1, 1, nv)
    X = np.zeros((nu, nv))
    Y = np.zeros((nu, nv))
    Z = np.zeros((nu, nv))
    for iu, u in enumerate(us):
        wid = halfwidth * (math.sin(math.pi * u) ** 0.6) * (1 - taper * u)
        along = length * u
        for iv, v in enumerate(vs):
            n_off = cup * (1 - v * v) * halfwidth      # gentle cup across the width
            p = base + axis * along + tang * (wid * v) + normal * n_off
            X[iu, iv], Y[iu, iv], Z[iu, iv] = p
    return _grid_mesh(X, Y, Z, color, opacity)


def _line(p0, p1, color, width, n=12):
    t = np.linspace(0, 1, n).reshape(-1, 1)
    pts = (1 - t) * np.array(p0) + t * np.array(p1)
    return go.Scatter3d(x=pts[:, 0], y=pts[:, 1], z=pts[:, 2], mode="lines",
                        line=dict(color=color, width=width), hoverinfo="skip",
                        showlegend=False)


def _dir(phi_deg, psi_deg):
    phi, psi = math.radians(phi_deg), math.radians(psi_deg)
    return np.array([math.cos(psi) * math.cos(phi),
                     math.cos(psi) * math.sin(phi),
                     math.sin(psi)])


# ----------------------------------------------------------------------
# main builder
# ----------------------------------------------------------------------
WHORL_OF = {"sepal": "calyx", "petal": "corolla", "filament": "androecium",
            "anther": "androecium", "stamen": "androecium", "ovary": "gynoecium",
            "style": "gynoecium", "stigma": "gynoecium", "carpel": "gynoecium",
            "pistil": "gynoecium"}


def build_flower(f, removed=None, highlight=None, show_numbers=False, cutaway=True,
                 spotlight=None):
    """Return (plotly Figure, hotspots). hotspots: {part,name,num,pos(x,y,z)}.

    spotlight : a part key. When set, that part's whorl is kept vivid (others
    dimmed) and a single named leader-line callout points at it. Used to render
    a clear per-part illustration for the glossary.
    """
    removed = removed or set()
    if spotlight and not highlight:
        highlight = WHORL_OF.get(spotlight)
    S = f["scale"]
    traces = []
    hotspots = []
    seen = set()

    def op(whorl):
        return 0.25 if (highlight and whorl != highlight and whorl != "stem") else 1.0

    def add_hotspot(part, name, pos):
        if part in seen:
            return
        seen.add(part)
        hotspots.append({"part": part, "name": name, "num": len(hotspots) + 1,
                         "pos": pos})

    # ---- stem + receptacle ----
    traces.append(_cylinder(0, 0, -3.2, Z0, 0.26 * S, STEM))
    traces.append(_ellipsoid(0, 0, Z0, 0.7 * S, 0.7 * S, 0.36 * S, STEM))
    add_hotspot("receptacle", "Receptacle", (0, 0, Z0))

    halfstep = 180.0 / max(1, f["petals"])

    # ---- calyx (sepals) ----
    if "calyx" not in removed:
        o = op("calyx")
        for i in range(f["sepals"]):
            phi = i * 360.0 / f["sepals"] + halfstep
            traces.append(_petal_mesh(phi, 14, 2.6 * S, 0.42 * S, f["sepal_fill"],
                                      cup=0.18, opacity=o))
            if i == 0:
                d = _dir(phi, 14)
                add_hotspot("sepal", "Sepal", tuple(d * 2.1 * S))

    # ---- corolla (petals) ----
    if "corolla" not in removed:
        o = op("corolla")
        if f["petal_fusion"] == "fused":
            # a corolla cup/tube that unites the petal bases
            traces.append(_cylinder(0, 0, Z0, Z0 + 1.1 * S, 0.9 * S, f["petal_fill"]))
            th = np.linspace(0, 2 * np.pi, 24)
            hh = np.linspace(0, 1, 6)
            TH, HH = np.meshgrid(th, hh)
            R = (0.9 + 0.7 * HH) * S
            X = R * np.cos(TH)
            Y = R * np.sin(TH)
            Z = Z0 + HH * 1.4 * S
            traces.append(_grid_mesh(X, Y, Z, f["petal_fill"], o))
        for i in range(f["petals"]):
            phi = i * 360.0 / f["petals"]
            psi = 40
            if f["symmetry"] == "bilateral":
                psi = 40 + 16 * math.cos(math.radians(phi))
            traces.append(_petal_mesh(phi, psi, 3.1 * S, 0.95 * S, f["petal_fill"],
                                      cup=0.30, opacity=o))
            if i == 0:
                d = _dir(phi, psi)
                add_hotspot("petal", "Petal", tuple(d * 1.7 * S))

    # ---- androecium (stamens) ----
    if "androecium" not in removed:
        o = op("androecium")
        for i in range(f["stamens"]):
            phi = i * 360.0 / f["stamens"] + halfstep / 2
            d = _dir(phi, 66)
            base = np.array([0, 0, Z0 + 0.2 * S])
            tip = base + d * 2.2 * S
            traces.append(_line(base, tip, FILAMENT, 6, n=8))
            traces.append(_ellipsoid(tip[0], tip[1], tip[2],
                                     0.16 * S, 0.16 * S, 0.32 * S, f["anther"], o))
            if i == 0:
                add_hotspot("filament", "Filament", tuple((base + tip) / 2))
                add_hotspot("anther", "Anther", tuple(tip))

    # ---- gynoecium (pistil) ----
    if "gynoecium" not in removed:
        o = op("gynoecium")
        stig = f["stigma"]

        def pistil(cx, cy, ovr, ovh, lobes, sc=1.0):
            ocz = Z0 + 0.55 * sc
            traces.append(_ellipsoid(cx, cy, ocz, ovr, ovr, ovh, OVARY, o))
            style_top = ocz + ovh + 1.4 * sc
            traces.append(_line((cx, cy, ocz + ovh * 0.4),
                                (cx, cy, style_top), STYLE_COL, 6 * sc, n=6))
            if lobes <= 1:
                traces.append(_ellipsoid(cx, cy, style_top + 0.2 * sc,
                                         0.4 * sc, 0.4 * sc, 0.3 * sc, stig, o))
                head = (cx, cy, style_top + 0.2 * sc)
            else:
                head = (cx, cy, style_top + 0.2 * sc)
                for lb in range(lobes):
                    ang = lb * 2 * math.pi / lobes
                    lx = cx + 0.28 * sc * math.cos(ang)
                    ly = cy + 0.28 * sc * math.sin(ang)
                    traces.append(_ellipsoid(lx, ly, style_top + 0.25 * sc,
                                             0.28 * sc, 0.28 * sc, 0.24 * sc, stig, o))
            return ocz, style_top, head

        if f["carpel_fusion"] == "fused":
            lobes = min(max(1, f["carpels"]), 5)
            ovr = (0.5 + 0.08 * (f["carpels"] - 1)) * S
            ovh = 0.72 * S
            ocz0 = Z0 + 0.55
            # faint ridges hinting at the fused chambers
            for c in range(f["carpels"]):
                ang = c * 2 * math.pi / f["carpels"]
                rx, ry = math.cos(ang) * ovr, math.sin(ang) * ovr
                traces.append(_line((rx, ry, ocz0 - ovh * 0.6),
                                    (rx, ry, ocz0 + ovh * 0.6), OVARY_DK, 3))
            ocz, stop, head = pistil(0, 0, ovr, ovh, lobes)
            add_hotspot("ovary", "Ovary", (0, 0, ocz))
            add_hotspot("style", "Style", (0, 0, (ocz + stop) / 2))
            add_hotspot("stigma", "Stigma", head)
        else:
            n = max(1, f["carpels"])
            sc = 1.0 if n <= 2 else (0.8 if n <= 4 else 0.66)
            rc = 0.0 if n == 1 else 0.55 * S
            reps = []
            for i in range(n):
                ang = i * 2 * math.pi / n
                cx, cy = rc * math.cos(ang), rc * math.sin(ang)
                reps.append((cx, cy) + pistil(cx, cy, 0.42 * S * sc, 0.6 * S * sc, 1, sc))
            cx, cy, ocz, stop, head = reps[len(reps) // 2]
            add_hotspot("ovary", "Ovary", (cx, cy, ocz))
            add_hotspot("style", "Style", (cx, cy, (ocz + stop) / 2))
            add_hotspot("stigma", "Stigma", head)

    # ---- single named callout for a glossary spotlight ----
    if spotlight:
        alias_t = {"carpel": "ovary", "pistil": "ovary", "stamen": "anther"}
        alias_n = {"carpel": "Carpel (pistil)", "pistil": "Carpel (pistil)",
                   "stamen": "Stamen"}
        target = alias_t.get(spotlight, spotlight)
        h = next((hh for hh in hotspots if hh["part"] == target), None)
        if h:
            x, y, z = h["pos"]
            name = alias_n.get(spotlight, h["name"])
            r = math.hypot(x, y)
            az = math.atan2(y, x) if r > 0.4 else math.radians(50)
            lp = (4.0 * S * math.cos(az), 4.0 * S * math.sin(az), z + 0.6)
            traces.append(go.Scatter3d(x=[x, lp[0]], y=[y, lp[1]], z=[z, lp[2]],
                          mode="lines", line=dict(color="#22463d", width=4),
                          hoverinfo="skip", showlegend=False))
            traces.append(go.Scatter3d(x=[x], y=[y], z=[z], mode="markers",
                          marker=dict(size=5, color="#22463d"), hoverinfo="skip",
                          showlegend=False))
            traces.append(go.Scatter3d(
                x=[lp[0]], y=[lp[1]], z=[lp[2]], mode="markers+text", text=[name],
                textposition="top center",
                textfont=dict(color="#22463d", size=20, family="Arial Black"),
                marker=dict(size=10, color="#22463d", line=dict(color="white", width=2)),
                hoverinfo="skip", showlegend=False))

    # ---- numbered callouts for label mode (leader lines, kept clear of the bloom) ----
    if show_numbers:
        R = 4.0 * S
        centre_order = ["receptacle", "ovary", "style", "stigma"]
        centre_z = {"receptacle": -0.4, "ovary": 0.5, "style": 1.5, "stigma": 2.5}
        anc_x, anc_y, anc_z = [], [], []
        lab_x, lab_y, lab_z, lab_t = [], [], [], []
        for h in hotspots:
            x, y, z = h["pos"]
            r = math.hypot(x, y)
            if r > 0.4 and h["part"] in ("sepal", "petal", "anther", "filament"):
                az = math.atan2(y, x)
                lp = (R * math.cos(az), R * math.sin(az), z + 0.3)
            else:
                k = centre_order.index(h["part"]) if h["part"] in centre_order else 0
                az = math.radians(45 + 90 * k)
                lp = (R * math.cos(az), R * math.sin(az), centre_z.get(h["part"], z))
            traces.append(go.Scatter3d(x=[x, lp[0]], y=[y, lp[1]], z=[z, lp[2]],
                          mode="lines", line=dict(color="#3a4a42", width=3),
                          hoverinfo="skip", showlegend=False))
            anc_x.append(x); anc_y.append(y); anc_z.append(z)
            lab_x.append(lp[0]); lab_y.append(lp[1]); lab_z.append(lp[2])
            lab_t.append(str(h["num"]))
        traces.append(go.Scatter3d(x=anc_x, y=anc_y, z=anc_z, mode="markers",
                      marker=dict(size=4, color="#3a4a42"), hoverinfo="skip",
                      showlegend=False))
        traces.append(go.Scatter3d(
            x=lab_x, y=lab_y, z=lab_z, mode="markers+text", text=lab_t,
            textposition="middle center", textfont=dict(color="white", size=13),
            marker=dict(size=19, color="#22463d", line=dict(color="white", width=2)),
            hoverinfo="skip", showlegend=False))

    fig = go.Figure(data=traces)
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.4, y=1.4, z=1.0),
                        up=dict(x=0, y=0, z=1)),
            bgcolor="#f4f8f1",
        ),
        paper_bgcolor="#f4f8f1",
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        uirevision="flower",     # keep the camera when Streamlit re-runs
    )
    return fig, hotspots
