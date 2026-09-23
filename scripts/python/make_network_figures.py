#!/usr/bin/env python3
"""Figures for the co-authorship analysis.

A 115-node co-authorship graph drawn as a node-link diagram is a hairball: it looks like
analysis and reads like nothing. The collaboration structure is shown here as a matrix,
which is legible, and the node-link rendering is left to VOSviewer, which is the tool
built for it. The VOSviewer map+network pairs are written by networks.py into outputs/maps/.
"""
import json, itertools
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REC, TAB, FIG = ROOT / "data/raw/openalex/records", ROOT / "outputs/tables", ROOT / "outputs/figures"

S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
# Sequential ramp: one hue, light to dark, from the dataviz blue ramp.
BLUES = LinearSegmentedColormap.from_list(
    "blues", ["#f2f7fe", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#0d366b"])

LATAM = ["BR", "MX", "AR", "CO", "CL", "PE", "EC", "UY", "VE", "CR", "CU", "BO"]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": "#e6e5e1", "grid.linewidth": 0.6, "font.family": "DejaVu Sans",
})


def countries_of(rec):
    cs = set()
    for a in rec.get("authorships") or []:
        for i in a.get("institutions") or []:
            if i.get("country_code"):
                cs.add(i["country_code"])
    return cs


def read(stem):
    p = REC / f"{stem}.jsonl"
    return [json.loads(l) for l in p.open(encoding="utf-8")] if p.exists() else []


def fig5_collab_matrix():
    """Who Latin America publishes with, as a matrix rather than a node-link hairball."""
    recs = read("core_latam")
    pair = Counter(); solo = Counter()
    for r in recs:
        cs = countries_of(r)
        for c in cs:
            solo[c] += 1
        for a, b in itertools.combinations(sorted(cs), 2):
            pair[(a, b)] += 1
    partners = Counter()
    for (a, b), w in pair.items():
        if a in LATAM and b not in LATAM:
            partners[b] += w
        elif b in LATAM and a not in LATAM:
            partners[a] += w
    outside = [c for c, _ in partners.most_common(10)]
    cols = LATAM + outside
    M = pd.DataFrame(0, index=LATAM, columns=cols, dtype=int)
    for (a, b), w in pair.items():
        for x, y in ((a, b), (b, a)):
            if x in M.index and y in M.columns:
                M.loc[x, y] = w
    fig, ax = plt.subplots(figsize=(10, 5.2))
    im = ax.imshow(M.values, cmap=BLUES, aspect="auto")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, color=INK2)
    ax.set_yticks(range(len(LATAM))); ax.set_yticklabels(LATAM, color=INK2)
    ax.axvline(len(LATAM) - 0.5, color=MUTED, linewidth=1)
    for i in range(len(LATAM)):
        for j in range(len(cols)):
            v = M.values[i, j]
            if v:
                ax.text(j, i, v, ha="center", va="center", fontsize=6.6,
                        color="#ffffff" if v > M.values.max() * 0.45 else INK2)
    ax.text(len(LATAM) / 2 - 0.5, -1.05, "within Latin America", ha="center",
            fontsize=8.5, color=INK2)
    ax.text(len(LATAM) + len(outside) / 2 - 0.5, -1.05, "outside partners",
            ha="center", fontsize=8.5, color=INK2)
    cb = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02)
    cb.set_label("co-authored works", color=INK2, fontsize=8.5)
    cb.outline.set_visible(False)
    ax.set_title("Country co-authorship in Latin American biopolymer research",
                 loc="left", fontsize=12, color=INK, pad=24)
    ax.set_ylim(len(LATAM) - 0.5, -1.6)
    fig.tight_layout()
    fig.savefig(FIG / "F5_collaboration_matrix.png", dpi=220)
    fig.savefig(FIG / "F5_collaboration_matrix.pdf")
    plt.close(fig)


def fig6_lotka():
    """Author productivity. A steeper slope means a shallower core of specialists."""
    pairs = [("methods_world", "World, computational layer", S1),
             ("core_latam", "Latin America, whole field", S3),
             ("core_colombia", "Colombia, whole field", S4)]
    summ = pd.read_csv(TAB / "T16_lotka_summary.csv").set_index("corpus")
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    for stem, label, col in pairs:
        p = TAB / f"T_lotka_{stem}.csv"
        if not p.exists():
            continue
        d = pd.read_csv(p)
        d = d[d["works_per_author"] <= 20]
        ax.plot(d["works_per_author"], d["share_pct"], color=col, linewidth=2,
                marker="o", markersize=4, label=f"{label} (n={summ.loc[stem,'lotka_exponent']})")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("works by the same author")
    ax.set_ylabel("share of authors (%)")
    ax.grid(which="both"); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8.5, labelcolor=INK2)
    ax.set_title("Author productivity: how shallow the specialist core is\n"
                 "(n is the fitted Lotka exponent; classic Lotka is 2)",
                 loc="left", fontsize=11.5, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(FIG / "F6_lotka.png", dpi=220)
    fig.savefig(FIG / "F6_lotka.pdf")
    plt.close(fig)


def fig7_colombia_partners():
    """Colombia's partners, split between the region and outside it."""
    recs = read("core_colombia")
    partners = Counter()
    for r in recs:
        cs = countries_of(r)
        if "CO" not in cs:
            continue
        for c in cs - {"CO"}:
            partners[c] += 1
    top = partners.most_common(18)[::-1]
    labels = [c for c, _ in top]; vals = [v for _, v in top]
    colors = [S3 if c in LATAM else S1 for c in labels]
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    ax.barh(range(len(top)), vals, color=colors, height=0.68)
    ax.set_yticks(range(len(top))); ax.set_yticklabels(labels, color=INK2)
    for i, v in enumerate(vals):
        ax.text(v + 0.6, i, str(v), va="center", fontsize=8, color=INK2)
    ax.set_xlabel("works co-authored with Colombia")
    ax.grid(axis="x"); ax.set_axisbelow(True)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=S3, label="Latin America"),
                       Patch(facecolor=S1, label="Outside the region")],
              frameon=False, loc="lower right", fontsize=8.5, labelcolor=INK2)
    ax.set_title("Who Colombia publishes biopolymer research with",
                 loc="left", fontsize=12, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(FIG / "F7_colombia_partners.png", dpi=220)
    fig.savefig(FIG / "F7_colombia_partners.pdf")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    fig5_collab_matrix(); fig6_lotka(); fig7_colombia_partners()
    print("figures written")
