"""Figures in the project's visual identity (brand palette, Source Code Pro)."""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from shapely.geometry import box

from . import style
from .config import TOWNS
from .data import town_view

HEAD, FOOT = 1.5, 0.6

# Variables of the tract maps: column, title, class breaks, labels, colors
PANELS = [
    ("residents", "Residents per tract", [0, 250, 500, 750, 1000, float("inf")],
     ["Under 250", "250–500", "500–750", "750–1,000", "1,000 or more"], style.SEQ),
    ("residents_per_dwelling", "Residents per dwelling", [0, 2.5, 3, 3.5, float("inf")],
     ["Under 2.5", "2.5–3", "3–3.5", "3.5 or more"], style.SEQ_GREEN),
    ("income_mw", "Mean income of the household head", [0, 1, 2, 3, float("inf")],
     ["Under 1 MW", "1–2 MW", "2–3 MW", "3 MW or more"], style.SEQ_OCHRE),
]
MAIN = ("motorway", "trunk", "primary", "secondary")


def _legend(fig, handles, x, y, title=None, **kw):
    opts = dict(loc="upper left", bbox_to_anchor=(x, y), fontsize=8, title_fontsize=8.5, handlelength=1.2,
                alignment="left", labelspacing=0.5)
    opts.update(kw)
    leg = fig.legend(handles=handles, title=title, **opts)
    leg.get_title().set_fontweight("semibold")
    return leg


def _context(ax, view, streets, water, labels=False):
    x0, y0, x1, y1 = view
    if water is not None:
        water.cx[x0:x1, y0:y1].plot(ax=ax, color=style.WATER, linewidth=0, zorder=2)
    s = streets.cx[x0:x1, y0:y1]
    s[~s["highway"].isin(MAIN)].plot(ax=ax, color="white", linewidth=0.45, alpha=0.9, zorder=3)
    main = s[s["highway"].isin(MAIN)]
    main.plot(ax=ax, color=style.INK, linewidth=1.6, zorder=4)
    if labels:
        for ref, g in main.dropna(subset=["ref"]).dissolve("ref").iterrows():
            geom = g.geometry.intersection(shapely_box(view, shrink=0.12))
            if not geom.is_empty and geom.length > 600:
                p = geom.interpolate(0.5, normalized=True)
                ax.text(p.x, p.y, ref.split(";")[0], fontsize=7.5, fontweight="semibold", color=style.INK, ha="center",
                        va="center", path_effects=style.halo(2.5), zorder=7)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(True)
        sp.set_color(style.GREY)


def shapely_box(view, shrink=0.0):
    """The view as a polygon, optionally shrunk by a share of its size (keeps labels off the edges)."""
    x0, y0, x1, y1 = view
    dx, dy = (x1 - x0) * shrink, (y1 - y0) * shrink
    return box(x0 + dx, y0 + dy, x1 - dx, y1 - dy)


