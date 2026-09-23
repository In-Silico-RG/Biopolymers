#!/usr/bin/env python3
"""Co-authorship networks, productivity laws and journal concentration.

Reads the harvested records in data/raw/openalex/records/ and produces:

  outputs/tables/   collaboration shares, centrality rankings, Lotka fit, Bradford zones
  outputs/maps/     VOSviewer map+network pairs, ready to open in VOSviewer
  outputs/figures/  the country co-authorship graph

Networks are built from co-occurrence within a work: every pair of distinct entities on a
work gets an edge, weighted by how many works they share. Country attribution comes from
institutions, so a work with authors in three countries contributes three pairs.
"""
import json, sys, itertools, math
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "data/raw/openalex/records"
TAB, MAPS, FIG = ROOT / "outputs/tables", ROOT / "outputs/maps", ROOT / "outputs/figures"

LATAM = {"AR", "BO", "BR", "CL", "CO", "CR", "CU", "DO", "EC", "GT", "HN", "MX",
         "NI", "PA", "PE", "PR", "PY", "SV", "UY", "VE"}


def read(stem):
    p = REC / f"{stem}.jsonl"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh]


def entities(rec):
    """Countries, institutions and authors of one work, each deduplicated."""
    countries, insts, authors = set(), {}, {}
    for a in rec.get("authorships") or []:
        au = a.get("author") or {}
        if au.get("id"):
            authors[au["id"]] = au.get("display_name") or au["id"]
        for i in a.get("institutions") or []:
            if i.get("country_code"):
                countries.add(i["country_code"])
            if i.get("id"):
                insts[i["id"]] = i.get("display_name") or i["id"]
    return countries, insts, authors


def cooccurrence(records, picker, min_weight=1):
    """Build a weighted co-occurrence graph plus a label map and per-node work counts."""
    G = nx.Graph()
    labels, docs = {}, Counter()
    for rec in records:
        items = picker(rec)
        if isinstance(items, dict):
            labels.update(items)
            keys = list(items)
        else:
            keys = sorted(items)
            labels.update({k: k for k in keys})
        for k in keys:
            docs[k] += 1
        for a, b in itertools.combinations(sorted(keys), 2):
            if G.has_edge(a, b):
                G[a][b]["weight"] += 1
            else:
                G.add_edge(a, b, weight=1)
    for k, c in docs.items():
        G.add_node(k)
        G.nodes[k]["docs"] = c
        G.nodes[k]["label"] = labels.get(k, k)
    if min_weight > 1:
        G.remove_edges_from([(u, v) for u, v, d in G.edges(data=True)
                             if d["weight"] < min_weight])
    return G


def write_vosviewer(G, stem, top=None):
    """VOSviewer map + network pair. Tab separated, as VOSviewer expects."""
    MAPS.mkdir(parents=True, exist_ok=True)
    nodes = sorted(G.nodes, key=lambda n: -G.nodes[n].get("docs", 0))
    if top:
        nodes = nodes[:top]
    keep = set(nodes)
    H = G.subgraph(keep).copy()
    H.remove_nodes_from([n for n in list(H.nodes) if H.degree(n) == 0])
    nodes = [n for n in nodes if n in H]
    idx = {n: i + 1 for i, n in enumerate(nodes)}
    try:
        comms = nx.community.louvain_communities(H, weight="weight", seed=7)
    except Exception:
        comms = [set(H.nodes)]
    cluster = {n: c + 1 for c, s in enumerate(comms) for n in s}
    with (MAPS / f"{stem}_map.txt").open("w", encoding="utf-8") as fh:
        fh.write("id\tlabel\tweight<Documents>\tcluster\n")
        for n in nodes:
            fh.write(f"{idx[n]}\t{H.nodes[n].get('label', n)}\t"
                     f"{H.nodes[n].get('docs', 0)}\t{cluster.get(n, 1)}\n")
    with (MAPS / f"{stem}_network.txt").open("w", encoding="utf-8") as fh:
        for u, v, d in H.edges(data=True):
            if u in idx and v in idx:
                fh.write(f"{idx[u]}\t{idx[v]}\t{d['weight']}\n")
    return H, cluster


def centrality_table(G, stem, top=40):
    if G.number_of_nodes() == 0:
        return pd.DataFrame()
    deg = dict(G.degree())
    wdeg = dict(G.degree(weight="weight"))
    try:
        btw = nx.betweenness_centrality(G, weight=None, k=min(500, G.number_of_nodes()),
                                        seed=7)
    except Exception:
        btw = {n: float("nan") for n in G}
    rows = [{"id": n, "label": G.nodes[n].get("label", n),
             "documents": G.nodes[n].get("docs", 0),
             "partners": deg.get(n, 0), "collaboration_links": wdeg.get(n, 0),
             "betweenness": round(btw.get(n, float("nan")), 5)} for n in G]
    df = pd.DataFrame(rows).sort_values("documents", ascending=False).head(top)
    df.to_csv(TAB / f"{stem}.csv", index=False)
    return df


