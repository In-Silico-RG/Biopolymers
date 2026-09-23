#!/usr/bin/env python3
"""Phase 1 figures, built from outputs/tables/ only.

Colors are the dataviz reference categorical palette, slots taken in fixed order and
never cycled. The palette ships pre-validated; the Node validator was not available on
this machine, so no custom palette was invented.

Rules followed: one y-axis per panel and never two scales in one plot, a legend whenever
two or more series share a panel plus direct labels, recessive grid and axes, text in ink
tokens rather than series colors.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TAB, FIG = ROOT / "outputs/tables", ROOT / "outputs/figures"

S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "font.size": 9,
    "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": "#e6e5e1", "grid.linewidth": 0.6,
    "font.family": "DejaVu Sans",
})

CTX = [("world", "World", S1), ("ibero", "Ibero-America", S2),
       ("latam", "Latin America", S3), ("colombia", "Colombia", S4)]


def fig1_production():
    """Small multiples. The four contexts differ by three orders of magnitude, so they
    get one panel each with its own scale rather than a second y-axis."""
    t1 = pd.read_csv(TAB / "T1_annual_production.csv").set_index("year")
    t1 = t1[t1.index >= 1995]
    fig, axes = plt.subplots(1, 4, figsize=(11, 2.9))
    for ax, (key, label, col) in zip(axes, CTX):
        s = t1[f"core_{key}"]
        ax.fill_between(s.index, s.values, color=col, alpha=0.18, linewidth=0)
        ax.plot(s.index, s.values, color=col, linewidth=2)
        ax.set_title(label, color=INK, fontsize=10, pad=8, loc="left")
        ax.grid(axis="y"); ax.set_axisbelow(True)
        ax.set_xlim(1995, 2025)
        ax.set_xticks([1995, 2005, 2015, 2025])
        peak = int(s.max()); pyear = int(s.idxmax())
        ax.annotate(f"{peak:,} in {pyear}", xy=(pyear, peak),
                    xytext=(-4, -12), textcoords="offset points",
                    ha="right", fontsize=8, color=INK2)
    axes[0].set_ylabel("works per year")
    fig.suptitle("Annual production of the biopolymers field, 1995-2025",
                 x=0.005, ha="left", fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(FIG / "F1_annual_production.png", dpi=220)
    fig.savefig(FIG / "F1_annual_production.pdf")
    plt.close(fig)


def fig2_methods_share():
    """The central figure: all four series are percentages, so they share one axis.

    The ratio is computed on a 3-year rolling sum, not on single years, and a point is
    dropped when its rolling denominator is under MIN_DEN works. Colombia publishes 0-3
    method papers a year, so a raw yearly percentage there swings between 0 and 9 percent
    and shows sampling noise rather than any change in practice.
    """
    MIN_DEN, WIN = 50, 3
    t1 = pd.read_csv(TAB / "T1_annual_production.csv").set_index("year")
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for key, label, col in CTX:
        num = t1[f"methods_{key}"].rolling(WIN, min_periods=WIN).sum()
        den = t1[f"core_{key}"].rolling(WIN, min_periods=WIN).sum()
        s_ = (num / den * 100).where(den >= MIN_DEN)
        s_ = s_[(s_.index >= 2000) & (s_.index <= 2025)].dropna()
        if s_.empty:
            continue
        ax.plot(s_.index, s_.values, color=col, linewidth=2, label=label)
        ax.annotate(label, xy=(s_.index[-1], s_.values[-1]),
                    xytext=(6, 0), textcoords="offset points",
                    color=INK2, fontsize=8.5, va="center")
    ax.set_ylabel("share of the field using computational or AI methods (%)")
    ax.set_xlabel("year (3-year rolling window, ending)")
    ax.grid(axis="y"); ax.set_axisbelow(True)
    ax.set_xlim(2000, 2030); ax.set_ylim(bottom=0)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5, labelcolor=INK2)
    ax.set_title("Uptake of computational chemistry, chemoinformatics and AI\n"
                 "inside the biopolymers field", loc="left", fontsize=12,
                 color=INK, pad=10)
    ax.text(0.0, -0.20, f"3-year rolling sums. A point is shown only where the window holds "
            f"at least {MIN_DEN} works.", transform=ax.transAxes, fontsize=7.5, color=MUTED)
    fig.tight_layout()
    fig.savefig(FIG / "F2_methods_share.png", dpi=220)
    fig.savefig(FIG / "F2_methods_share.pdf")
    plt.close(fig)


def fig3_countries():
    """Two panels sharing the country axis: volume on the left, method intensity on the
    right. Two measures of different scale are never put on one pair of axes."""
    t4 = pd.read_csv(TAB / "T4_country_ranking.csv").head(20).iloc[::-1]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 6), sharey=True,
                                 gridspec_kw={"width_ratios": [2, 1]})
    y = range(len(t4))
    latam = {"BR", "MX", "AR", "CO", "CL", "PE", "EC", "UY", "VE", "CR"}
    colors = [S3 if c in latam else S1 for c in t4["country_code"]]
    a1.barh(list(y), t4["core_count"], color=colors, height=0.68)
    a1.set_yticks(list(y)); a1.set_yticklabels(t4["country"], color=INK2)
    a1.set_xlabel("works in the biopolymers field")
    a1.grid(axis="x"); a1.set_axisbelow(True)
    for i, v in enumerate(t4["core_count"]):
        a1.text(v + 250, i, f"{v:,}", va="center", fontsize=8, color=INK2)
    a2.barh(list(y), t4["methods_share_pct"], color=colors, height=0.68)
    a2.set_xlabel("of which computational or AI (%)")
    a2.grid(axis="x"); a2.set_axisbelow(True)
    for i, v in enumerate(t4["methods_share_pct"]):
        a2.text(v + 0.08, i, f"{v:.1f}", va="center", fontsize=8, color=INK2)
    from matplotlib.patches import Patch
    a1.legend(handles=[Patch(facecolor=S3, label="Latin America"),
                       Patch(facecolor=S1, label="Rest of the world")],
              frameon=False, loc="lower right", fontsize=8.5, labelcolor=INK2)
    fig.suptitle("Top 20 countries by biopolymer research volume, and how much of it is computational",
                 x=0.005, ha="left", fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(FIG / "F3_country_ranking.png", dpi=220)
    fig.savefig(FIG / "F3_country_ranking.pdf")
    plt.close(fig)


def fig4_anchors():
    t6 = pd.read_csv(TAB / "T6_anchor_lines.csv")
    names = {"cellulose": "Cellulose and\nnanocellulose", "pha": "PHA / PHB",
             "lignin": "Lignin"}
    labels = [names[a] for a in t6["anchor"]]
    x = range(len(t6)); w = 0.36
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.8))
    a1.bar([i - w/2 for i in x], t6["world"], width=w, color=S1, label="World")
    a1.bar([i + w/2 for i in x], t6["latam"], width=w, color=S3, label="Latin America")
    a1.set_yscale("log"); a1.set_ylabel("works (log scale)")
    a1.set_xticks(list(x)); a1.set_xticklabels(labels, color=INK2, fontsize=8.5)
    a1.grid(axis="y"); a1.set_axisbelow(True)
    a1.legend(frameon=False, fontsize=8.5, labelcolor=INK2)
    for i, (wv, lv) in enumerate(zip(t6["world"], t6["latam"])):
        a1.text(i - w/2, wv * 1.15, f"{wv:,}", ha="center", fontsize=7.5, color=INK2)
        a1.text(i + w/2, lv * 1.15, f"{lv:,}", ha="center", fontsize=7.5, color=INK2)
    a1.set_title("Volume", loc="left", color=INK, fontsize=10)
    a2.bar([i - w/2 for i in x], t6["methods_share_world_pct"], width=w, color=S1)
    a2.bar([i + w/2 for i in x], t6["methods_share_latam_pct"], width=w, color=S3)
    a2.set_ylabel("computational or AI share (%)")
    a2.set_xticks(list(x)); a2.set_xticklabels(labels, color=INK2, fontsize=8.5)
    a2.grid(axis="y"); a2.set_axisbelow(True)
    for i, (wv, lv) in enumerate(zip(t6["methods_share_world_pct"],
                                     t6["methods_share_latam_pct"])):
        a2.text(i - w/2, wv + 0.05, f"{wv:.2f}", ha="center", fontsize=7.5, color=INK2)
        a2.text(i + w/2, lv + 0.05, f"{lv:.2f}", ha="center", fontsize=7.5, color=INK2)
    a2.set_title("Method intensity", loc="left", color=INK, fontsize=10)
    fig.suptitle("The three anchored biopolymer lines", x=0.005, ha="left",
                 fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(FIG / "F4_anchor_lines.png", dpi=220)
    fig.savefig(FIG / "F4_anchor_lines.pdf")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    fig1_production(); fig2_methods_share(); fig3_countries(); fig4_anchors()
    for p in sorted(FIG.glob("*")):
        print(f"  {p.name}")