def _square(view):
    """Square extent around a view, so the three towns share one panel shape."""
    x0, y0, x1, y1 = view
    cx, cy, half = (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2
    return (cx - half, cy - half, cx + half, cy + half)


def map_tracts(t, streets, water, out):
    """3 x 3 grid: towns in rows, census variables in columns (2010)."""
    towns = list(TOWNS)
    W, H = 12, 14.2
    fig, axes = plt.subplots(3, 3, figsize=(W, H))
    fig.subplots_adjust(left=0.07, right=0.99, top=1 - (HEAD + 0.5) / H, bottom=(FOOT + 1.35) / H, wspace=0.03, hspace=0.05)
    for i, town in enumerate(towns):
        view = _square(town_view(t, town))
        km = (view[2] - view[0]) / 1000
        for j, (col, title, breaks, labels, colors) in enumerate(PANELS):
            ax = axes[i, j]
            cls = pd.cut(t[col], breaks, labels=labels, right=False)
            for lab, color in zip(labels, colors):
                sub = t[cls == lab]
                if len(sub):
                    sub.plot(ax=ax, color=color, linewidth=0, zorder=1)
            t.boundary.plot(ax=ax, color="white", linewidth=0.5, zorder=1.5)
            _context(ax, view, streets[town], water)
            if i == 0:
                ax.set_title(title, loc="left", fontsize=9.5, fontweight="semibold", color=style.INK, pad=8)
            if j == 0:
                ax.set_ylabel(town, fontsize=11, fontweight="semibold", color=style.INK, labelpad=8)
            if j == 2:
                style.scalebar(ax, km=1, loc=(0.06, 0.05))
                ax.text(0.95, 0.04, f"{km:.1f} km wide", transform=ax.transAxes, ha="right", fontsize=7,
                        color=style.MUTED, path_effects=style.halo(2))
    for j, (col, title, breaks, labels, colors) in enumerate(PANELS):
        x = axes[2, j].get_position().x0
        _legend(fig, [Patch(facecolor=c, label=lab) for lab, c in zip(labels, colors)], x - 0.005, (FOOT + 1.25) / H,
                ncol=2, columnspacing=1.0)
    _legend(fig, [Line2D([], [], color=style.INK, lw=1.6, label="Main roads"),
                  Patch(facecolor=style.WATER, label="Rivers")], 0.82, 1 - (HEAD - 0.1) / H, ncol=2, columnspacing=1.0)
    style.header(fig, "Three small towns, census tract by census tract",
                 "Sobradinho, Rio Pardo and Encantado in the 2010 census. Income in minimum wages (MW) of 2010 (R$ 510).\n"
                 "Larger households and lower incomes sit at the edges; the highest incomes are in the centers.")
    style.footer(fig)
    style.save(fig, out)


def map_neighborhoods(nb, streets, water, out):
    """The neighborhoods of the three towns (IBGE 2010), shaded by residents."""
    towns = list(TOWNS)
    W, H = 13, 7.0
    fig, axes = plt.subplots(1, 3, figsize=(W, H))
    fig.subplots_adjust(left=0.01, right=0.99, top=1 - (HEAD + 0.45) / H, bottom=(FOOT + 0.75) / H, wspace=0.03)
    breaks, labels = [0, 1000, 2000, 4000, float("inf")], ["Under 1,000", "1,000–2,000", "2,000–4,000", "4,000 or more"]
    colors = style.SEQ[:4]
    for ax, town in zip(axes, towns):
        n = nb[nb["town"] == town]
        view = _square(tuple(n.total_bounds + [-500, -500, 500, 500]))
        cls = pd.cut(n["residents"], breaks, labels=labels, right=False)
        for lab, color in zip(labels, colors):
            sub = n[cls == lab]
            if len(sub):
                sub.plot(ax=ax, color=color, linewidth=0, zorder=1, alpha=0.85)
        n.boundary.plot(ax=ax, color="white", linewidth=1.4, zorder=1.5)
        _context(ax, view, streets[town], water)
        # label boxes in map units: a 7.5 pt monospaced character is about 0.0625 in wide
        unit = (view[2] - view[0]) / (ax.get_position().width * W) * 0.0625
        placed, keyed = [], []
        for _, r in n.assign(a=n.area).sort_values("a", ascending=False).iterrows():
            p = r.geometry.representative_point()
            name = r["neighborhood"]
            half_w, half_h = (len(name) + 1) * unit / 2, 1.1 * unit
            box_ = (p.x - half_w, p.y - half_h, p.x + half_w, p.y + half_h)
            free = all(box_[2] < b[0] or box_[0] > b[2] or box_[3] < b[1] or box_[1] > b[3] for b in placed)
            if free:
                ax.text(p.x, p.y, name, fontsize=7.5, color=style.INK, ha="center", va="center",
                        path_effects=style.halo(2.5), zorder=8)
                placed.append(box_)
            else:
                keyed.append(name)
                ax.text(p.x, p.y, str(len(keyed)), fontsize=7.5, fontweight="semibold", color=style.INK, ha="center",
                        va="center", path_effects=style.halo(2.5), zorder=8)
                placed.append((p.x - unit, p.y - half_h, p.x + unit, p.y + half_h))
        if keyed:
            ax.text(0.98, 0.03, "\n".join(f"{i}  {k}" for i, k in enumerate(keyed, 1)), transform=ax.transAxes,
                    ha="right", va="bottom", fontsize=7.5, color=style.INK, linespacing=1.4,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=3), zorder=9)
        ax.set_title(f"{town}  ·  {len(n)} neighborhoods", loc="left", fontsize=10.5, fontweight="semibold",
                     color=style.INK, pad=8)
        style.scalebar(ax, km=1, loc=(0.06, 0.05))
    _legend(fig, [Patch(facecolor=c, label=lab) for lab, c in zip(labels, colors)], 0.035, (FOOT + 0.6) / H,
            "Residents (2010)", ncol=4, columnspacing=1.4, fontsize=8.5)
    _legend(fig, [Line2D([], [], color=style.INK, lw=1.6, label="Main roads"), Patch(facecolor=style.WATER, label="Rivers")],
            0.62, (FOOT + 0.42) / H, ncol=2, fontsize=8.5)
    style.header(fig, "The neighborhoods of three small towns",
                 "Urban neighborhoods as delimited by IBGE in the 2010 census, shaded by number of residents, with the main roads.")
    style.footer(fig)
    style.save(fig, out)