def collaboration_shares(records, label):
    """International, regional and domestic collaboration, counted per work."""
    n = intl = latam_intl = solo_country = 0
    for rec in records:
        c = rec.get("countries_distinct_count")
        if c is None:
            c = len(entities(rec)[0])
        if c == 0:
            continue
        n += 1
        if c > 1:
            intl += 1
            cs = entities(rec)[0]
            if len([x for x in cs if x in LATAM]) > 1:
                latam_intl += 1
        else:
            solo_country += 1
    return {"corpus": label, "works_with_country": n,
            "international_pct": round(intl / n * 100, 1) if n else None,
            "single_country_pct": round(solo_country / n * 100, 1) if n else None,
            "intra_latam_pct": round(latam_intl / n * 100, 1) if n else None}


def lotka(records, label):
    """Lotka's law: the share of authors producing exactly n works."""
    prod = Counter()
    for rec in records:
        for aid in entities(rec)[2]:
            prod[aid] += 1
    dist = Counter(prod.values())
    tot = sum(dist.values())
    rows = [{"works_per_author": k, "authors": v, "share_pct": round(v / tot * 100, 2)}
            for k, v in sorted(dist.items())]
    df = pd.DataFrame(rows)
    # exponent of the fitted power law, on the log-log slope of the first decade
    d = df[df["works_per_author"] <= 10]
    if len(d) > 2:
        x = [math.log10(v) for v in d["works_per_author"]]
        y = [math.log10(v) for v in d["authors"]]
        mx, my = sum(x) / len(x), sum(y) / len(y)
        num = sum((a - mx) * (b - my) for a, b in zip(x, y))
        den = sum((a - mx) ** 2 for a in x)
        slope = num / den if den else float("nan")
    else:
        slope = float("nan")
    df.to_csv(TAB / f"T_lotka_{label}.csv", index=False)
    return {"corpus": label, "authors": tot,
            "single_work_authors_pct": df.iloc[0]["share_pct"] if len(df) else None,
            "lotka_exponent": round(-slope, 2)}


def bradford(records, label, top=40):
    """Bradford zones: the core journals holding the first third of the output."""
    j = Counter()
    for rec in records:
        src = ((rec.get("primary_location") or {}).get("source") or {})
        name = src.get("display_name")
        if name:
            j[name] += 1
    if not j:
        return {"corpus": label}
    df = pd.DataFrame(j.most_common(), columns=["journal", "works"])
    df["cumulative"] = df["works"].cumsum()
    total = df["works"].sum()
    df["cumulative_pct"] = (df["cumulative"] / total * 100).round(1)
    third = total / 3
    zone1 = int((df["cumulative"] < third).sum()) + 1
    df["zone"] = pd.cut(df["cumulative"], [0, third, 2 * third, total],
                        labels=["1 core", "2", "3"], include_lowest=True)
    df.head(top).to_csv(TAB / f"T_bradford_{label}.csv", index=False)
    return {"corpus": label, "journals": len(df), "works_with_journal": int(total),
            "core_zone_journals": zone1,
            "core_zone_pct_of_journals": round(zone1 / len(df) * 100, 2)}


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    corpora = ["methods_world", "core_latam", "core_colombia", "methods_latam"]
    loaded = {c: read(c) for c in corpora}
    for c, r in loaded.items():
        print(f"{c:18s} {len(r)} records")

    # --- collaboration, Lotka, Bradford ---
    pd.DataFrame([collaboration_shares(r, c) for c, r in loaded.items() if r]).to_csv(
        TAB / "T15_collaboration_shares.csv", index=False)
    pd.DataFrame([lotka(r, c) for c, r in loaded.items() if r]).to_csv(
        TAB / "T16_lotka_summary.csv", index=False)
    pd.DataFrame([bradford(r, c) for c, r in loaded.items() if r]).to_csv(
        TAB / "T17_bradford_summary.csv", index=False)

    # --- country co-authorship ---
    for c in ["methods_world", "core_latam"]:
        if not loaded[c]:
            continue
        G = cooccurrence(loaded[c], lambda r: entities(r)[0])
        centrality_table(G, f"T18_country_centrality_{c}")
        write_vosviewer(G, f"country_coauthorship_{c}", top=80)
        print(f"country network {c}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # --- institution co-authorship, regional ---
    for c in ["core_latam", "core_colombia"]:
        if not loaded[c]:
            continue
        G = cooccurrence(loaded[c], lambda r: entities(r)[1], min_weight=2)
        centrality_table(G, f"T19_institution_centrality_{c}", top=50)
        write_vosviewer(G, f"institution_coauthorship_{c}", top=250)
        print(f"institution network {c}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # --- author co-authorship, Colombia ---
    if loaded["core_colombia"]:
        G = cooccurrence(loaded["core_colombia"], lambda r: entities(r)[2], min_weight=2)
        centrality_table(G, "T20_author_centrality_core_colombia", top=50)
        write_vosviewer(G, "author_coauthorship_core_colombia", top=300)
        print(f"author network Colombia: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    print("\ntables:", len(list(TAB.glob('*.csv'))), " maps:", len(list(MAPS.glob('*.txt'))))


if __name__ == "__main__":
    main()
